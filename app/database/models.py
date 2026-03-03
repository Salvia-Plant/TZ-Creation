from app import db
from sqlalchemy.dialects.postgresql import UUID 
import uuid

class TechnicalTask(db.Model):
    """первая модель"""

    __tablename__= 'Technical Task'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4) #uuid первичный ключ
    status = db.Column(db.String(32), nullable=False, default="INITIALIZED") #статус исполнения тз