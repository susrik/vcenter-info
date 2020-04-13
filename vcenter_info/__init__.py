"""
automatically invoked app factory
"""
import logging
import os

from flask import Flask

from vcenter_info import config

logger = logging.getLogger(__name__)
CONFIG_ENV_VAR_NAME = 'CONFIG_FILENAME'


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
        config_params = config.parse_config_and_add_defaults(f.read())

    app = Flask(__name__)
    app.secret_key = 'super secret session key'
    app.config['CONFIG_PARAMS'] = config_params

    from vcenter_info import api
    app.register_blueprint(api.blueprint, url_prefix='/api')

    from vcenter_info import default
    app.register_blueprint(default.blueprint, url_prefix='/')

    logger.info('vcenter_info Flask app initialized')

    return app
