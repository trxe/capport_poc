from abc import ABC, abstractmethod


class ConfigParser(ABC):
    """Interface for all parsers."""

    @classmethod
    @abstractmethod
    def parse_all(cls, config_list: list):
        """
        The config scraper finds all the configs in a directory under the config type
        (model, service, source, transform, pipeline) and combines them into a list
        separated by the original file it was in.
        You validate everything in this method, before handing off each config into `parse`.

        Places the keyed map of configs for this config type into a Registry.
        The Registry will be queried to pull the correct components for usage.
        """

    @classmethod
    @abstractmethod
    def parse(cls, config: any):
        """
        parses and returns the config.
        additional config validation can take place.
        """
