from abc import ABC, abstractmethod


class ConfigParser(ABC):
    """Interface for all parsers."""

    @classmethod
    @abstractmethod
    def validate_all(cls, config_pages: list):
        """
        Validates the combined config_list
        """

    @classmethod
    @abstractmethod
    def parse_all(cls, config_pages: list):
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
    def validate(cls, config_id: str):
        """
        Validates the individual config
        """

    @classmethod
    @abstractmethod
    def parse(cls, config_id: str):
        """
        parses and returns the indiv config.
        additional config validation can take place.
        """

    @classmethod
    def assert_no_duplicates(cls, structure: list | dict):
        existing = set()
        duplicates = []
        for item in structure:
            if item in existing:
                duplicates.append(item)
            existing.add(item)
        assert not duplicates, f"Duplicate keys found: {duplicates}"
