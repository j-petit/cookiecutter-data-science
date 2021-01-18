import logging
import pdb
import logging.config
import yaml
import sacred
import pprint
import os
from datetime import datetime
import dotenv
import pandas as pd

from sacred import Experiment
from sacred.observers import MongoObserver

from src.main import main


ex = sacred.Experiment("{{ cookiecutter.repo_name }}")
ex.add_config(yaml.load("config/config.yaml", yaml.SafeLoader))


dotenv.load_dotenv(".env")
URI = "mongodb://{}:{}@172.26.44.33/?authSource=ogb_citation&authMechanism=SCRAM-SHA-1".format(
    os.environ["SACRED_MONGODB_USER"], os.environ["SACRED_MONGODB_PWD"]
)
ex.observers.append(MongoObserver(url=URI, db_name="ogb_citation"))


@ex.command(unobserved=True)
def print_config(_config):
    """ Replaces print_config which is not working with python 3.8 and current packages sacred"""
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(_config)


@ex.config
def config(c_data, c_dataset, c_results, c_model):

    c_data["raw"] = os.path.join(c_data["prefix"], "raw", c_dataset)
    c_data["processed"] = os.path.join(c_data["prefix"], "processed", c_dataset)
    c_data["interim"] = os.path.join(c_data["prefix"], "interim", c_dataset)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    c_results["output_path"] = os.path.join(c_results["prefix"], timestamp)


@ex.config_hook
def hook(config, command_name, logger):

    config.update({"hook": True})

    pd.set_option("display.max_columns", 500)
    pd.set_option("display.max_rows", None)
    pd.options.display.width = 0

    os.makedirs(config["c_results"]["output_path"], exist_ok=True)
    os.makedirs(config["c_data"]["processed"], exist_ok=True)
    os.makedirs(config["c_data"]["interim"], exist_ok=True)

    log_config = yaml.load(open("config/logging.yaml", "r"), yaml.SafeLoader)

    for handler in log_config["handlers"].values():
        if "filename" in handler.keys():
            handler["filename"] = os.path.join(
                config["c_results"]["output_path"], handler["filename"]
            )

    logging.config.dictConfig(log_config)

    return config


@ex.automain
def run(hook, _config, c_stages, c_results, _run):

    logger = logging.getLogger(
        "{{ cookiecutter.repo_name }}." + os.path.basename(os.path.splitext(__file__)[0])
    )
    logger.info(_config["timestamp"])

    if c_stages["main"]:
        main(_config)

    ex.add_artifact(os.path.join(c_results["output_path"], "general.log"))
