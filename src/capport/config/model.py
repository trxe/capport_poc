from dataclasses import dataclass

from capport.config.common import ConfigParser


@dataclass
class ModelFieldConfig:
    dtype: str
    constraints: list[str] | None = None


class ModelConfig:
    name: str
    schema: dict[str, str | ModelFieldConfig]

    def __init__(self, name: str, raw_config: dict):
        self.name = name
        self.schema = {
            key: (conf if isinstance(conf, str) else ModelFieldConfig(**conf)) for key, conf in raw_config.items()
        }


class ModelParser(ConfigParser):
    configs: dict[str, ModelConfig]

    @classmethod
    def validate_all(cls, config_pages: list[dict[str, dict]]):
        all_models = [configs for page in config_pages for configs in page.items()]
        cls.assert_no_duplicates([x for x, _ in all_models])

    @classmethod
    def parse_all(cls, config_pages: list[dict[str, dict]]):
        cls.configs = {name: ModelConfig(name, config) for page in config_pages for name, config in page.items()}

    @classmethod
    def get_config(cls, config_key: str) -> ModelConfig:
        if config_key not in cls.configs:
            raise Exception(
                f"Model not initialized: {config_key}, not found "
                f"amongst initialized configs: {list(cls.configs.keys())}"
            )
        return cls.configs[config_key]
