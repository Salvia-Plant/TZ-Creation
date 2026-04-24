from marshmallow import Schema, fields, EXCLUDE, post_load, pre_load, validate
from .models import *
import uuid
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

#class TechnicalTaskSchema(SQLAlchemyAutoSchema): - на случай если нужно использовать класс мета    
#    class Meta:
#        model = TechnicalTask
#        load_instance = True

class TechnicalTaskInSchema(Schema): #для десериализации, обработка POST запроса
    title = fields.Str(required=True) #что клиент имеет право присылать

class TechnicalTaskOutSchema(Schema): #для сериализации, обработка GET запроса
    id = fields.UUID(dump_only=True) 
    parent_id = fields.UUID(allow_none = True)
    creating_author_id = fields.UUID(allow_none=True)
    created_at = fields.DateTime()
    title = fields.Str()
    status = fields.Str()
    is_active = fields.Boolean()
    deletion_mark = fields.Boolean()

class StatusSchema(Schema):
    status = fields.Str(required=True) # поле статуса обязательное