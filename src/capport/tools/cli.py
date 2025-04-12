import argparse
import os
from fnmatch import fnmatch
from pathlib import Path
from typing import Any

import yaml

import capport.config.common as cfg_common
from capport.config import ModelParser, PipelineParser, TransformParser


class ConfigPack:
    CONFIG_FILE_EXTS = ["*.yml", "*.yaml"]
    CONFIG_PARSER: dict[str, cfg_common.ConfigParser] = {
        "model": ModelParser,
        "transform": TransformParser,
        "services": None,  # clients/client-wrappers to access services
        "pipeline": PipelineParser,
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
                    # each file's node is a separate config entry,
                    self.collated_configs.get(key).append(subconfig)
        self.parse_all("model")
        self.parse_all("transform")
        self.parse_all("pipeline")

    @classmethod
    def _get_config_component(cls, config_key: str) -> None:
        if config_key not in cls.CONFIG_PARSER:
            raise Exception(f"{config_key} not a valid configurable")
        if not cls.CONFIG_PARSER.get(config_key):
            raise Exception(f"{config_key}'s parser isn't implemented/recognised by ConfigPack yet")
        return cls.CONFIG_PARSER.get(config_key)

    def parse_all(self, config_key: str) -> None:
        parser = self._get_config_component(config_key)
        config_pages = self.collated_configs.get(config_key)
        if not config_pages:
            return
        parser.validate_all(config_pages)
        parser.parse_all(config_pages)

    def get_config(self, config_key: str, config_name: str) -> Any:
        parser = self._get_config_component(config_key)
        return parser.get_config(config_name)


def get_cli_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="CapPort (POC)",
        description="Configurable data aggregator",
    )
    parser.add_argument("-c", "--config_dir", required=True)
    parser.add_argument("-o", "--output_dir")
    parser.add_argument("-dt", "--datetime", type=str)
    parser.add_argument("-p", "--pipeline", required=True)
    parser.add_argument("-i", "--interactive", default=True)
    return parser
