from abc import ABC, abstractmethod


class ConfigParser(ABC):
    @classmethod
    @abstractmethod
    def parse_all(cls, config_list: list):
        pass

    @classmethod
    @abstractmethod
    def parse(cls, config: any):
        pass
