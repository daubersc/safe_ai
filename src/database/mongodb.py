"""
This module handles the database access.
"""
import copy
from src.util.config import Config
from pymongo import MongoClient

__author__ = __maintainer__ = "Kai Dauberschmidt"
__copyright__ = "Copyright 2021, Kai Dauberschmidt "
__license__ = "GPL"
__version__ = "0.1"
__email__ = "daubersc@fim.uni-passau.de"
__status__ = "Development"

class MongoDBClient:
    """
    The class to handle the DB access. It loads the config and allows duplicate free insertion.
    """

    def __init__(self):
        """
        Loads the config, the concrete db and the collection.
        """

        cfg = Config()
        self.client = MongoClient(cfg.db_url)
        self.db = self.client[cfg.db_name]
        self.collection = cfg.db_collection

    def insert_document(self, document: dict, collection=None):
        """
        Inserts a document into the collection given or the collection specified in config. Silently
        """

        if collection is None:
            collection = self.db[self.collection]
        else:
            collection = self.db[collection]

        # Update the id. MongoDB stores ids in _id as opposed to coco which stores it in id.
        document_cpy = copy.deepcopy(document)
        try:
            document_cpy['_id'] = document_cpy.pop('id')
        except KeyError:
            pass

        collection.insert_one(document_cpy)
