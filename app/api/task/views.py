from flask import jsonify, request
from flask.views import MethodView
from app import db
from app.database.models import TechnicalTask

class TaskOne(MethodView):
    model = TechnicalTask
   #schema = xxx (пока не добавляла валидацию и не заполняла файл schemas.py)
    def get(self):
        items = self.model.query.all()
        # записи - в формат словаря
        result = [
              {
                    "id": str(item.id),
                    "status": item.status,
              }
              for item in items
        ]
        return jsonify(result) #возвращает записи из модели в форме джейсон