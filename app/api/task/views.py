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

class TaskOne(MethodView):
    model = TechnicalTask
    
    def get(self):
        items = self.model.query.all()
        result = tasks_out_schema.dump(items)
        return jsonify(result) #возвращает записи из модели в форме джейсон (сериализация)
    
    def post(self):
        data = request.get_json() # читает данные из конекста запроса
        if data is None:
            return jsonify({"error": "JSON необхлдим"}), 400
        try:
            val_data = task_in_schema.load(data) # валидирует данные от клиента (десериализация)
        except ValidationError as err:
            return jsonify(err.messages), 400
        
        task = self.model(**val_data) # создал ORM-объект
        task.status = "INITIALIZED" #фиксированный статус при создании новго тз

        db.session.add(task) # записал строку в PostgreSQL
        db.session.commit()

        result = task_out_schema.dump(task) # сериализовал объект в JSON
        return jsonify(result), 201
    
# кортеж с фиксированными статусами
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

    def post(self, task_id): #task_id идентификатор ТЗ, фласк его берёт из адреса запроса.
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
            }), 400  # нельзя из текущего состояния перейти в указанный статус

        task.status = new_status #присваиваем новое значение орм объекту
        db.session.commit()

        result = task_out_schema.dump(task) #сериализуем 
        return jsonify(result), 200


class TaskRegenerate(MethodView):
    model = TechnicalTask