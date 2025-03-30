from abc import ABC, abstractmethod


class ConfigParser(ABC):
    @abstractmethod
    @classmethod
    def parse_all(cls, config_list: list):
        pass

    @abstractmethod
    @classmethod
    def parse(cls, config: any):
        pass
