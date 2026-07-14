from flask import Blueprint

catalogs = Blueprint ('catalogs',__name__)

from . import routes