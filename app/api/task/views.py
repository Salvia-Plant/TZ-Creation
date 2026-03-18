from flask import jsonify, request
from flask.views import MethodView
from marshmallow import ValidationError

from app import db
from app.database.models import TechnicalTask
from app.database.schemas import TechnicalTaskInSchema, TechnicalTaskOutSchema

task_in_schema = TechnicalTaskInSchema()
task_out_schema = TechnicalTaskOutSchema()
tasks_out_schema = TechnicalTaskOutSchema(many=True)

class TaskOne(MethodView):
    model = TechnicalTask
    
    def get(self):
        items = self.model.query.all()
        result = tasks_out_schema.dump(items)
        return jsonify(result) #возвращает записи из модели в форме джейсон (сериализация)
    
    def post(self):
        data = request.get_json() # читает данные из конекста запроса
        if not data:
            return jsonify({"error": "JSON необхлдим"}), 400
        try:
            val_data = task_in_schema.load(data) # валидирует данные от клиента (десериализация)
        except ValidationError as err:
            return jsonify(err.messages), 400
        
        task = self.model(**val_data) # создал ORM-объект

        db.session.add(task) # записал строку в PostgreSQL
        db.session.commit()

        result = task_out_schema.dump(task) # сериализовал объект в JSON
        return jsonify(result), 201