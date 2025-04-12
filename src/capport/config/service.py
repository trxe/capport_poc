"""
ServiceRegistry:

The services should be singletons that are globally accessible. I have some code
that does similar stuff already but it's literally from my work.

for now the service.yml is just an example and i didn't fill out with any
concrete service initialization args, but those args should be parsed and
directly passed into the Service singleton class.

The implementation is more important for the services, please check the
./services/* folder.
"""

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
