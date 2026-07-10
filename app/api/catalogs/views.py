from flask import jsonify, request
from flask.views import MethodView
from marshmallow import ValidationError, EXCLUDE

from app import db
from app.database.models import PersonInfo, Organization, Equipment
from app.database.schemas import OrganizationSchema, EquipmentSchema,PersonInfoSchema,\
    PersonInfoLoadSchema, SuccessResponseSchema,UnprocessableEntitySchema,BadIdResponseSchema


class CatalogMixin:
    model = None
    load_schema = None
    dump_schema = None

    def get(self):
        records = self.model.query.all()
        return jsonify(self.dump_schema(many=True).dump(records)), 200

    def post(self):
        data = request.get_json()

        if data is None:
            return jsonify({"error": "JSON необходим"}), 400
        try:
            if isinstance(data, list):
                records = self.load_schema(many=True).load(data,session=db.session,unknown=EXCLUDE)
                for record in records:
                    db.session.add(record)
            else:
                record = self.load_schema(many=False).load(data,session=db.session,unknown=EXCLUDE)
                db.session.add(record)
        except ValidationError as err:
            db.session.rollback()
            return UnprocessableEntitySchema().dump(dict(messages=err.messages)), 422
        db.session.commit()
        return SuccessResponseSchema().dump(dict(message="Каталог успешно загружен")), 201

    def put(self):
        return self.post()


class CatalogPersonnel(CatalogMixin, MethodView):
    model = PersonInfo
    load_schema = PersonInfoLoadSchema
    dump_schema = PersonInfoSchema

    def get(self):
        personnel = PersonInfo.query.filter(
            PersonInfo.is_active.is_(True)
        ).all()
        return jsonify(self.dump_schema(many=True).dump(personnel)), 200

    def delete(self):
        data = request.get_json()
        if data is None:
            return jsonify({"error": "JSON необходим"}), 400
        ref = data.get("ref")
        target = PersonInfo.query.get(ref)
        if target:
            target.is_active = False
            db.session.commit()
            return "Пользователь успешно удален", 201

        return BadIdResponseSchema().dump(dict(message="Такого пользователя нет в БД")), 422


class CatalogOrganization(CatalogMixin, MethodView):
    model = Organization
    load_schema = OrganizationSchema
    dump_schema = OrganizationSchema

    def get(self):
        organizations = Organization.query.filter(Organization.parent_id.is_(None)).all()

        return jsonify(self.dump_schema(many=True).dump(organizations)), 200


class CatalogEquipment(MethodView):
    @staticmethod
    def get():
        equipment = Equipment.query.filter(Equipment.parent_id.is_(None)).all()
        return jsonify(EquipmentSchema(many=True).dump(equipment)), 200
