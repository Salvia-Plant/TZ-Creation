from flask import jsonify, request
from flask.views import MethodView
from marshmallow import ValidationError, EXCLUDE
import uuid

from app import db
from app.api.task.statuses import TASK_STATUSES, GetStatusValues,CanChangeStatus
from app.database.models import TechnicalTask, Organization, Equipment, PersonInfo, TaskPerson
from app.database.schemas import OrganizationSchema,EquipmentSchema, \
 PersonInfoSchema,TechnicalTaskSchema, TaskPersonSchema, PersonRoleSchema,  StatusSchema,\
    CreateTaskSchema, SuccessResponseSchema, BadIdResponseSchema, UnprocessableEntitySchema\

def GetCurrentUserId():
    if PersonInfo.query.get('fed3e0ec-673c-49ab-b73e-8d9934bf0d70'):
        return 'fed3e0ec-673c-49ab-b73e-8d9934bf0d70'
    else: 
        return None 
    
class TaskList(MethodView):
    model = TechnicalTask
    model2 = TaskPerson
    create_schema = CreateTaskSchema
    task_schema = TechnicalTaskSchema

    def get(self): 
        return jsonify(self.task_schema(many=True).dump(self.
                model.query.filter(self.model.deletion_mark.is_(False)).all()))

    def post(self):
        data = request.get_json()
        if data is None:
            return jsonify({"error": "JSON необходим"}), 400
        try:
            current_user = GetCurrentUserId()
            val_data = self.create_schema().load(data, unknown=EXCLUDE) 
            persons = val_data.pop('persons') #отдельно берём людей, их не надо в technicaltask
            if not persons:
                raise ValidationError({'persons': ['Отсутствует список личного состава для создания ТЗ']}) 
            target_task = self.model(**val_data) # создал ORM-объект
            target_task.id = uuid.uuid4()
            target_task.creating_author_id = current_user
            target_task.status = "INITIALIZED" 
            #target_task.parent_id = None #потом для перегенерации
            target_task.is_active = True
            db.session.add(target_task)
            # заполняем связующую таблицу людьми
            for person_data in persons:
                target_person = PersonInfo.query.get(person_data['person_id'])
                if not target_person:
                    raise ValidationError({'person_id': "Человек не найден"})
                task_person = self.model2(
                id = uuid.uuid4(),
                task=target_task,
                person=target_person,
                role=person_data['role'])
                db.session.add(task_person)
        except ValidationError as err:
            db.session.rollback()
            return UnprocessableEntitySchema().dump (dict (messages=err.messages)), 422 
        db.session.commit()
        return SuccessResponseSchema().dump(
            dict(message='Данные ТЗ успешно добавлены')), 201
    
    def delete(self): 
        target_id = request.args.get('id')
        target_task = self.model.query.get(target_id)
        if not target_task:
            return BadIdResponseSchema().dump (dict (message='неверный id ТЗ')), 404
        current_user = GetCurrentUserId()
        target_task.deletion_mark = True
        target_task.deleting_author_id = current_user
        db.session.commit()
        return SuccessResponseSchema().dump(dict(message='Данные ТЗ успешно удалены')), 201
    
class TaskUpdate(MethodView):
    def put(self, task_id):
        data = request.get_json()
        if data is None:
            return jsonify({"error": "JSON необходим"}), 400
        try:
            current_user = GetCurrentUserId()
            val_data = self.create_schema().load(data, unknown=EXCLUDE) 
            persons = val_data.pop('persons') #отдельно берём людей, их не надо в technicaltask
            if not persons:
                raise ValidationError({'persons': ['Отсутствует список личного состава для создания ТЗ']}) 
            target_task = self.model(**val_data) # создал ORM-объект
            target_task.id = uuid.uuid4()
            target_task.creating_author_id = current_user
            target_task.status = "INITIALIZED" 
            #target_task.parent_id = None #потом для перегенерации
            target_task.is_active = True
            db.session.add(target_task)
            # заполняем связующую таблицу людьми
            for person_data in persons:
                target_person = PersonInfo.query.get(person_data['person_id'])
                if not target_person:
                    raise ValidationError({'person_id': "Человек не найден"})
                task_person = self.model2(
                id = uuid.uuid4(),
                task=target_task,
                person=target_person,
                role=person_data['role'])
                db.session.add(task_person)
        except ValidationError as err:
            db.session.rollback()
            return UnprocessableEntitySchema().dump (dict (messages=err.messages)), 422 
        db.session.commit()
        return SuccessResponseSchema().dump(
            dict(message='Данные ТЗ успешно добавлены')), 201


class SingleTask(MethodView):
    model = TechnicalTask
    schema = TechnicalTaskSchema

    def get(self, task_id):
        task = self.model.query.get(task_id)
        if not task or task.deletion_mark:
            return jsonify({"error":"ТЗ не найдено"}), 404
        return jsonify({'TechnicalTask': self.schema().dump(task)})
    
class Statuses(MethodView):
    """отдельная ручка для получения списка статусов. для фронта"""
    def get(self):
        return jsonify(TASK_STATUSES), 200

class TaskStatus(MethodView): 
    """статус исполнения тз, редактируется в этом сервисе сразу в таблице"""
    model = TechnicalTask 
    schema = StatusSchema
    task_schema = TechnicalTaskSchema

    def put(self, task_id): #task_id идентификатор ТЗ, фласк его берёт из адреса запроса.
        data = request.get_json()
        if data is None:
            return jsonify({"error":"JSON необходим"}), 400
        try:
            val_data = self.schema().load(data)
            task = self.model.query.get(task_id) #локал переменная, в которой орм объект конкрет ТЗ.
            if task is None or task.deletion_mark:
                return jsonify({"error": "ТЗ не найдено"}), 404 #если нет такого id

            new_status = val_data["status"] #берём новое значения статуса из присланных данных
            current_status = task.status #берём текущее значение статуса из таблицы
            values = GetStatusValues() 
            if new_status not in values: 
                return jsonify({
                    "error": "Недопустимый статус",
                    "allowed_statuses": values
                }), 400 #если нет такого статуса
            if not CanChangeStatus(current_status, new_status): 
                return jsonify({
                    "error": "Недопустимый переход статуса",
                    "current_status": current_status,
                    "new_status": new_status
                }), 400  #нельзя из текущего состояния перейти в указанный статус
            task.status = new_status #присваиваем новое значение орм объекту
        except ValidationError as err:
            db.session.rollback()
            return UnprocessableEntitySchema().dump (dict (messages=err.messages)), 422 
        db.session.commit()
        return jsonify(self.task_schema().dump(task)), 200

class TaskRegenerate(MethodView):
    model = TechnicalTask
#это пока что временная бессмысленная "загушка", не полноценный процесс перегенерации 
#вероятно надо будет перегенерацию в отдельный модуль выносить
    def post(self, task_id):
        task = self.model.query.get(task_id)
        if task is None:
            return jsonify({"error":"ТЗ не найдено"}), 404
        
        return jsonify({"message": "Перегенерация ТЗ запущена"}), 200