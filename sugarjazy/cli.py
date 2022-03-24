#!/usr/bin/env python3
#
# Parse json logs we have from knative to something a bit more readable and
# pareseable to the eyes of a user
import argparse
import datetime
import json
import random
import re
import sys

try:
    import dateutil.parser as dtparse

    dtparseb = "store_true"
except ImportError:
    dtparseb = "store_false"

DEFAULT_TIMEFORMAT = "%H:%M:%S"
CURRENT_EVENT_CHAR = "˃"

KAIL_PREFIX_REGEXP = re.compile(
    r"^(?P<namespace>[^/]*)/(?P<pod>[^\[]*)\[(?P<container>[^\]]*)\]: (?P<line>.*)"
)

# pylint: disable=too-few-public-methods
class bcolors:
    MAGENTA = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"

    @classmethod
    def as_string(cls, s: str) -> str:
        return getattr(cls, s.upper())

    @staticmethod
    def random256() -> str:
        color = random.randint(0o22, 0o231)
        return f"\033[38;5;{color}m"


def jline(line, argp):
    colors = {}
    kail_prefix = ""
    if not line.strip():
        return

    if argp.kail:
        kail_re = KAIL_PREFIX_REGEXP.match(line)
        if kail_re:
            line = kail_re.group("line")
            kail_prefix = argp.kail_prefix_format.format(
                pod=kail_re.group("pod"),
                container=kail_re.group("container"),
                namespace=kail_re.group("namespace"),
            )
    try:
        jeez = json.loads(line)
    except json.decoder.JSONDecodeError:
        if not argp.filter_level:
            print(line)
        return

    getkey = lambda x: jeez.get(x) and x

    key_level = getkey("severity") or getkey("level")
    if argp.filter_level:
        if not key_level:
            return
        if jeez[key_level].lower() not in [
            x.lower() for x in argp.filter_level.split(",")
        ]:
            return
    key_message = getkey("msg") or getkey("message")
    key_event = getkey("event") or getkey("knative.dev/key") or getkey("caller")

    eventcolor = bcolors.ENDC
    chevent = ""
    if not argp.disable_event_colouring and key_event:
        if not jeez[key_event] in colors:
            colors[jeez[key_event]] = bcolors.random256()
        eventcolor = colors[jeez[key_event]]
        chevent = f"{eventcolor}{CURRENT_EVENT_CHAR}{bcolors.ENDC}"
    # highlight string in jeez[km] with a regexp
    if key_message and argp.regexp_highlight:
        jeez[key_message] = re.sub(
            "(" + argp.regexp_highlight + ")",
            bcolors.as_string(argp.regexp_color) + r"\1" + bcolors.ENDC,
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
    if kt and not argp.hide_timestamp:
        if isinstance(jeez[kt], float):
            dt = datetime.datetime.fromtimestamp(jeez[kt])
        else:
            dt = dtparse.parse(jeez[kt])
        dts = f"{bcolors.MAGENTA}{dt.strftime(argp.timeformat)}{bcolors.ENDC} "
    kails = ""
    if argp.kail and kail_prefix and not argp.kail_no_prefix:
        kails = f" {bcolors.BLUE}{kail_prefix: <20}{bcolors.ENDC}"
    print(
        f"{color}{jeez[key_level].upper(): <7}{bcolors.ENDC} {chevent}{kails} {dts}{jeez[key_message]}"
    )


def stream(argp):
    buff = ""
    try:
        while True:
            buff += sys.stdin.read(1)
            if buff.endswith("\n"):
                jline(buff[:-1], argp)
                buff = ""
    except KeyboardInterrupt:
        sys.stdout.flush()


def parse(fp, argp):
    for line in fp.read().split("\n"):
        jline(line, argp)


def args(sysargs: list) -> argparse.Namespace:
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
        "--filter-level", "-F", help="filter levels separated by commas, eg: info,debug"
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
        "--hide-timestamp", "-H", action=dtparseb, help="don't show timestamp"
    )
    parser.add_argument("files", nargs="*", default="")
    return parser.parse_args(sysargs)


def main():
    aargp = args(sys.argv[1:])
    if aargp.kail and aargp.files:
        print("kail mode only work on stream")
        sys.exit(1)
    elif aargp.kail:
        aargp.stream = True
    if aargp.files:
        for f in aargp.files:
            with open(f, encoding="utf-8") as ff:
                parse(ff, aargp)
        sys.exit()
    if aargp.stream:
        stream(aargp)
        sys.exit()

    parse(sys.stdin, aargp)


if __name__ == "__main__":
    main()
