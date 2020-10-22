import os
import glob
import logging
import sys
import yaml


def get_dataset(config):
    """Downloads the dataset if it is not yet available and unzips it"""

    datasets = {
        "CVE-2014-0160": "https://www.exploids.de/lid-ds-downloads/LID-DS-Recordings-01/CVE-2014-0160.tar.gz",
    }

    try:
        link = datasets[config["dataset"]]
    except KeyError as key:
        print("This dataset does not exist. Aborting.")
        print(f"The key was {key}")
        sys.exit(1)

    raw_data = os.path.join(config["data"]["prefix"], "raw")

    datapath = "{}/{}.tar.gz".format(raw_data, config["dataset"])

    print(datapath)

    if not os.path.exists(datapath):
        os.system(f"curl -LOJ {link}")
        os.system(f"mv {config['dataset']}.tar.gz {datapath}")
        os.system(f"tar -zxvf {datapath} -C {raw_data}")
        os.system(f"rm {datapath}")
