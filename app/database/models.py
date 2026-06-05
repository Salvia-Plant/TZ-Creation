from app import db
from sqlalchemy.dialects.postgresql import UUID 
import uuid
from datetime import datetime


class TechnicalTask(db.Model):
    """основная сущность"""

    __tablename__= 'technical_task'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True) #uuid первичный ключ
    parent_id = db.Column(UUID(as_uuid=True),db.ForeignKey('technical_task.id', 
                            ondelete='SET NULL'),doc='id предыдущей версии') # ссылка на предыдущую версию
    
    creating_author_id = db.Column(UUID(as_uuid=True),db.ForeignKey('person_info.id', 
                            ondelete='SET NULL'),nullable=True,doc='Создатель записи')
    creating_author = db.relationship('PersonInfo', primaryjoin='TechnicalTask.creating_author_id == PersonInfo.id',
                      foreign_keys='TechnicalTask.creating_author_id',passive_deletes=True)
    
    deleting_author_id = db.Column(UUID(as_uuid=True), db.ForeignKey('person_info.id', ondelete='SET NULL'))
    creating_author = db.relationship('PersonInfo', primaryjoin='TechnicalTask.deleting_author_id == PersonInfo.id',
                foreign_keys='TechnicalTask.deleting_author_id',passive_deletes=True, doc='Удаливший запись')
    organization_id = db.Column(UUID(as_uuid=True),db.ForeignKey('organization.id', 
                                    ondelete='SET NULL'),doc='id организации') #из мониторинга
    organization = db.relationship('Organization', passive_deletes=True, doc='Организация')

    efo_id = db.Column(UUID(as_uuid=True),db.ForeignKey('equipment.id', 
                                        ondelete='SET NULL'),doc='id ЭФО')#из мониторинга
    efo = db.relationship('Equipment', passive_deletes=True, doc='ЭФО')
    
    bg_impact = db.Column(db.String(255), doc='Влияние на БГ') #из мониторинга
    fault_detected_at = db.Column(db.Date, doc='Дата обнаружения неисправности')#из мониторинга
    monitoring_id = db.Column(db.String(255), doc='id записи из Monitoring')#из мониторинга

    created_at = db.Column(db.DateTime, default=datetime.now, doc='Дата создания записи')
    title = db.Column(db.String(255), nullable=False, doc="Название ТЗ")
    status = db.Column(db.String(32), nullable=False, default="INITIALIZED") 
    is_active = db.Column(db.Boolean, nullable = False, default = True, doc = "флаг активной записи") #для текущей версии
    deletion_mark = db.Column(db.Boolean, nullable = False, default = False, server_default = 'false') 


class Organization(db.Model):
    """Организации"""

    __tablename__ = "organization"

    id = db.Column(UUID(as_uuid=True), primary_key=True)
    
    org_type = db.Column(db.String(255), nullable = True, doc = 'Тип организации (Изготовитель или ЭксплуатирующаяОрганизация)')
    org_title = db.Column(db.String(255), nullable=False, doc="Наименование организации")
    

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

    organization_id = db.Column(UUID(as_uuid=True), db.ForeignKey('organization.id',
                            ondelete='SET NULL')) #Если организация меняется, человек как запись может остаться.
    organization = db.relationship('Organization',passive_deletes=True, doc='Войсковая часть')
    
    department = db.Column(db.String(255), doc='Подразделение')
    position = db.Column(db.String(255), doc='Должность')
    rank = db.Column(db.String(255), doc='Звание')
    full_name = db.Column(db.String(255), doc='Фамилия Имя Отчество')
    status = db.Column(db.String(255), doc='Статус')
    is_active = db.Column(db.Boolean, default=True, doc='флаг активной записи')

class TechnicalTaskPerson(db.Model):
    """Личный состав для создания ТЗ"""
    __tablename__ = 'technical_task_person'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = db.Column(UUID(as_uuid=True), db.ForeignKey('technical_task.id', ondelete='CASCADE'), 
                        nullable=False, doc='id ТЗ')
    task = db.relationship('TechnicalTask', passive_deletes = True, doc = 'ТЗ')

    person_id = db.Column(UUID(as_uuid=True), db.ForeignKey('person_info.id', ondelete='RESRTICT'),
                          nullable=False, doc='id человека')
    person = db.relationship('PersonInfo', passive_deletes=True, doc='Человек')

    role = db.Column(db.String(64), nullable=False, doc='роль человека в ТЗ')
    
    



    
