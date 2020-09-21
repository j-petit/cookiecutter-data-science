import os
from datetime import datetime
import pprint
import glob
import logging
from pprint import pformat
import sys
import yaml

from src.utils import load_config

def get_dataset(args):
    """Downloads the dataset if it is not yet available and unzips it

    Parameters
    ----------
    args : dict
    """

    datasets = {
        "Name": "link",
    }

    config = load_config(args.config)


def preprocess(args):
    """Preprocesses the dataset into an intermediate format

    Parameters
    ----------
    args : dict
    """

    config = load_config(args.config)
