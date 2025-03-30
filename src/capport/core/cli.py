import argparse
import os
from fnmatch import fnmatch
from pathlib import Path

import yaml

import capport.config.common as cfg_common


class ConfigPack:
    CONFIG_FILE_EXTS = ["*.yml", "*.yaml"]
    CONFIG_PARSER: dict[str, cfg_common.ConfigParser] = {
        "model": None,
        "transform": None,
        "services": None,  # clients/client-wrappers to access services
        "filter": None,
        "pipeline": None,
    }

    def __init__(self, config_dir: str):
        self.dir = config_dir
        self.filepaths = []
        for path, _, files in os.walk(self.dir):
            for name in files:
                for ext in self.CONFIG_FILE_EXTS:
                    if fnmatch(name, ext):
                        self.filepaths.append(Path(path, name))
        self.collated_configs = {key: [] for key in self.CONFIG_PARSER}
        for fp in self.filepaths:
            with open(fp, "r") as file:
                conf = yaml.safe_load(file)
                for key, subconfig in conf.items():
                    # each parser must handle a list of configs,
                    # i cannot generalise their concatenation
                    self.collated_configs.get(key).append(subconfig)

    def parse(self, config_key: str) -> None:
        if config_key not in self.CONFIG_PARSER:
            raise Exception(f"{config_key} not a valid configurable")
        if not self.CONFIG_PARSER.get(config_key):
            raise Exception(f"{config_key}'s parser isn't implemented/recognised by ConfigPack yet")
        parser = self.CONFIG_PARSER.get(config_key)
        parser.parse_all(self.collated_configs.get(config_key, []))


def get_cli_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="CapPort (POC)",
        description="Combined gateway for data",
    )
    parser.add_argument("-c", "--config_dir", required=True)
    parser.add_argument("-o", "--output_dir")
    parser.add_argument("-dt", "--datetime", type=str)
    parser.add_argument("-p", "--pipeline", required=True)
    parser.add_argument("-i", "--interactive", default=True)
    return parser
