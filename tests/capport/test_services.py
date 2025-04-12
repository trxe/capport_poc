import pytest
import yaml

from capport.config import ServiceParser

SAMPLE_SERVICE_YAML = """
---
mongo_csdb: 
    provider: mongo
    args:
        endpoint_env_var: DEV_MONGO
        db: csdb

postgres_nhl_prod: 
    provider: postgres
    args:
        username: test
        password_env_var: POSTGRES_NHL_PROD_PW
        database: nhl

postgres_nhl_dev: 
    provider: postgres
    args:
"""

SAMPLE_DUPLICATE_YAML = """
---
postgres_nhl_dev: 
    provider: postgres
    args:
        username: trxe
        password_env_var: POSTGRES_NHL_TRXE_PW
        database: nhl_dev
"""

SAMPLE_INVALID_YAML = """
---
postgres_nhl_dev: 
    args:
"""

SAMPLE_SERVICE_CONFIG = yaml.load(SAMPLE_SERVICE_YAML, Loader=yaml.SafeLoader)
SAMPLE_DUPLICATE_CONFIG = yaml.load(SAMPLE_DUPLICATE_YAML, Loader=yaml.SafeLoader)
SAMPLE_INVALID_CONFIG = yaml.load(SAMPLE_INVALID_YAML, Loader=yaml.SafeLoader)


class TestServiceConfig:
    def test_transform_config_valid(self):
        ServiceParser.validate_all([SAMPLE_SERVICE_CONFIG])
        ServiceParser.parse_all([SAMPLE_SERVICE_CONFIG])
        assert set(ServiceParser.configs.keys()) == set(SAMPLE_SERVICE_CONFIG.keys())

    def test_transform_config_invalid(self):
        with pytest.raises(Exception):
            ServiceParser.validate_all([SAMPLE_SERVICE_CONFIG, SAMPLE_DUPLICATE_CONFIG])

        with pytest.raises(Exception):
            ServiceParser.validate_all([SAMPLE_INVALID_CONFIG])
            ServiceParser.parse_all([SAMPLE_INVALID_CONFIG])
