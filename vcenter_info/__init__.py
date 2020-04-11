"""
automatically invoked app factory
"""
import json
import logging
import os

from flask import Flask
import jsonschema

logger = logging.getLogger(__name__)
CONFIG_ENV_VAR_NAME = 'CONFIG_FILENAME'

CONFIG_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",

    "definitions": {
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

    "type": "array",
    "items": {"$ref": "#/definitions/datacenter"}
}


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
        config = json.loads(f.read())
        jsonschema.validate(config, CONFIG_SCHEMA)

    app = Flask(__name__)
    app.secret_key = 'super secret session key'
    app.config['VCENTER_PARAMS'] = config

    from vcenter_info import api
    app.register_blueprint(api.blueprint, url_prefix='/api')

    from vcenter_info import default
    app.register_blueprint(default.blueprint, url_prefix='/')

    logger.info('vcenter_info Flask app initialized')

    return app
