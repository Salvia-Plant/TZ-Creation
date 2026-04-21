from app import db
from sqlalchemy.dialects.postgresql import UUID 
import uuid
from datetime import datetime

class TechnicalTask(db.Model):
    """первая модель"""

    __tablename__= 'technical_task'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4) #uuid первичный ключ
    parent_id = db.Column(UUID(as_uuid=True), doc='id родителя') # для версий
    creating_author_id = db.Column(UUID(as_uuid=True), doc='id автора записи')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    version = db.Column(db.Integer, nullable=False, default=1, doc='Версия ТЗ') # для версий
    title = db.Column(db.String(255), nullable=False, doc="Название ТЗ")
    status = db.Column(db.String(32), nullable=False, default="INITIALIZED") #статус исполнения тз
    is_active = db.Column(db.Boolean, default = True, doc = "флаг активной записи") #для текущей версии
    deletion_mark = db.Column(db.Boolean, nullable = False, default = False, server_default = 'false') 
