from dataclasses import dataclass

from capport.config.common import ConfigParser


@dataclass
class TransformConfig:
    label: str
    task: str
    mapping: dict[str, str | dict]


class TransformParser(ConfigParser):
    configs: dict[str, TransformConfig]

    @classmethod
    def validate_all(cls, config_pages: list[dict[str, dict]]):
        cls.assert_no_duplicates([label for page in config_pages for label in page.keys()])

    @classmethod
    def parse_all(cls, config_pages: list[dict[str, dict]]):
        cls.configs = {
            name: TransformConfig(label=name, **config) for page in config_pages for name, config in page.items()
        }

    @classmethod
    def get_config(cls, config_key: str) -> TransformConfig:
        if config_key not in cls.configs:
            raise Exception(
                f"Transform not initialized: {config_key}, not found "
                f"amongst initialized configs: {list(cls.configs.keys())}"
            )
        return cls.configs[config_key]
