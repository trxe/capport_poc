import pytest
import yaml

from capport.config import TransformParser

SAMPLE_TRANSFORM_YAML = """
---
nhl_player_to_player:
    task: mapping
    mapping:
        person_id: csid
        player_id: playerId
        shoots_catches: shootsCatches
        positions: 
            action: to_list
            args: position

cs_player_ids_to_nhl_landing_urls:
    task: mapping
    mapping: 
        csid: _id
        url:
            template: "https://api-web.nhle.com/v1/player/%s/landing"
            args: id 
"""

SAMPLE_DUPLICATE_YAML = """
---
nhl_player_to_player:
    task: mapping
    mapping:
        person_id: csid
"""

SAMPLE_TRANSFORM_CONFIG = yaml.load(SAMPLE_TRANSFORM_YAML, Loader=yaml.SafeLoader)
SAMPLE_DUPLICATE_CONFIG = yaml.load(SAMPLE_DUPLICATE_YAML, Loader=yaml.SafeLoader)


class TestTransformConfig:
    def test_transform_config_valid(self):
        TransformParser.validate_all([SAMPLE_TRANSFORM_CONFIG])
        TransformParser.parse_all([SAMPLE_TRANSFORM_CONFIG])
        assert set(TransformParser.configs.keys()) == set(SAMPLE_TRANSFORM_CONFIG.keys())

    def test_transform_config_invalid(self):
        with pytest.raises(Exception):
            TransformParser.validate_all([SAMPLE_TRANSFORM_CONFIG, SAMPLE_DUPLICATE_CONFIG])
