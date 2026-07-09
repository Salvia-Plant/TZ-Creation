import asyncio
import ssl
import websockets
import json

from flask.views import MethodView
from collections import OrderedDict

from marshmallow import ValidationError, EXCLUDE, fields, pre_load
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from app import app, db
from app.database.models import Organization, Equipment
from app.database.schemas import UnprocessableEntitySchema


EMPTY_UUID = '00000000-0000-0000-0000-000000000000'


class OrganizationFromParserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Organization
        exclude = ('children',)

    id = fields.UUID(required=True,data_key='Ref',load_only=True)
    parent_id = fields.UUID(required=False,data_key='Parent',allow_none=True,load_only=True)
    org_title = fields.Str(required=True,data_key='Description',load_only=True)

    @pre_load(pass_many=True)
    def prepare_parent_organization(self, data, **kwargs):
        for organization in data:
            if organization.get('Parent') == EMPTY_UUID:
                organization.pop('Parent', None)

        return data


class EfoFromParserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Equipment
        # Если в твоей модели Equipment нет поля/relationship children,
        # эту строку нужно убрать.
        exclude = ('children',)

    id = fields.UUID(required=True, data_key='Ref',load_only=True)
    parent_id = fields.UUID(required=False,data_key='Parent',allow_none=True,load_only=True)
    equipment_name = fields.Str(required=True, data_key='Description',load_only=True)
    designation = fields.Str(required=False,data_key='OboznachenieFormulyara',allow_none=True,load_only=True)
    factory_number = fields.Str(required=False,data_key='ZavodskoyNomerIzdeliyal',allow_none=True,load_only=True)
    esi_id = fields.UUID(required=False,data_key='ZavodskoyNomerIsdeliya',allow_none=True,load_only=True )
   
    @pre_load(pass_many=True)
    def prepare_fks(self, data, **kwargs):
        for product in data:
            for key in (
                'ZavodskoyNomerIzdeliyal',
                'Parent',
                'ZavodskoyNomerIsdeliya',):
                if not product.get(key) or product.get(key) == EMPTY_UUID:
                    product.pop(key, None)
        return data


class ParserReceiver:
    loop = asyncio.get_event_loop()

    key_func = OrderedDict()
    key_func['CatalogObject.Organizacii'] = OrganizationFromParserSchema
    key_func['CatalogObject.LenInfo_JEHIFO'] = EfoFromParserSchema

    async def start_client(self):
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        url = 'wss://{}'.format(app.config['PARSER_ADDRESS'])

        async with websockets.connect(
            url,
            ssl=ssl_context,
            max_size=2 ** 40
        ) as websocket:
            message = {'table_names': [table_name for table_name in self.key_func.keys()]}
            await websocket.send(json.dumps(message))
            try:
                for _ in range(len(self.key_func.keys())):
                    message = await websocket.recv()
                    table_name, data = next(iter(json.loads(message).items()))
                    schema_class = self.key_func.get(table_name)
                    if schema_class is None:
                        continue
                    if data:
                        table = schema_class(many=True).load(data,session=db.session,unknown=EXCLUDE)
                        for record in table:
                            db.session.merge(record)
                        db.session.commit()
            except ValidationError as err:
                db.session.rollback()
                return UnprocessableEntitySchema().dump(dict(messages=err.messages)), 422

            except websockets.exceptions.ConnectionClosed:
                db.session.rollback()
                return ('Сервис PANDA закрыл соединение до завершения обновления баз данных!'), 201

        return 'База данных успешно обновлена', 201


class ParserExchange(MethodView):
    @staticmethod
    def post():
        parser = ParserReceiver()
        result = ParserReceiver.loop.run_until_complete(
            parser.start_client()
        )

        return result