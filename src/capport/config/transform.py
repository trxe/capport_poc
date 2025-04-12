"""
TransformRegistry:

Configurations for the transform template_tasks.

Inside ./transforms/* there should only be one `mapping` method.
`mapping` infact actually takes in the mapping config from the
transforms config file and creates mapping functions, named by their keys,
that the PipelineRegistry can lookup.

see transform.yml for features required.
"""

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
