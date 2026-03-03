from flask import Flask, abort
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from sqlalchemy.exc import OperationalError

from dotenv import load_dotenv
load_dotenv()
from .config import AppConfig
config = AppConfig() 

app = Flask(__name__)
app.config.from_object(config) # применение настроек
db = SQLAlchemy(app) 
migrate = Migrate(app, db)
ma = Marshmallow(app)
from . import api

# Проверка соединения с бд
@app.before_request
def check_db_connection():
   try:
     db.engine.connect()
   except OperationalError as exc_info:
     app.logger.error('Heт соединения с базой данныx. {}.'.format(exc_info))
     abort (500)

@app.errorhandler(500)
def internal_server_error(e):
   return dict(message='внутренняя ошибка сервера'), e.code