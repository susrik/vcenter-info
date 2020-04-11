import logging
from flask import Blueprint, render_template\

blueprint = Blueprint("vcenter-info-default-routes", __name__)
logger = logging.getLogger(__name__)


@blueprint.route('/')
def index():
    return render_template('index.html')
