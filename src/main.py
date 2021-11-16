"""
Automatically loads the COCO dataset into a mongoDB instance.
"""

import getopt
import os
import sys
import pymongo.errors
from pycocotools.coco import COCO
from src.util.downloader import DatasetDownloader
from src.database.mongodb import MongoDBClient
from src.util.printer import Printer

__author__ = __maintainer__ = "Kai Dauberschmidt"
__copyright__ = "Copyright 2021, Kai Dauberschmidt "
__license__ = "GPL"
__version__ = "0.1"
__email__ = "daubersc@fim.uni-passau.de"
__status__ = "Development"


class Loader:
    """
    This class loads the dataset on init, discovers the dataset's json files and adds each data entry to mongoDB
    """

    def __init__(self):
        self.data_dl = DatasetDownloader()
        self.data_files = self._discover_files()
        self.db_client = MongoDBClient()
        self.coco_cats = self._get_coco_cats()

    def _discover_files(self):
        """ Traverses the directory of the downloaded dataset and adds all .json paths to a list. """

        paths = []
        for root, dirs, files in os.walk(self.data_dl.path):
            for file in files:
                if file.endswith(".json"):
                    paths.append(os.path.join(root, file))

        return paths

    def _get_coco_cats(self):
        """ Returns a list of coco categories as strings. """

        # find the instances_train file because this contains certainly all categories using list comprehension.
        instance_file = [file for file in self.data_files if 'instances_train' in file][0]

        coco = COCO(instance_file)
        cats = coco.loadCats(coco.getCatIds())
        return [cat['name'] for cat in cats]

    def fill_db(self, cat: str = None, collection: str = None):
        """
        Extracts the images from the coco data files and stores them individually into the database duplicate free.

        :param cat: The optional coco image category. If None is given, all categories will be chosen.
        :type cat: str
        :param collection: The optional collection, i.e. 'table' name. If none is given, the config name will be used.
        :type collection: str
        """

        cat_names = []
        global_counter = 0

        # Check if a coco coco category is given. If it is, just use this category.
        if cat is not None:
            if cat in self.coco_cats:
                cat_names.append(cat)
            else:
                Printer.error("No such COCO category.")
                sys.exit(-1)

        # Else use all categories
        else:
            cat_names = self.coco_cats

        # wrap in a list in order to process each cat individually.
        cat_wrapper = _wrap(cat_names)

        for file in self.data_files:
            counter = 0
            coco = COCO(file)

            for cat in cat_wrapper:

                # Get the image data for each file -  continue with the next file if it has none.
                try:
                    cat_ids = coco.getCatIds(catNms=cat)
                    img_ids = coco.getImgIds(catIds=cat_ids)
                    images = coco.loadImgs(ids=img_ids)
                except KeyError:
                    continue

                # Insert the images into the db
                for img in images:
                    try:
                        self.db_client.insert_document(document=img, collection=collection)
                        global_counter += 1
                        counter += 1
                    except pymongo.errors.DuplicateKeyError:
                        continue
            Printer.info(f"Added {counter} images from {file}.")
        Printer.success(f"Successfully added {global_counter} images to the database.")


def _wrap(names: list):
    """ Wraps the list of names in another list and returns it. """
    wrapper = []

    for name in names:
        wrapper.append([name])

    return wrapper


def main(argv):
    """
    The main function. Parses the command line arguments and proceeds with the action.

    :param argv: The arguments list.
    :type argv: list
    """

    try:
        opts, args = getopt.getopt(argv, "hn:c:", ["help", "cat_name", "collection"])
    except getopt.GetoptError:
        Printer.error("Unknown command line arguments")
        sys.exit(-1)

    cat_name = None
    collection = None

    # Handle the command line arguments.
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            help_me()
            sys.exit(0)
        elif opt in ("-n", "--cat_name"):
            cat_name = arg
        elif opt in ("-c", "--collection"):
            collection = arg

    Printer.info(f"Starting the procedure.")
    loader = Loader()
    loader.fill_db(cat_name, collection)
    Printer.info(f"Finished the procedure.")


def help_me():
    Printer.info(
        "Before you start, make sure you have everything set in ./config/config.json.\n"
        "You can set a specific category name using the '-n' or '--cat_name' operator.\n"
        "You can set a specific collection name using the '-c' or '--collection' operator."
    )


if __name__ == "__main__":
    main(sys.argv[1:])
