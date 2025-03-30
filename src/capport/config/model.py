from enum import Enum

from common import ConfigParser


# TODO: complete
class ModelType(Enum):
    INT64 = "int64"
    FLOAT = "float"
    STRING = "string"
    VARCHAR = "varchar"


class ModelConstraintType(Enum):
    UNIQUE = "unique"
    FOREIGN = "foreign"
    CHECK = "check"
    EXCLUDE = "exclude"
    INVALID = "invalid"


class ModelConstraint:
    def __init__(self, config: any):
        if isinstance(config, str):
            self.type = ModelConstraintType.get(config, ModelConstraintType.INVALID)
        else:
            self.config = config


class ModelMapping:
    def __init__(self, model_name: str, config: dict[str, str | dict]):
        self.model_name = model_name


class ModelTable(ConfigParser):
    @classmethod
    def parse(cls, config: list[tuple[str, dict]]):
        cls.models = {
            model_name: ModelMapping(model_name, model_desc)
            for model_name, model_desc in config.items()
        }

    def validate_configs(cls, config: list[tuple[str, dict]]):
        seen = set()
        for name, _ in config:
            assert name not in seen, f"{name} found with 2 configs"

    @classmethod
    def parse_all(cls, config_list: list[any]):
        model_list = [(name, desc) for c in config_list for name, desc in c]
        cls.validate_configs(model_list)
        cls.parse(model_list)
