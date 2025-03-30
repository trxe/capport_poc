from abc import ABC, abstractmethod


class ConfigParser(ABC):
    @abstractmethod
    def parse_all(cls, config_list: list):
        pass

    @abstractmethod
    def parse(cls, config: any):
        pass
