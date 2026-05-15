from app import db
from sqlalchemy.dialects.postgresql import UUID 
import uuid
from datetime import datetime

class TechnicalTask(db.Model):
    """основная сущность"""

    __tablename__= 'technical_task'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4) #uuid первичный ключ
    parent_id = db.Column(UUID(as_uuid=True),nullable=True, doc='id родителя') # ссылка на предыдущую версию
    creating_author_id = db.Column(UUID(as_uuid=True),nullable=True, doc='id автора записи')
    fault_detected_at = db.Column(db.DateTime, doc='Дата обнаружения неисправности')
    created_at = db.Column(db.DateTime, default=datetime.now, doc='Дата создания записи')
    title = db.Column(db.String(255), nullable=False, doc="Название ТЗ")
    status = db.Column(db.String(32), nullable=False, default="INITIALIZED") 
    is_active = db.Column(db.Boolean, nullable = False, default = True, doc = "флаг активной записи") #для текущей версии
    deletion_mark = db.Column(db.Boolean, nullable = False, default = False, server_default = 'false') 


class Organization(db.Model):
    """Организации"""

    __tablename__ = "organization"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    parent_id = db.Column(UUID(as_uuid=True), doc="id родителя")
    org_type = db.Column(db.String(255), nullable = True, doc = 'Тип организации (Изготовитель или ЭксплуатирующаяОрганизация)')
    org_title = db.Column(db.String(255), nullable=False, doc="Наименование организации")
    children = db.relationship("Organization", primaryjoin=parent_id == id, foreign_keys=id, 
                               remote_side=parent_id, uselist=True)
    

class Equipment(db.Model):
    """Оборудование, ЭФО"""

    __tablename__ = "equipment"

    id = db.Column(UUID(as_uuid=True), primary_key=True)
    equipment_name = db.Column(db.String(255), nullable=False, doc="Наименование оборудования")
    #technical_tasks = db.relationship("TechnicalTask", back_populates="equipment",passive_deletes=True)



class PersonInfo(db.Model):
    """Сведения о должностном лице"""

    __tablename__= 'person_info'

    id = db.Column(UUID(as_uuid=True), primary_key=True) 
    military_unit_id = db.Column(UUID(as_uuid=True), db.ForeignKey('organization.id')) # ссылка на предыдущу
    military_unit = db.Column(UUID(as_uuid=True),nullable=True, doc='Войсковая часть')
