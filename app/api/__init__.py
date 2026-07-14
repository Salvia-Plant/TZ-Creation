from .task import task
from .parser_exchange import parser_exchange
from .catalogs import catalogs
from app import app

app.register_blueprint(task, url_prefix='/TZAPI/task') 
app.register_blueprint(catalogs, url_prefix='/TZAPI/catalogs') 
app.register_blueprint(parser_exchange, url_prefix='/TZAPI/parser_exchange') 