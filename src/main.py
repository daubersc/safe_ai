"""
Automatically loads the COCO dataset into a mongoDB instance.
"""

import getopt
import json
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
        self.data_paths = self._discover_files()
        self.db_client = MongoDBClient()

    def _discover_files(self):
        """ Traverses the directory of the downloaded dataset and adds all .json paths to a list. """

        paths = []
        for root, dirs, files in os.walk(self.data_dl.path):
            for file in files:
                if file.endswith(".json"):
                    paths.append(os.path.join(root, file))

        return paths

    def fill_db(self, cat: str = None):
        """
        Extracts the images from the coco data files and stores them individually into the database duplicate free.

        :param cat: The optional coco image category. If None is given, all categories will be chosen.
        :type cat: str
        :param collection: The optional collection, i.e. 'table' name. If none is given, the config name will be used.
        :type collection: str
        """


        # Basic population:
        if cat is None:
            for path in self.data_paths:

                Printer.info(f"loading file {path}")
                json_file = json.load(open(path))

                # Basic Population of DB.
                try:
                    image_list = self._bulk_insert(json_file['images'], 'all_images')
                    cat_list = self._bulk_insert(json_file['categories'], 'categories')
                    annotations_list = self._bulk_insert(json_file['annotations'], 'annotations')
                except KeyError:
                    continue
        else:
            collection_name = cat.replace(" ", "_")
            counter = 0

            # Get the category as JSON object and find the id.
            collection = self.db_client.db['categories']
            cat_object = collection.find_one({"name": cat})
            cat_id = cat_object['_id']

            # Get a cursor to annotations with the given category.
            collection = self.db_client.db['annotations']
            cursor = collection.find({"category_id": cat_id})

            # Get the collection of images.
            collection = self.db_client.db['all_images']

            for annotation in cursor:
                # Get the image id.
                img_id = annotation['image_id']

                # Find the concrete image.
                image = collection.find_one({"_id": img_id})

                # insert it into a new collection
                try:
                    self.db_client.insert_document(image, collection_name)
                    counter += 1
                except pymongo.errors.DuplicateKeyError:
                    continue

            Printer.success(f"Inserted {counter} images into {collection_name}.")

    def _bulk_insert(self, data: list, collection):
        """ Bulk inserts documents while skipping duplicates. """
        counter = 0

        for item in data:
            try:
                self.db_client.insert_document(item, collection)
                counter += 1
            except pymongo.errors.DuplicateKeyError:
                continue

        print(f"Inserted {counter} JSON objects into {collection}.")
        return data

def main(argv):
    """
    The main function. Parses the command line arguments and proceeds with the action.

    :param argv: The arguments list.
    :type argv: list
    """

    try:
        opts, args = getopt.getopt(argv, "hv:c:", ["help", "verbose", "category"])
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

        elif opt in ("-v", "--verbose"):
            cp = Comparator()
            cp.find(arg)

        elif opt in ("-n", "--category"):
            ldr = Loader()
            ldr.fill_db(arg)

        else:
            ldr = Loader()
            ldr.fill_db()

def help_me():
    Printer.info(
        "Before you start, make sure you have everything set in ./config/config.json."
        "Filling the database will be done by two ways:\n"
        "- Generating ALL data (required for the first time!) using no command line arguments.\n"
        "- Generating specific category data using the -c or --category optional argument.\n\n"
        "If you have your DB already setup you can use the -v or --verbose to get the biggest and the smallest image."
    )


class Comparator:
    """
    Find the biggest and smallest picture of the dataset in MongoDB.
    """

    def __init__(self):
        self.db_client = MongoDBClient()
        self.MAX = 0
        self.max_doc = None
        self.MIN = (2 ** 31) - 1  # max int value
        self.min_doc = None

    def find(self, collection):
        """
        Findds the biggest and smalles picture of the dataset in MongoDB.

        :param collection: The collection to search.
        """

        collection = self.db_client.db[collection]
        cursor = collection.find()

        for image in cursor:

            height = image.get("height")
            width = image.get("width")

            # Make sure both height and width exist and are integers.
            assert isinstance(height, int) and isinstance(width, int)

            dimension = height * width

            if dimension < self.MIN:
                self.MIN = dimension
                self.min_doc = image
            elif dimension > self.MAX:
                self.MAX = dimension
                self.max_doc = image

        Printer.info(f"biggest image is {self.max_doc} with {self.MAX} pixels.")
        Printer.info(f"smallest image is {self.min_doc} with {self.MIN} pixels.")

# replace with main function and argv.
if __name__ == "__main__":
    cp = Loader()
    cp.fill_db(cat="traffic light")
