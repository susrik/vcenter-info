import functools
import logging

from flask import Blueprint, jsonify, request, \
    Response, render_template, current_app

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
        'module': None
        # 'module': pkg_resources.get_distribution('vcenter_info').version
    }
    return jsonify(version_params)


@blueprint.route("/vms", methods=['GET', 'POST'])
@require_accepts_json
def vms():
    logger.debug('getting vms')
    config = current_app.config['VCENTER_PARAMS']

    # dc_names = [dc['hostname'] for dc in config]
    # def _dummy_vm(id):
    #     return {
    #         'datacenter': dc_names[id % len(dc_names)].upper(),
    #         'name': f'vm \'{id}\' name',
    #         'annotation': f'vm \'{id}\' annotation',
    #         'state': f'vm \'{id}\' state'
    #     }
    # return jsonify([_dummy_vm(x) for x in range(10)])

    vms = vcenter.get_vms(current_app.config['VCENTER_PARAMS'])
    return jsonify(list(vms))
