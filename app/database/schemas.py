from marshmallow import Schema, fields, EXCLUDE, post_load, pre_load, validate
from .models import *
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from .models import TechnicalTask, Organization, Equipment, PersonInfo, TechnicalTaskPerson

class OrganizationSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Organization

    id = fields.UUID(required=True)
    org_title = fields.Str(required=True)

class EquipmentSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Equipment

    id = fields.UUID(required=True)
    equipment_name = fields.Str(required=True)

class PersonInfoSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = PersonInfo

    id = fields.UUID(required=True)
    organization_id = fields.UUID(required=False, allow_none=True)
    department = fields.Str(required=False, allow_none=True)
    position = fields.Str(required=False, allow_none=True)
    rank = fields.Str(required=False, allow_none=True)
    full_name = fields.Str(required=False, allow_none=True)
    status = fields.Str(required=False, allow_none=True)
    is_active = fields.Boolean(required=False)

class TechnicalTaskSchema(SQLAlchemyAutoSchema): #для дампа 
    class Meta:
        model = TechnicalTask
        exclude = ('creating_author', 'deleting_author', 'organization', 'efo')

    id = fields.UUID(dump_only=True)
    parent_id = fields.UUID(required=False, allow_none=True)
    creating_author_id = fields.UUID(required=False, allow_none=True)
    deleting_author_id = fields.UUID(required=False, allow_none=True)
    organization_id = fields.UUID(required=False, allow_none=True)
    efo_id = fields.UUID(required=False, allow_none=True)
    bg_impact = fields.Str(required=False, allow_none=True)
    fault_detected_at = fields.DateTime(required=False, allow_none=True)
    monitoring_id = fields.Str(required=False, allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    title = fields.Str(required=True)
    status = fields.Str(dump_only=True)
    is_active = fields.Boolean(dump_only=True)
    deletion_mark = fields.Boolean(dump_only=True)

class TechnicalTaskPersonSchema(SQLAlchemyAutoSchema): #чтение состава ТЗ, отдача связей ТЗ -люди, потенциально сериализация этих записей
    class Meta:
        model = TechnicalTaskPerson
        exclude = ('task', 'person')

    id = fields.UUID(dump_only=True)
    task_id = fields.UUID(required=False, allow_none=True)
    person_id = fields.UUID(required=True)
    role = fields.Str(required=True)

class PersonRoleSchema(Schema): #отдельная схема для людей (для загрузки), т.к нужно знать кого выбрали и в какой роли
    person_id = fields.UUID(required=True)
    role = fields.Str(required=True)

class TechnicalTaskCreateSchema(Schema): #для загрузки
    title = fields.Str(required=True)
    fault_detected_at = fields.DateTime(required=True)
    monitoring_id = fields.Str(required=True)
    organization_id = fields.UUID(required=True)
    efo_id = fields.UUID(required=True)
    bg_impact = fields.Str(required=False, allow_none=True)
    persons = fields.Nested(PersonRoleSchema, many=True, required=True)

class StatusSchema(Schema):
    status = fields.Str(required=True)

class SuccessResponseSchema(Schema):
    message = fields.Str()

class BadIdResponseSchema(Schema):
    message = fields.Str()

class UnprocessableEntitySchema(Schema):
    messages = fields.Dict(fields.Str())
"""
class TechnicalTaskInSchema(Schema): #для десериализации, обработка POST запроса
    title = fields.Str(required=True) #что клиент имеет право присылать
    fault_detected_at = fields.DateTime()

class TechnicalTaskOutSchema(Schema): #для сериализации, обработка GET запроса
    id = fields.UUID(dump_only=True) 
    parent_id = fields.UUID(allow_none = True)
    creating_author_id = fields.UUID(allow_none=True)
    fault_detected_at = fields.Date()
    created_at = fields.DateTime()
    title = fields.Str()
    status = fields.Str()
    is_active = fields.Boolean()
    deletion_mark = fields.Boolean()

class StatusSchema(Schema):
    status = fields.Str(required=True) # поле статуса обязательное
"""