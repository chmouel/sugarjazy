import argparse
import datetime
import json
import re
import sys
import typing

from .colors import bcolors

DEFAULT_TIMEFORMAT = "%H:%M:%S"
CURRENT_EVENT_CHAR = "˃"

KAIL_PREFIX_REGEXP = re.compile(
    r"^(?P<namespace>[^/]*)/(?P<pod>[^\[]*)\[(?P<container>[^]]*)]: (?P<line>.*)"
)

DTPARSEB = "store_false"
try:
    import dateutil.parser as dtparse

    DTPARSEB = "store_true"
except ImportError:
    DTPARSEB = "store_false"


class SugarJazyBadArgumentExc(Exception):
    pass


class Sugarjazy:
    sysargs: list
    argp: argparse.Namespace

    def __init__(self, sysargs: typing.Union[None, list]):
        if sysargs is None:
            self.sysargs = sys.argv[1:]
        else:
            self.sysargs = sysargs
        self.make_args()

    def do_fp(self, fp: typing.IO):
        for line in fp.read().split("\n"):
            if line.strip():
                sys.stdout.write(self.parse(line) + "\n")

    def do_stdin(self):
        buff = ""
        try:
            while True:
                buff += sys.stdin.read(1)
                if buff.endswith("\n"):
                    sys.stdout.write(self.parse(buff[:-1]) + "\n")
                    buff = ""
                elif buff == "EOF":
                    break
        except KeyboardInterrupt:
            sys.stdout.flush()

    def make_args(self) -> None:
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--timeformat",
            default=DEFAULT_TIMEFORMAT,
            help='timeformat default only to the hour:minute:second. Use "%%Y-%%m-%%d %%H:%%M:%%S" if you want to add the year',
        )
        parser.add_argument(
            "--regexp-highlight",
            "-r",
            help=r'Highlight a regexp in message, eg: "Failed:\s*\d+, Cancelled\s*\d+"',
        )
        parser.add_argument(
            "--disable-event-colouring",
            action="store_true",
            help=f"By default sugarjazy will try to add a {CURRENT_EVENT_CHAR} char with a color to the eventid to easily identify which event belongs to which. Use this option to disable it.",
        )

        parser.add_argument(
            "--filter-level",
            "-F",
            help="filter levels separated by commas, eg: info,debug",
        )

        parser.add_argument(
            "--stream", "-s", action="store_true", help="wait for input stream"
        )

        parser.add_argument(
            "--kail",
            "-k",
            action="store_true",
            help="assume streaming logs from kail (https://github.com/boz/kail)",
        )
        parser.add_argument(
            "--kail-no-prefix",
            action="store_true",
            help="by default kail will print the prefix unless you specify this flag",
        )
        parser.add_argument(
            "--kail-prefix-format",
            default="{namespace}/{pod}[{container}]",
            help="the template of the kail prefix.",
        )

        parser.add_argument(
            "--regexp-color", default="CYAN", help=r"Regexp highlight color"
        )
        parser.add_argument(
            "--hide-timestamp", "-H", action=DTPARSEB, help="don't show timestamp"
        )
        parser.add_argument("files", nargs="*", default="")
        self.argp = parser.parse_args(self.sysargs)

        if self.argp.kail and self.argp.files:
            raise SugarJazyBadArgumentExc("kail mode only work on stream")
        if self.argp.kail:
            self.argp.stream = True

    def main(self):
        if self.argp.files:
            for f in self.argp.files:
                with open(f, encoding="utf-8") as ff:
                    self.do_fp(ff)
            return

        if self.argp.stream:
            self.do_stdin()
            return

        self.do_fp(sys.stdin)

    # pylint: disable=too-many-return-statements
    def parse(self, line: str) -> str:
        colors = {}
        kail_prefix = ""
        if not line.strip():
            return ""

        if self.argp.kail:
            kail_re = KAIL_PREFIX_REGEXP.match(line)
            if kail_re:
                line = kail_re.group("line")
                kail_prefix = self.argp.kail_prefix_format.format(
                    pod=kail_re.group("pod"),
                    container=kail_re.group("container"),
                    namespace=kail_re.group("namespace"),
                )
        try:
            jeez = json.loads(line)
        except json.decoder.JSONDecodeError:
            if not self.argp.filter_level:
                return line
            return ""

        getkey = lambda x: jeez.get(x) and x
        key_level = getkey("severity") or getkey("level")
        if not key_level:
            if not self.argp.filter_level:
                return line
            return ""

        if self.argp.filter_level:
            if not key_level:
                return ""
            if jeez[key_level].lower() not in [
                x.lower() for x in self.argp.filter_level.split(",")
            ]:
                return ""
        key_message = getkey("msg") or getkey("message")
        key_event = getkey("event") or getkey("knative.dev/key") or getkey("caller")
        chevent = ""

        if not key_message:
            return ""

        if not self.argp.disable_event_colouring and key_event:
            if not jeez[key_event] in colors:
                colors[jeez[key_event]] = bcolors.random256()
            eventcolor = colors[jeez[key_event]]
            chevent = f"{eventcolor}{CURRENT_EVENT_CHAR}{bcolors.ENDC}"
        # highlight string in jeez[km] with a regexp
        if key_message and self.argp.regexp_highlight:
            jeez[key_message] = re.sub(
                "(" + self.argp.regexp_highlight + ")",
                bcolors.as_string(self.argp.regexp_color) + r"\1" + bcolors.ENDC,
                jeez[key_message],
            )

        kt = getkey("ts") or getkey("timeformat") or getkey("timestamp")
        if key_level and jeez[key_level].lower() == "info":
            color = bcolors.GREEN
        elif key_level and (
            jeez[key_level].lower() == "warning" or jeez[key_level].lower() == "warn"
        ):
            color = bcolors.YELLOW
        elif key_level and jeez[key_level].lower() == "error":
            color = bcolors.RED
        else:
            color = bcolors.CYAN

        dts = ""
        if kt and not self.argp.hide_timestamp:
            if isinstance(jeez[kt], float):
                dt = datetime.datetime.fromtimestamp(jeez[kt])
            else:
                dt = dtparse.parse(jeez[kt])
            dts = f"{bcolors.MAGENTA}{dt.strftime(self.argp.timeformat)}{bcolors.ENDC} "
        kails = ""
        if self.argp.kail and kail_prefix and not self.argp.kail_no_prefix:
            kails = f" {bcolors.BLUE}{kail_prefix: <20}{bcolors.ENDC}"
        return f"{color}{jeez[key_level].upper(): <7}{bcolors.ENDC} {chevent}{kails} {dts}{jeez[key_message]}"


def main(sysargs: typing.Union[None, list]):
    SJ = Sugarjazy(sysargs)
    SJ.main()


if __name__ == "__main__":
    main(sys.argv[0:])
