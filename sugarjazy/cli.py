#!/usr/bin/env python3
#
# Parse json logs we have from knative to something a bit more readable and
# pareseable to the eyes of a user
import argparse
import datetime
import json
import re
import sys
try:
    import dateutil.parser as dtparse
    dtparseb = "store_true"
except ImportError:
    dtparseb = "store_false"

DEFAULT_TIMEFORMAT = '%H:%M:%S'


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


def parse(fp, argp):
    for i in fp.read().split("\n"):
        if not i.strip():
            continue
        try:
            jeez = json.loads(i)
        except json.decoder.JSONDecodeError:
            print(i)
            continue

        kl = None
        if 'severity' in jeez:
            kl = 'severity'
        elif 'level' in jeez:
            kl = 'level'

        km = None
        if 'msg' in jeez:
            km = 'msg'
        elif 'message' in jeez:
            km = 'message'

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
        elif kl and (jeez[kl].lower() == "warning"
                     or jeez[kl].lower() == "warn"):
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
        print(f"{color}{jeez[kl]: <7}{bcolors.ENDC} {dts}{jeez[km]}")


def args(sysargs: list) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--timeformat",
        default=DEFAULT_TIMEFORMAT,
        help=
        "timeformat default only to the hour minute. Use \"%%Y-%%m-%%d %%H:%%M:%%S\" if you want to add the year"
    )
    parser.add_argument(
        "--regexp-highlight",
        '-r',
        help=
        r"Highlight a regexp in message, for example: \"Failed:\s*\d+, Cancelled\s*\d+\""
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
    if aargp.files:
        for f in aargp.files:
            with open(f, encoding='utf-8') as ff:
                parse(ff, aargp)
        sys.exit()
    parse(sys.stdin, aargp)


if __name__ == '__main__':
    main()
