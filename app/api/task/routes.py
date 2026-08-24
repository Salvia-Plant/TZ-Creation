from . import task
from .views import TaskList, SingleTask, TaskStatus, TaskRegenerate, Statuses,TaskUpdate, AdmittedPeople

#для каждого вью класса регистрируем url
task.add_url_rule('/task_list', view_func=TaskList.as_view('task_list'))
task.add_url_rule('/<uuid:task_id>/status', view_func=TaskStatus.as_view('status'))
task.add_url_rule('/<uuid:task_id>/task_update', view_func=TaskUpdate.as_view('task_update'))
task.add_url_rule('/statuses', view_func=Statuses.as_view('statuses'))
task.add_url_rule('/<uuid:task_id>/single_task', view_func=SingleTask.as_view('single_task'))
task.add_url_rule('/<uuid:task_id>/regenerate', view_func=TaskRegenerate.as_view('regenerate'))
task.add_url_rule('/<uuid:task_id>/people', view_func=AdmittedPeople.as_view('admitted_people'))
task.add_url_rule('/<uuid:task_id>/autogenerate', view_func=AdmittedPeople.as_view('autogenerate'))

