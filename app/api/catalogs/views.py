from flask import jsonify
from flask.views import MethodView

from app import db
from app.database.models import TechnicalTask, Organization, Equipment, PersonInfo, TaskPerson
from app.database.schemas import OrganizationSchema,EquipmentSchema, \
 PersonInfoSchema,TechnicalTaskSchema, TaskPersonSchema, PersonRoleSchema,  StatusSchema,\
    TechnicalTaskCreateSchema, SuccessResponseSchema, BadIdResponseSchema, UnprocessableEntitySchema\

class CatalogPersonnel(MethodView):
    def get(self):
        ...

class CatalogOrganizations(MethodView):
    def get(self):
        ...

class CatalogEquipment(MethodView):
    def get(self):
        ...