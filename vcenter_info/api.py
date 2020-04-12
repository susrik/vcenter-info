import functools
import json
import logging
import os
import pkg_resources
import time

from flask import Blueprint, jsonify, request, Response, current_app

from vcenter_info import vcenter

blueprint = Blueprint("vcenter-info-api-routes", __name__)

API_VERSION = '0.1'
RESPONSE_TIMEOUT_SEC = 2.0
logger = logging.getLogger(__name__)


def require_accepts_json(f):
    """
    used as a route handler decorator to return an error
    unless the request allows responses with type "application/json"
    :param f: the function to be decorated
    :return: the decorated function
    """
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        # TODO: use best_match to disallow */* ...?
        if not request.accept_mimetypes.accept_json:
            return Response(
                response="response will be json",
                status=406,
                mimetype="text/html")
        return f(*args, **kwargs)
    return decorated_function


@blueprint.route("/version", methods=['GET', 'POST'])
@require_accepts_json
def version():
    version_params = {
        'api': API_VERSION,
        'module': pkg_resources.get_distribution('vcenter_info').version
    }
    return jsonify(version_params)


def load_cached_vms(params):
    if params['expiration_seconds'] > 0 \
            and os.path.isfile(params['filename']):
        stat = os.stat(params['filename'])
        if time.time() - stat.st_mtime < params['expiration_seconds']:
            with open(params['filename']) as f:
                try:
                    return json.loads(f.read())
                except json.JSONDecodeError:
                    logger.exception(f'error parsing {params["filename"]}')

    return None


@blueprint.route("/vms", methods=['GET', 'POST'])
@require_accepts_json
def vms():

    refresh = request.args.get('refresh', default=False, type=bool)

    logger.debug('getting vms')

    config = current_app.config['CONFIG_PARAMS']

    vm_list = None if refresh else load_cached_vms(config['cache'])
    if not vm_list:
        vm_list = list(vcenter.get_vms(config['auth']))
        with open(config['cache']['filename'], 'w') as f:
            f.write(json.dumps(vm_list))

    return jsonify(vm_list)
