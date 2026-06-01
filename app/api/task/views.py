from flask import jsonify, request
from flask.views import MethodView
from marshmallow import ValidationError, EXCLUDE
import uuid

from app import db
from app.database.models import TechnicalTask, Organization, Equipment, PersonInfo, TechnicalTaskPerson
from app.database.schemas import OrganizationSchema,EquipmentSchema, \
    StatusSchema, PersonInfoSchema,TechnicalTaskSchema, TechnicalTaskPersonSchema, TaskPersonSchema, \
    TechnicalTaskCreateSchema, SuccessResponseSchema, BadIdResponseSchema, UnprocessableEntitySchema

task_in_schema = TechnicalTaskInSchema()
tasks_out_schema = TechnicalTaskOutSchema(many=True)
status_schema = StatusSchema() 

#def GetCurrentUserID():
#    if PersonInfo.query.get('fed3egec-673c-49ab-b73e-8d9934bf0d70'):
#        return 'fed3egec-673c-49ab-b73e-8d9934bf0d70'
#    else: 
#        return None  #это когда появится таблица 
    
def GetCurrentUserID():
    return uuid.UUID('fed3e0ec-673c-49ab-b73e-8d9934bf0d70')

class TaskList(MethodView):
    model = TechnicalTask
    schema = xxx

    def get(self): 
        return jsonify(self.briefing_schema (many=True).dump(self.
                briefing_model.query.filter(self.briefing_model.deletion_mark.is_(False)).all()))

    def post(self):
        data = request.get_json()
        try:
            current_user = GetCurrentUserId()
            target_briefing = self.briefing_schema().load(data, session=db.session, unknown=EXCLUDE) 
            target_briefing.creating_author_id = current_user
            db.session.add(target_briefing)
            if not data.get('persons'):
                raise ValidationError({'persons': ['Отсутствует список ЛС, проходящего проверку']}) 
            for person in data['persons']:
                if not person.get('id'):
                    person['id'] = uuid.uuid4()
                    target_person = None
                else:
                    target_person = PersonInfo.query.get(person['id'])
                if not target_person:
                    target_person = PersonInfoSchema().load(person, session=db.session, unknown=EXCLUDE)
                    db.session.add(target_person)
                    grades = self.grades_schema().load(person, session=db.session, unknown=EXCLUDE) 
                    grades. person = target_person
                    grades.briefing = target_briefing
                    db.session.add(grades)
        except ValidationError as err:
            db.session.rollback()
            return UnprocessableEntitySchema().dump (dict (messages=err.messages)), 422 
        db.session.commit()
        return SuccessResponseSchema().dump(
            dict(message='Данные проведенного инструктажа успешно добавлены')), 201
    
    def delete(self): 
        target_id = request.args.get('id')
        target_briefing = self.briefing_model.query.get(target_id)
        if not target_briefing:
            return BadIdResponseSchema().dump (dict (message='неверный id ТЗ')), 422
        current_user = GetCurrentUserId()
        target_briefing.deletion_mark = True
        target_briefing.deleting_author_id = current_user
        db.session.commit()
        return SuccessResponseSchema().dump(dict(message='Данные ТЗ успешно удалены')), 201
        
"""
        task = self.model(**val_data) # создал ORM-объект
        task.id = uuid.uuid4()
        task.creating_author_id = None
        task.status = "INITIALIZED" 
        task.parent_id = None
        task.is_active = True

        db.session.add(task) 
        db.session.commit()

        return jsonify(task_out_schema.dump(task)), 201
"""


class TaskOne(MethodView):
    model = TechnicalTask
    schema = task_out_schema

    def get(self, task_id):
        task = self.model.query.get(task_id)
        if not task or task.deletion_mark:
            return jsonify({"error":"ТЗ не найдено"}), 404
        return jsonify({'TechnicalTask': self.schema.dump(task)})
    
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
STATUSES = (
    "INITIALIZED",
    "PLAN_CREATED",
    "APPROVED",
    "DONE",
)
# словарь с фиксированными переходами между статусами (значения - множества)
STATUS_TRANSITIONS = {
    "INITIALIZED": {"PLAN_CREATED","APPROVED","DONE"},
    "PLAN_CREATED": {"INITIALIZED","APPROVED","DONE"},
    "APPROVED": {"INITIALIZED","PLAN_CREATED","DONE"},
    "DONE": {"INITIALIZED", "PLAN_CREATED", "APPROVED"}, 
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
        
        return jsonify(task_out_schema.dump(task)), 200


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