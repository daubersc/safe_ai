"""
You can use this utility module to load the config of the project in a more or less DTO.
"""
import json
import sys
from json import JSONDecodeError
from pathlib import Path
from src.util.printer import Printer

__author__ = __maintainer__ = "Kai Dauberschmidt"
__copyright__ = "Copyright 2021, Kai Dauberschmidt "
__license__ = "GPL"
__version__ = "0.1"
__email__ = "daubersc@fim.uni-passau.de"
__status__ = "Development"


class Config:

    def __init__(self):
        """ Load the config and save it as class attributes. """

        # Get the path to the config file.
        path = Path(__file__).parents[0].parents[0].parents[0] / 'config' / 'config.json'

        # Read the config.
        try:
            cfg = json.load(open(path))
            self.dataset_name = cfg['coco']['dataset']
            self.dataset_path = cfg['coco']['path']
            self.db_url = cfg['mongodb']['url']
            self.db_name = cfg['mongodb']['db']
            self.db_collection = cfg['mongodb']['collection']

        except FileNotFoundError:
            Printer.error(f"No file {path} found.")
            sys.exit(-1)
        except JSONDecodeError as e:
            Printer.error(f"{e}")
            sys.exit(-1)
        except KeyError as e:
            Printer.error(f"Config file broken: No key {e} found.")
            sys.exit(-1)