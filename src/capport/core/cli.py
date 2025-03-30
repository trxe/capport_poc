import argparse
import datetime as dt
import fnmatch
import os
from pathlib import Path

import config as cfg
import yaml


class ConfigPack:
    CONFIG_FILE_EXTS = ["*.yml", "*.yaml"]
    CONFIG_PARSER: dict[str, cfg.ConfigParser] = {
        "model": cfg.ModelTable,
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
        self.collated_configs = {key: [] for key in self.CONFIG_PARSER.keys()}
        for fp in self.filepaths:
            with open(fp, "r") as file:
                conf = yaml.safe_load(file)
                for key, subconfig in conf:
                    # each parser must handle a list of configs,
                    # i cannot generalise their concatenation
                    self.collated_configs.get(key).append(subconfig)

    def parse(self, config_key: str) -> None:
        if config_key not in self.CONFIG_PARSER:
            raise Exception(f"{config_key} not a valid configurable")
        elif not self.CONFIG_PARSER.get(config_key):
            raise Exception(
                f"{config_key}'s parser isn't implemented/recognised by ConfigPack yet"
            )
        parser = self.CONFIG_PARSER.get(config_key)
        parser.parse_all(self.collated_configs.get(config_key, []))


def cli_args() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="CapPort (POC)",
        description="Combined gateway for data",
    )
    parser.add_argument("-c", "config_dir", required=True)
    parser.add_argument("-o", "output_dir")
    parser.add_argument("-dt", "datetime", type=dt.date | dt.time | dt.datetime)
    return parser
