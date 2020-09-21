import os
from datetime import datetime
import pprint
import glob
import logging
from pprint import pformat

from sacred import Experiment
from sacred.observers import MongoObserver
import dotenv

from src.utils import load_config


project_dir = os.path.join(os.path.dirname(__file__), os.pardir)
dotenv_path = os.path.join(project_dir, ".env")
dotenv.load_dotenv(dotenv_path)

URI = "mongodb://{}:{}@139.18.13.64/?authSource={{cookiecutter.repo_name}}&authMechanism=SCRAM-SHA-1".format(
    os.environ["SACRED_MONGODB_USER"], os.environ["SACRED_MONGODB_PWD"]
)

ex = Experiment("{{cookiecutter.repo_name}}")
ex.observers.append(MongoObserver(url=URI, db_name="{{cookiecutter.repo_name"))
ex.logger = logging.getLogger("{{cookiecutter.repo_name}}")
config = load_config("config/config.yaml")
ex.add_config(config)


@ex.config
def my_config(data, simulate, c_results, seed, dataset):

    if c_results["timestamp"]:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        experiment_name = "{}_{}".format(dataset.upper(), timestamp)
    else:
        experiment_name = "{}".format(dataset.upper())

    c_results["output_path"] = os.path.join(c_results["prefix"], experiment_name)
    os.makedirs(c_results["output_path"], exist_ok=True)

    log_file = os.path.join(c_results["output_path"], "general.log")
    hdlr = logging.FileHandler(log_file, mode="w")
    hdlr.setFormatter(logging.Formatter(fmt="%(asctime)s %(name)-12s %(levelname)-8s %(message)s"))
    ex.logger.addHandler(hdlr)


@ex.command
def print_config(_config, unobserved=True):
    """ Replaces print_config which is not working with python 3.8 and current packages sacred"""
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(_config)


@ex.automain
def my_main(_log, _run, simulate, c_results, timestamp, model, data):

    results_logger = logging.getLogger("results")
    results_logger.addHandler(
        logging.FileHandler(os.path.join(c_results["output_path"], "results.log"), mode="w")
    )

    _log.info("Starting experiment at {}".format(timestamp))

    ex.add_artifact(os.path.join(c_results["output_path"], "results.log"))
