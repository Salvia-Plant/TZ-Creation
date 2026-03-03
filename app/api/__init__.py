from .task import task
from app import app

app.register_blueprint(task, url_prefix='/tz-creation/task') 
