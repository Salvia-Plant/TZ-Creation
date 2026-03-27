from . import task
from .views import TaskOne, TaskStatus, TaskRegenerate

#для каждого вью класса регистрируем url
task.add_url_rule('/first', view_func=TaskOne.as_view('first'))
task.add_url_rule('/<uuid:task_id>/status', view_func=TaskStatus.as_view('status'))
task.add_url_rule('/<uuid:task_id>/regenerate', view_func=TaskRegenerate.as_view('regenerate'))
