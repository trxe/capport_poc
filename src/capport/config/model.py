"""
ModelRegistry:

ModelRegistry will hold a mapping of model names to their specifications,
in order to make the correct SQL commands to CRUD their tables.
see configs/model.yml for an example.

Roughly, the structure is:
---
model:
    <table_name>:
        <mandatory_table_key>: <type>
        <optional_table_key>?:
            dtype: <type>
            constraints: [<list of constraints>]
---
constraints include (for now):
- primary
- foreign
- unique
- optional (idiom for this is the "?" similar to typescript)
- indexed

there's more complex stuff we can handle later i think for now this is good enough

This will be used by the `sink` template_tasks e.g.

---
    - label: store_cs_player
      use: postgres
      take_from:
        data: cs_player
        model_name: player <--
---
"""

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
