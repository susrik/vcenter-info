import functools
import logging

from flask import Blueprint, jsonify, request, \
    Response, render_template, current_app

blueprint = Blueprint("vcenter-info-default-routes", __name__)

logger = logging.getLogger(__name__)


@blueprint.route('/')
def index():
    return render_template('index.html')
