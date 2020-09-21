import yaml


def load_config(config: str):
    """Custom function to load a config file with additional constructor

    Parameters
    ----------
    config : str
        Path to the config.yaml file

    Returns
    -------
    config : dict
    """

    def join(loader, node):
        seq = loader.construct_sequence(node)
        return "/".join([str(i) for i in seq])

    yaml.add_constructor("!join", join)
    with open(config, "r") as config_file:
        config = yaml.load(config_file, yaml.FullLoader)

    return config
