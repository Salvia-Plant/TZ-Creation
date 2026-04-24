from flask import jsonify, request
from flask.views import MethodView
from marshmallow import ValidationError, EXCLUDE

from app import db
from app.database.models import TechnicalTask
from app.database.schemas import TechnicalTaskInSchema, TechnicalTaskOutSchema, StatusSchema

task_in_schema = TechnicalTaskInSchema()
task_out_schema = TechnicalTaskOutSchema()
tasks_out_schema = TechnicalTaskOutSchema(many=True)
status_schema = StatusSchema() 

def GetCurrentUserID():
    if TechnicalTask.query.get('fed3eGec-673c-49ab-b73e-8d9934bf0d70'):
        return 'fed3eGec-673c-49ab-b73e-8d9934bf0d70'
    else: 
        return None

class TaskList(MethodView):
    model = TechnicalTask 

    def get(self):
        items = self.model.query.filter(self.model.deletion_mark.is_(False)).all()
        result = tasks_out_schema.dump(items)
        return jsonify(result) 
 # базовый пост запрос на создание нового тз, от клиента принимаем только тайтл и валидируем
    def post(self):
        data = request.get_json() # читает данные из запроса
        if data is None:
            return jsonify({"error": "JSON необхлдим"}), 400
        try:
            val_data = task_in_schema.load(data) # валидирует данные от клиента (десериализация)
        except ValidationError as err:
            return jsonify(err.messages), 400
        
        task = self.model(**val_data) # создал ORM-объект
        task.creating_author_id = GetCurrentUserID()
        task.status = "INITIALIZED" #фиксированный статус при создании новго тз
        task.parent_id = None
        task.is_active = True
        #task.version = 1

        db.session.add(task) # записал строку в бд
        db.session.commit()

        result = task_out_schema.dump(task) # сериализовал объект в JSON
        return jsonify(result), 201
    
class TaskDelete(MethodView):
    model = TechnicalTask

    def post(self, task_id):
        task = self.model.query.get(task_id)
        if task is None:
            return jsonify({"error":"ТЗ не найдено"}), 404
        
        task.deletion_mark = True
        db.session.commit()
        
        return jsonify({"message":"ТЗ успешно удалено"}), 200

# кортеж с фиксированными статусами
# вот его и словарь с переходом вероятно надо как-то оформить в отдельном классе в "справочниках"
STATUSES = (
    "INITIALIZED",
    "PLAN_CREATED",
    "APPROVED",
    "DONE",
)
# словарь с фиксированными переходами между статусами (значения - множества)
STATUS_TRANSITIONS = {
    "INITIALIZED": {"PLAN_CREATED"},
    "PLAN_CREATED": {"APPROVED"},
    "APPROVED": {"DONE"},
    "DONE": set(), # пустое множество, переходов нет, конечный статус
}

# входит ли новый статус в множество разрешённых переходов для текущего статуса (булевое)
def change_status(current_status, new_status):
    return new_status in STATUS_TRANSITIONS.get(current_status, set())

class TaskStatus(MethodView): 
    """статус исполнения тз (машина состояний). редактируется в этом сервисе сразу в таблице"""
    model = TechnicalTask 

    def put(self, task_id): #task_id идентификатор ТЗ, фласк его берёт из адреса запроса.
        data = request.get_json()
        if data is None:
            return jsonify({"error":"JSON необходим"}), 400
        try:
            val_data = status_schema.load(data)
        except ValidationError as err:
            return jsonify(err.messages), 400
        task = self.model.query.get(task_id) #локал переменная, в которой орм объект конкрет ТЗ.
        if task is None:
            return jsonify({"error": "ТЗ не найдено"}), 404 #если нет такого id

        new_status = val_data["status"] #берём новое значения статуса из присланных данных
        current_status = task.status #берём текущее значение статуса из таблицы

        if new_status not in STATUSES:
            return jsonify({
                "error": "Недопустимый статус",
                "allowed_statuses": list(STATUSES)
            }), 400 #если нет такого статуса

        if not change_status(current_status, new_status):
            return jsonify({
                "error": "Недопустимый переход статуса",
                "current_status": current_status,
                "new_status": new_status
            }), 400  #нельзя из текущего состояния перейти в указанный статус

        task.status = new_status #присваиваем новое значение орм объекту
        db.session.commit()
        
        result = task_out_schema.dump(task) #сериализуем 
        return jsonify(result), 200


class TaskRegenerate(MethodView):
    model = TechnicalTask
#это пока что временная бессмысленная "загушка", не полноценный процесс перегенерации естественно
#вероятно надо будет перегенерацию в отдельный модуль выносить
    def post(self, task_id):
        task = self.model.query.get(task_id)
        if task is None:
            return jsonify({"error":"ТЗ не найдено"}), 404
        
        return jsonify({
            "message": "Перегенерация ТЗ запущена",
            "task_id": str(task.id),
            "current_status": task.status
        }), 200