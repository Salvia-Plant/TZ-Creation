from flask import Blueprint

task = Blueprint ('task',__name__)
from . import routes # импортируем маршруты из следующего файла