# pylint: disable=too-few-public-methods
import random


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
