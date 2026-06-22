from flask import Blueprint

task = Blueprint ('catalogs',__name__)
from . import routes # импортируем маршруты из следующего файла