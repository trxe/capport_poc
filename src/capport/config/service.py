from dataclasses import dataclass

from capport.config.common import ConfigParser


@dataclass
class ServiceConfig:
    label: str
    provider: str
    args: dict | None = None


class ServiceParser(ConfigParser):
    configs: dict[str, ServiceConfig]

    @classmethod
    def validate_all(cls, config_pages: list[dict[str, dict]]):
        cls.assert_no_duplicates([label for page in config_pages for label in page.keys()])

    @classmethod
    def parse_all(cls, config_pages: list[dict[str, dict]]):
        cls.configs = {
            name: ServiceConfig(label=name, **config) for page in config_pages for name, config in page.items()
        }

    @classmethod
    def get_config(cls, config_key: str) -> ServiceConfig:
        if config_key not in cls.configs:
            raise Exception(
                f"Service not initialized: {config_key}, not found "
                f"amongst initialized configs: {list(cls.configs.keys())}"
            )
        return cls.configs[config_key]
