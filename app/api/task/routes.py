from . import task
from .views import TaskOne, TaskStatus

#для каждого вью класса регистрируем url
task.add_url_rule('/first', view_func=TaskOne.as_view('first'))
task.add_url_rule('/first', view_func=TaskStatus.as_view('status'))
