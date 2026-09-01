from flask import jsonify, request
from flask.views import MethodView
from marshmallow import ValidationError, EXCLUDE
import uuid
from sqlalchemy.exc import IntegrityError
from requests import get, post,ConnectionError

from app import db
from app.api.task.statuses import TASK_STATUSES, GetStatusValues,CanChangeStatus
from app.database.models import TechnicalTask, Organization, Equipment, PersonInfo, TaskPerson, RoleInfo
from app.database.schemas import OrganizationSchema,EquipmentSchema, TaskUpdateSchema, \
 PersonInfoSchema,TechnicalTaskSchema, TaskPersonSchema, StatusSchema,\
    CreateTaskSchema, SuccessResponseSchema, BadIdResponseSchema, UnprocessableEntitySchema\

def GetCurrentUserId():
    if PersonInfo.query.get('fed3e0ec-673c-49ab-b73e-8d9934bf0d70'):
        return 'fed3e0ec-673c-49ab-b73e-8d9934bf0d70'
    else: 
        return None 


class TaskList(MethodView):
    model = TechnicalTask
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
            val_data = self.create_schema().load(data,unknown=EXCLUDE)
            measurement1=val_data["measurement_id"]
            task = self.model.query.filter_by(measurement_id=measurement1).first()
            if task is not None:
               return "ТЗ с таким measurement_id уже существует", 409
            target_task = self.model(**val_data)
            target_task.id = uuid.uuid4()
            target_task.status = "INITIALIZED"
            target_task.is_active = True
            target_task.deletion_mark = False
            target_task.creating_author_id = None

            db.session.add(target_task)
            db.session.commit()
        except ValidationError as err:
            db.session.rollback()
            return UnprocessableEntitySchema().dump(dict(messages=err.messages)), 422
        #except IntegrityError:
        #    db.session.rollback()
        #    return jsonify({"error": "Уже существует ТЗ по данной неисправности"}), 409
        return jsonify(self.task_schema().dump(target_task)), 201
    
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


class AdmittedPeople(MethodView):
    model = TechnicalTask
    def get(self, task_id):
        target_task = self.model.query.get(task_id)
        if not target_task or target_task.deletion_mark:
            return jsonify({"error":"ТЗ не найдено"}), 404
        
        equipment = Equipment.query.get(target_task.efo_ref)
        organization = Organization.query.get(target_task.organization_ref)
        if not equipment:
            return jsonify({"efo_ref": "Оборудование для ТЗ не найдено"})
        if not organization:
            return jsonify({"organization_ref": " организация не найдена у тз"})

        esi_id = equipment.esi_id
        org = organization.id

        try:
            response = get('http://192.168.74.71:9037/AttestationAPI/passports/suitable_personnel',params={"esi": str(esi_id),"organization":str(org)})
        except ConnectionError:
            return jsonify({"error": "Не удалось подключиться к сервису Attestation"}), 503

        people = response.json()
        
        return jsonify({'persons':people,
                        'esi':str(equipment.esi_id)}), 200


class TaskUpdate(MethodView):
    model = TechnicalTask
    model2 = TaskPerson
    update_schema = TaskUpdateSchema
    task_schema = TechnicalTaskSchema

    def put(self, task_id):
        data = request.get_json()
        target_task = self.model.query.get(task_id)
        if target_task is None or target_task.deletion_mark:
            return jsonify({"error": "ТЗ не найдено"}), 404
        try:
            val_data = self.update_schema().load(data)
            target_task.number = val_data["number"]
            roles = RoleInfo.query.all()
            validated_persons = []
            for role in roles:
                role_code = role.code
                selected_persons = val_data.get(role_code)
                if selected_persons is not None:
                    if role_code == "field_team":
                        person_ids = selected_persons
                    else:
                        person_ids = [selected_persons]
                    for person_id in person_ids:
                        target_person = PersonInfo.query.get(person_id)
                        if not target_person:
                            raise ValidationError({role_code: [f'Человек с id {person_id} не найден']})
                        validated_persons.append({
                            "person": target_person,
                            "role": role})
            old_task_persons = self.model2.query.filter_by(task_id=task_id).all()
            
            for old_task_person in old_task_persons:
                db.session.delete(old_task_person)
            for person_data in validated_persons:
                task_person = self.model2(
                    id=uuid.uuid4(),
                    task=target_task,
                    person=person_data["person"],
                    role=person_data["role"]
                )
                db.session.add(task_person)
            db.session.commit()
        except ValidationError as err:
            db.session.rollback()
            return UnprocessableEntitySchema().dump(dict(messages=err.messages)), 422
        return 'личный состав обновлён'
    '''
        updated_persons = self.model2.query.filter_by(task_id=task_id).all()
        return jsonify({
            "task": self.task_schema().dump(target_task),
            "persons": TaskPersonSchema(many=True).dump(updated_persons)
        }), 200
    '''

class SingleTask(MethodView):
    model = TechnicalTask
    model2 = TaskPerson
    schema = TechnicalTaskSchema

    def get(self, task_id):
        task = self.model.query.get(task_id)
        if not task or task.deletion_mark:
            return jsonify({"error":"ТЗ не найдено"}), 404
        persons = self.model2.query.filter_by(task_id=task_id).all()
        
        response = self.schema().dump(task)
        response["field_team"] = []
        for task_person in persons:
            role_code = task_person.role.code
            if role_code == "field_team":
                response["field_team"].append(str(task_person.person_id))
            else:
                response[role_code] = str(task_person.person_id)
        return jsonify(response), 200

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
                    "error": "Недопустимый переход статуса",}), 400  #нельзя из текущего состояния перейти в указанный статус
            task.status = new_status #присваиваем новое значение орм объекту
        except ValidationError as err:
            db.session.rollback()
            return UnprocessableEntitySchema().dump (dict (messages=err.messages)), 422 
        db.session.commit()
        return jsonify(self.task_schema().dump(task)), 200


class Autogenerate(MethodView):
    model = TechnicalTask
    model2 = TaskPerson
    schema = TechnicalTaskSchema
 
    def post(self, task_id):
        task = self.model.query.get(task_id)
        if not task or task.deletion_mark:
            return jsonify({"error":"ТЗ не найдено"}), 404
        number = task.number
        persons = self.model2.query.filter_by(task_id=task_id).all()

        try:
            try:
                response = get('http://192.168.74.63:9005/DAFDAPI/templates/asd8hyH9-56gd-87gy-a5dv-56747gdhcn8h/generate_doc',params={})
            except ConnectionError:
                return jsonify({"error": "Не удалось подключиться к сервису DAFD"}), 503
            template = response.json()
            text_fields = template.get("text_fields", {})
            text_fields["tz_date"] = str(task.creation_date or "")
            text_fields["N_TZ"] = str(task.number or "")

            template["text_fields"] = text_fields

            filled_template = template
            payload = {'name':f'ТЗ номер {number}', 'description':f'сгенерированный документ номер {number}', 'data':filled_template}
            response = post('http://192.168.74.63:9005/DAFDAPI/templates/asd8hyH9-56gd-87gy-a5dv-56747gdhcn8h/generate_doc',json=payload)
            result = response.json()
            result["id"] = result.pop("doc_ref")
            result["source"] = "doc"
            task.doc_ref = result["id"]
        except ValidationError as err:
            return UnprocessableEntitySchema().dump(dict(messages=err.messages)), 422
        except ConnectionError:
             return jsonify({"error": "Не удалось подключиться к сервису DAFD"}), 503
        db.session.commit()
        return jsonify(result), 200

class TaskRegenerate(MethodView):
    model = TechnicalTask
#это пока что временная бессмысленная "загушка", не полноценный процесс перегенерации 
#вероятно надо будет перегенерацию в отдельный модуль выносить
    def post(self, task_id):
        task = self.model.query.get(task_id)
        if task is None:
            return jsonify({"error":"ТЗ не найдено"}), 404
        
        return jsonify({"message": "Перегенерация ТЗ запущена"}), 200
        
