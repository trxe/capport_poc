import pytest
import yaml

from capport.config import ModelParser

SAMPLE_MODEL_YAML = """
---
person:
    id:
        dtype: uuid
        constraints: [primary]
    full_name: str
    first_name: str
    last_name: str
    birthdate: date
    deathdate: date
    birth_city: str
    birth_country_code: varchar
    birth_state_province_code: varchar

player:
    person_id:
        dtype: uuid
        constraints: [primary, foreign, indexed]
    nhl_player_id?: # some guys simply don't have id yet
        dtype: int
        constraints: [unique, indexed]
    shoots_catches:
        dtype: varchar
    positions: list[str]
"""

SAMPLE_DUPLICATE_YAML = """
---
player:
    person_id:
        dtype: uuid
        constraints: [primary, foreign, indexed]
"""

SAMPLE_INVALID_YAML = """
---
player:
    person_id:
        constraints: [primary, foreign, indexed]
"""

SAMPLE_MODEL_CONFIG = yaml.load(SAMPLE_MODEL_YAML, Loader=yaml.SafeLoader)
SAMPLE_DUPLICATE_CONFIG = yaml.load(SAMPLE_DUPLICATE_YAML, Loader=yaml.SafeLoader)
SAMPLE_INVALID_CONFIG = yaml.load(SAMPLE_INVALID_YAML, Loader=yaml.SafeLoader)


class TestModelConfig:
    def test_transform_config_valid(self):
        ModelParser.validate_all([SAMPLE_MODEL_CONFIG])
        ModelParser.parse_all([SAMPLE_MODEL_CONFIG])
        assert set(ModelParser.configs.keys()) == set(SAMPLE_MODEL_CONFIG.keys())

    def test_transform_config_invalid(self):
        with pytest.raises(Exception):
            ModelParser.validate_all([SAMPLE_MODEL_CONFIG, SAMPLE_DUPLICATE_CONFIG])

        with pytest.raises(Exception):
            ModelParser.validate_all([SAMPLE_INVALID_CONFIG])
            ModelParser.parse_all([SAMPLE_INVALID_CONFIG])
