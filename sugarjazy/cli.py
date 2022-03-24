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

DEFAULT_TIMEFORMAT = '%H:%M:%S'
CURRENT_EVENT_CHAR = "˃"


# pylint: disable=too-few-public-methods
class bcolors:
    MAGENTA = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    @classmethod
    def as_string(cls, s: str) -> str:
        return getattr(cls, s.upper())

    @staticmethod
    def random256() -> str:
        color = random.randint(0o22, 0o231)
        return f'\033[38;5;{color}m'


def jline(line, argp):
    colors = {}
    prefix = ""
    if not line.strip():
        return

    if argp.kail:
        prefix = line.split(":")[0]
        line = line.replace(prefix, '')[1:].strip()
    try:
        jeez = json.loads(line)
    except json.decoder.JSONDecodeError:
        if not argp.filter_level:
            print(line)
        return

    kl = None
    if 'severity' in jeez:
        kl = 'severity'
    elif 'level' in jeez:
        kl = 'level'

    if argp.filter_level:
        if not kl:
            return
        if jeez[kl].lower() not in [
                x.lower() for x in argp.filter_level.split(",")
        ]:
            return

    km = None
    if 'msg' in jeez:
        km = 'msg'
    elif 'message' in jeez:
        km = 'message'

    keve = None
    if 'event' in jeez:
        keve = 'event'
    elif 'knative.dev/key' in jeez:
        keve = 'knative.dev/key'
    elif 'caller' in jeez:
        keve = 'caller'
    eventcolor = bcolors.ENDC
    chevent = ""
    if not argp.disable_event_colouring and keve:
        if not jeez[keve] in colors:
            colors[jeez[keve]] = bcolors.random256()
        eventcolor = colors[jeez[keve]]
        chevent = f"{eventcolor}{CURRENT_EVENT_CHAR}{bcolors.ENDC}"
    # highlight string in jeez[km] with a regexp
    if km and argp.regexp_highlight:
        jeez[km] = re.sub(
            "(" + argp.regexp_highlight + ")",
            bcolors.as_string(argp.regexp_color) + r'\1' + bcolors.ENDC,
            jeez[km])

    kt = None
    if 'ts' in jeez:
        kt = 'ts'
    elif 'timeformat' in jeez:
        kt = 'timeformat'
    elif 'timestamp' in jeez:
        kt = 'timestamp'

    if kl and jeez[kl].lower() == "info":
        color = bcolors.GREEN
    elif kl and (jeez[kl].lower() == "warning" or jeez[kl].lower() == "warn"):
        color = bcolors.YELLOW
    elif kl and jeez[kl].lower() == "error":
        color = bcolors.RED
    else:
        color = bcolors.CYAN

    dts = ""
    if kt and not argp.hide_timestamp:
        if isinstance(jeez[kt], float):
            dt = datetime.datetime.fromtimestamp(jeez[kt])
        else:
            dt = dtparse.parse(jeez[kt])
        dts = f'{bcolors.MAGENTA}{dt.strftime(argp.timeformat)}{bcolors.ENDC} '
    kails = ''
    if argp.kail and argp.kail_prefix:
        kails = f" {bcolors.BLUE}{prefix: <20}{bcolors.ENDC}"
    print(
        f"{color}{jeez[kl].upper(): <7}{bcolors.ENDC} {chevent}{kails} {dts}{jeez[km]}"
    )


def stream(argp):
    buff = ''
    try:
        while True:
            buff += sys.stdin.read(1)
            if buff.endswith('\n'):
                jline(buff[:-1], argp)
                buff = ''
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
        help=
        "timeformat default only to the hour:minute:second. Use \"%%Y-%%m-%%d %%H:%%M:%%S\" if you want to add the year"
    )
    parser.add_argument(
        "--regexp-highlight",
        '-r',
        help=
        r'Highlight a regexp in message, eg: "Failed:\s*\d+, Cancelled\s*\d+"')
    parser.add_argument(
        "--disable-event-colouring",
        action='store_true',
        help=
        f"By default sugarjazy will try to add a {CURRENT_EVENT_CHAR} char with a color to the eventid to easily identify which event belongs to which. Use this option to disable it."
    )

    parser.add_argument(
        "--filter-level",
        "-F",
        help="filter levels separated by commas, eg: info,debug")

    parser.add_argument("--stream",
                        "-s",
                        action='store_true',
                        help="wait for input stream")

    parser.add_argument(
        "--kail",
        "-k",
        action='store_true',
        help="assume streaming logs from kail (https://github.com/boz/kail)")
    parser.add_argument(
        "--kail-prefix",
        action='store_true',
        help=
        "wether to print the prefix of the pods/container when using the kail mode "
    )
    parser.add_argument("--regexp-color",
                        default='CYAN',
                        help=r"Regexp highlight color")
    parser.add_argument("--hide-timestamp",
                        "-H",
                        action=dtparseb,
                        help="don't show timestamp")
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
            with open(f, encoding='utf-8') as ff:
                parse(ff, aargp)
        sys.exit()
    if aargp.stream:
        stream(aargp)
        sys.exit()

    parse(sys.stdin, aargp)


if __name__ == '__main__':
    main()
