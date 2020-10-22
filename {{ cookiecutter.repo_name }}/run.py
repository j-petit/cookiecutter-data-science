import logging
import pdb
import logging.config
import yaml
import sacred
import pprint
import os
from datetime import datetime
import dotenv
import multiprocessing
import pandas as pd
import pathpy

from sacred import Experiment
from sacred.observers import MongoObserver

from src.utils import config_adapt


ex = sacred.Experiment("{{ cookiecutter.repo_name }}")
ex.add_config(yaml.load("config/config.yaml", yaml.SafeLoader))


dotenv.load_dotenv(".env")
URI = "mongodb://{}:{}@139.18.13.64/?authSource=hids&authMechanism=SCRAM-SHA-1".format(
    os.environ["SACRED_MONGODB_USER"], os.environ["SACRED_MONGODB_PWD"]
)
ex.observers.append(MongoObserver(url=URI, db_name="hids"))


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

    c_results["output_path"] = os.path.join(c_results["prefix"], c_dataset, timestamp)


@ex.config_hook
def hook(config, command_name, logger):

    config.update({"hook": True})

    pd.set_option("display.max_columns", 500)
    pd.set_option("display.max_rows", None)
    pd.options.display.width = 0

    os.makedirs(config["c_results"]["output_path"], exist_ok=True)
    os.makedirs(config["c_data"]["processed"], exist_ok=True)
    os.makedirs(config["c_data"]["interim"], exist_ok=True)
    os.makedirs(os.path.dirname(config["c_model"]["save"]), exist_ok=True)

    # logging.config.fileConfig("config/logging_local.conf")
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

    logger = logging.getLogger("{{ cookiecutter.repo_name }}." + os.path.basename(os.path.splitext(__file__)[0]))
    logger.info(_config["timestamp"])

    min_likelihood = None

    if c_stages["pull_data"]:
        src.get_data.get_dataset(_config)
    if c_stages["analyze"]:
        src.ex_analyze_data.analyze(_config)
        ex.add_artifact(os.path.join(c_results["output_path"], "analyze.log"))
    if c_stages["make_temp_paths"]:
        src.preprocess_experiment.preprocess(_config)
        ex.add_artifact(os.path.join(c_results["output_path"], "preprocess.log"))
    if c_stages["create_model"]:
        min_likelihood = src.ex_create_model.create_model(_config, _run)
        ex.add_artifact(os.path.join(c_results["output_path"], "preprocess.log"))
    if c_stages["simulate"]:
        src.run_experiment.my_main(_config, _run, min_likelihood)
        ex.add_artifact(os.path.join(c_results["output_path"], "results.log"))
        ex.add_artifact(os.path.join(c_results["output_path"], "results.csv"))

    ex.add_artifact(os.path.join(c_results["output_path"], "general.log"))
