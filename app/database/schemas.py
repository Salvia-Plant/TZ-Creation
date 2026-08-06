from marshmallow import Schema, fields, EXCLUDE, post_load, pre_load, validate
from .models import *
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from .models import TechnicalTask, Organization, Equipment, PersonInfo, TaskPerson
from datetime import datetime

class OrganizationSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Organization

    id = fields.UUID(required=True)
    parent_id = fields.UUID(required=True)
    org_type = fields.Str(required=True)
    org_title = fields.Str(required=True)

    children = fields.Nested('OrganizationSchema', many=True, dump_only=True)

class EquipmentSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Equipment

    id = fields.UUID(required=True)
    equipment_name = fields.Str(required=True)
    esi_id = fields.UUID(required=True)
    from_designation = fields.Str(dump_only=True)
    factory_number = fields.Str(dump_only=True)

    children = fields.Nested('EquipmentSchema', many=True, dump_only=False)
 
class PersonInfoLoadSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = PersonInfo
    
    id = fields.UUID(required=True, data_key='Ref', load_only=True)
    organization_id = fields.UUID(required=False, data_key='organization_ref',allow_none=True)
    department = fields.Str(required=False, data_key='subdivision_description',allow_none=True)
    full_name = fields.Str(required=False, allow_none=True)
    position = fields.Str(required=False, data_key='position_description', load_only=True)
    rank = fields.Str(required=True, data_key='rank_description', load_only=True)

class PersonInfoSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = PersonInfo

    id = fields.UUID(required=True)
    organization_id = fields.UUID(required=False, allow_none=True)
    organization = fields.Pluck('OrganizationSchema','org_title',dump_only=True)
    department = fields.Str(required=False, allow_none=True)
    position = fields.Str(required=False, allow_none=True)
    rank = fields.Str(required=False, allow_none=True)
    full_name = fields.Str(required=False, allow_none=True)

class TechnicalTaskSchema(SQLAlchemyAutoSchema): #для дампа 
    class Meta:
        model = TechnicalTask
        exclude = ('creating_author', 'deleting_author')

    id = fields.UUID(dump_only=True)
    parent_id = fields.UUID(required=False, allow_none=True)
    creating_author_id = fields.UUID(required=False, allow_none=True)
    deleting_author_id = fields.UUID(required=False, allow_none=True)
    organization_ref = fields.UUID(required=False, allow_none=True)
    organization = fields.Pluck('OrganizationSchema','org_title',dump_only=True)
    efo = fields.Pluck('EquipmentSchema','equipment_name',dump_only=True)
    efo_ref = fields.UUID(required=False, allow_none=True)
    combat_impact = fields.Boolean(required=False, allow_none=True)
    malfunction_time = fields.DateTime(format='%d.%m.%YT%H:%M:%S',required=False, allow_none=True)
    measurement_id = fields.Int(required=False, allow_none=True)
    creation_date = fields.Date(dump_only=True)
    number = fields.Str(dump_only=True)
    status = fields.Str(dump_only=True)
    is_active = fields.Boolean(dump_only=True)
    deletion_mark = fields.Boolean(dump_only=True)

class TaskPersonSchema(SQLAlchemyAutoSchema):
    """Для связей человек-ТЗ-роль"""
    class Meta:
        model = TaskPerson
        exclude = ('task', 'person', 'role')

    id = fields.UUID(dump_only=True)
    task_id = fields.UUID(required=False, allow_none=True)
    person_id = fields.UUID(required=True)
    role_id = fields.UUID(required=True)

    role_name = fields.Pluck('RoleInfoSchema','name',attribute='role',dump_only=True)
    role_code = fields.Pluck('RoleInfoSchema','code',attribute='role',dump_only=True)
    person_name = fields.Pluck('PersonInfoSchema','full_name',attribute='person',dump_only=True)

"""
class PersonRoleSchema(Schema):
    #Выбранный человек и его роль в ТЗ, для входных данных
    person_id = fields.UUID(required=True)
    role_id = fields.UUID(required=True)


class TaskUpdateSchema(Schema):
    persons=fields.Nested(PersonRoleSchema, many=True, required=True)
    number = fields.Str()
"""

class TaskUpdateSchema(Schema):
    number = fields.Str(required=False)

    leader = fields.UUID(required=False, allow_none=True)
    special_service_officer = fields.UUID(required=False, allow_none=True)
    data_preparation_officer = fields.UUID(required=False, allow_none=True)
    support_officer = fields.UUID(required=False, allow_none=True)

    field_team = fields.List(fields.UUID(),required=False)
    
class CreateTaskSchema(Schema):
    malfunction_time = fields.DateTime(required=True)
    measurement_id = fields.Int(required=True)
    organization_ref = fields.UUID(required=True)
    efo_ref = fields.UUID(required=True)
    combat_impact = fields.Boolean(required=False, allow_none=True)

class RoleInfoSchema(SQLAlchemyAutoSchema): 
    """Справочник ролей ЛС для ТЗ"""
    class Meta:
        model = RoleInfo

    id = fields.UUID()
    name = fields.Str(required=True)
    code = fields.Str(required=True) #для нас с Катей
    is_multiple = fields.Boolean()

class StatusSchema(Schema):
    status = fields.Str(required=True)

class SuccessResponseSchema(Schema):
    message = fields.Str()

class BadIdResponseSchema(Schema):
    message = fields.Str()

class UnprocessableEntitySchema(Schema):
    messages = fields.Dict(fields.Str())
