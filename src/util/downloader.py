"""
This module is used to handle the download of the coco dataset via fiftyone as suggested by Microsoft.
"""
import sys

__author__ = __maintainer__ = "Kai Dauberschmidt"
__copyright__ = "Copyright 2021, Kai Dauberschmidt "
__license__ = "GPL"
__version__ = "1.0.1"
__email__ = "daubersc@fim.uni-passau.de"
__status__ = "Development"

import os
import shutil

from src.util.printer import Printer
from pathlib import Path
import fiftyone.zoo as foz
from src.util.config import Config


class DatasetDownloader:
    """
     This class is  a utility class to download the dataset via fiftyone and store it in the directory. Both are taken
     from the config file in ./config.
    """

    def __init__(self):

        config = Config()

        # if the directory is specified, use this as path.
        if config.dataset_path:
            self.path = config.dataset_path

        # fiftyone points to a folder in ~/fiftyone/..
        else:
            self.path = Path.home() / "fiftyone" / config.dataset_name
            self.path = str(self.path)

        # Check if enough disk space is available to dl the whole coco 2017 set (which is 26.2 on win)
        free_space = shutil.disk_usage(self.path).free / (1024 ** 3)
        if free_space < 26.2 and config.dataset_name == 'coco-2017':
            Printer.error(
                f"Not enough disk space. The dataset '{config.dataset_name}' requires at least 26.2 GB available space."
                f"You currently only have {free_space} GB available."
            )
            sys.exit(-1)

        # Check if content is empty:
        if not os.listdir(self.path):
            self.data = foz.load_zoo_dataset(name=config.dataset_name, dataset_dir=self.path)
        else:
            Printer.warn(f"directory '{self.path}' is not empty. Skipping download of {config.dataset_name}.")

