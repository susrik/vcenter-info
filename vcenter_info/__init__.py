"""
automatically invoked app factory
"""
import copy
import json
import logging
import os

from flask import Flask
import jsonschema

logger = logging.getLogger(__name__)
CONFIG_ENV_VAR_NAME = 'CONFIG_FILENAME'

CONFIG_DEFAULT_PORT = 443
CONFIG_DEFAULT_CACHE_PARAMS = {
    'filename': '/tmp/cached-vms.json',
    'expiration_seconds': 86400
}

CONFIG_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",

    "definitions": {
        "cache": {
            "type": "object",
            "properties": {
                "filename": {"type": "string"},
                "expiration_seconds": {
                    "type": "number",
                    "minimum": 0
                },
            },
            "additionalProperties": False
        },
        "datacenter": {
            "type": "object",
            "properties": {
                "hostname": {"type": "string"},
                "port": {"type": "integer"},
                "username": {"type": "string"},
                "password": {"type": "string"}
            },
            "required": ["hostname", "username", "password"],
            "additionalProperties": False
        }
    },

    "type": "object",
    "properties": {
        "cache": {"$ref": "#/definitions/cache"},
        "auth": {
            "type": "array",
            "minItems": 1,
            "items": {"$ref": "#/definitions/datacenter"}
        }
    },
    "required": ["auth"],
    "additionalProperties": False
}


def _parse_config_and_add_defaults(s):
    config = json.loads(s)
    jsonschema.validate(config, CONFIG_SCHEMA)
    for dc in config['auth']:
        dc.setdefault('port', CONFIG_DEFAULT_PORT)
    input_cache = config.get('cache', {})
    config['cache'] = copy.copy(CONFIG_DEFAULT_CACHE_PARAMS)
    config['cache'].update(input_cache)

    if config['cache']['expiration_seconds'] > 0:
        # verify cache file is writeable & is parseable if exists
        already_exists = os.path.exists(config['cache']['filename'])
        with open(config['cache']['filename'], 'a') as f:
            pass
        if not already_exists:
            os.unlink(config['cache']['filename'])
        else:
            with open(config['cache']['filename'], 'r') as f:
                json.loads(f.read())

    return config


def create_app():
    """
    :return: a new flask app instance
    """

    assert CONFIG_ENV_VAR_NAME in os.environ, \
        'expected {} to be defined in the environment'.format(
            CONFIG_ENV_VAR_NAME)
    config_filename = os.environ[CONFIG_ENV_VAR_NAME]
    assert os.path.isfile(config_filename), \
        'config file {} not found'.format(config_filename)

    with open(config_filename) as f:
        config = _parse_config_and_add_defaults(f.read())

    app = Flask(__name__)
    app.secret_key = 'super secret session key'
    app.config['CONFIG_PARAMS'] = config

    from vcenter_info import api
    app.register_blueprint(api.blueprint, url_prefix='/api')

    from vcenter_info import default
    app.register_blueprint(default.blueprint, url_prefix='/')

    logger.info('vcenter_info Flask app initialized')

    return app
