"""
 The printer module is used to apply various styling to console output to increase readability. It uses standard JS
 colors which can be adjusted below.
"""

__author__ = __maintainer__ = "Kai Dauberschmidt"
__copyright__ = "Copyright 2021, Kai Dauberschmidt "
__license__ = "GPL"
__version__ = "0.1"
__email__ = "daubersc@fim.uni-passau.de"
__status__ = "Development"


class _FontStyle:
    """
    This class is used as an enum for various console style printing. These are default console colors for WebDevs.
    The values are Ascii Escape Codes.
    """

    # error: red
    ERROR = '\033[91m'

    # warn: yellow
    WARNING = '\033[93m'

    # info: cyan
    INFO = '\033[96m'

    # ok / success: green
    SUCCESS = '\033[92m'

    # end styling
    END = '\033[0m'

    # Text Styles: currently unused.
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class Printer:
    """
    This Printer class is used for enhanced console printing, i.e. applying _FontStyles to console prints.
    """

    @staticmethod
    def error(text):
        print(f"{_FontStyle.ERROR}Error: {text}{_FontStyle.END}")

    @staticmethod
    def info(text):
        print(f"{_FontStyle.INFO}Info: {text}{_FontStyle.END}")

    @staticmethod
    def success(text):
        print(f"{_FontStyle.SUCCESS}Success: {text}{_FontStyle.END}")

    @staticmethod
    def warn(text):
        print(f"{_FontStyle.WARNING}Warning: {text}{_FontStyle.END}")
