from .task import task
from app import app

app.register_blueprint(task, url_prefix='/TechnicalTaskAPI/task') 
