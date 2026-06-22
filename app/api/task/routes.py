from . import task
from .views import TaskList, SingleTask, TaskStatus, TaskRegenerate, Statuses

#для каждого вью класса регистрируем url
task.add_url_rule('/tasks', view_func=TaskList.as_view('tasks'))
task.add_url_rule('/<uuid:task_id>/status', view_func=TaskStatus.as_view('status'))
task.add_url_rule('/statuses', view_func=Statuses.as_view('statuses'))
task.add_url_rule('/<uuid:task_id>/single_task', view_func=SingleTask.as_view('single_task'))
task.add_url_rule('/<uuid:task_id>/regenerate', view_func=TaskRegenerate.as_view('regenerate'))

