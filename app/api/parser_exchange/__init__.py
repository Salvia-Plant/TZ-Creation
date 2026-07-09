from flask import Blueprint

parser_exchange = Blueprint('parser_exchange', __name__)

from . import routes