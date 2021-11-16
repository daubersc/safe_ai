# COCO Loader  

This is a small script to load individual images from the [Coco Dataset](https://cocodataset.org/#download)
into an instance of [MongoDB](https://www.mongodb.com/) as part of the Safe AI seminar from 2021, University of
Passau. 

## Prerequisites

Before you can execute the script, make sure you have:

- At least 30 GB of disk space.
- MongoDB database, either locally or a cluster. 
- Python 3.9+ including its modules:
    - pymongo
    - json
    - pathlib 
    - copy
    - fiftyone.zoo
    - pycocotools.coco

You can install these modules using pip. 

## Setup

Please head to /config/config.json and fill in the config according to the predefined keys and descriptions.

## Run 

In order to run the script use the command `Python3 main.py [-n category_name] [-c collection_name]`. Both 
of these are optional parameters. If you do not set them the script will instead use all categories and store them in 
the default collection from `config.json`. 



