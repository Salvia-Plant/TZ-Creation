from app import db
from sqlalchemy.dialects.postgresql import UUID 
import uuid
from datetime import date

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
    deleting_author = db.relationship('PersonInfo', primaryjoin='TechnicalTask.deleting_author_id == PersonInfo.id',
                foreign_keys='TechnicalTask.deleting_author_id',passive_deletes=True, doc='Удаливший запись')
    organization_ref = db.Column(UUID(as_uuid=True),doc='id организации') #из мониторинга

    efo_ref = db.Column(UUID(as_uuid=True),doc='id ЭФО')#из мониторинга
    
    combat_impact = db.Column(db.Boolean, doc='Влияние на боевую готовность') #из мониторинга
    malfunction_time = db.Column(db.DateTime, doc='Дата обнаружения неисправности')#из мониторинга
    measurement_id = db.Column(UUID(as_uuid=True), doc='id записи из Monitoring')#из мониторинга

    number = db.Column(db.String(32), doc='Номер ТЗ')
    creation_date = db.Column(db.Date, default=date.today, doc='Дата создания записи')
    status = db.Column(db.String(32), nullable=False) 
    is_active = db.Column(db.Boolean, nullable = False, default = True, doc = "флаг активной записи") #для текущей версии
    deletion_mark = db.Column(db.Boolean, nullable = False, default = False, server_default = 'false') 


class Organization(db.Model):
    """Организации"""

    __tablename__ = "organization"

    id = db.Column(UUID(as_uuid=True), primary_key=True)
    parent_id = db.Column(UUID(as_uuid=True), doc='id родителя')
    org_type = db.Column(db.String(255), doc= 'Тип организации (Изготовитель или Эксплуатирующая Организация)')
    org_title = db.Column(db.String(255), nullable=False, doc="Наименование организации")

    children = db.relationship('Organization', primaryjoin=parent_id == id, foreign_keys=id,
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

    organization_id = db.Column(UUID(as_uuid=True)) #Если организация меняется, человек как запись может остаться.
    
    department = db.Column(db.String(255), doc='Подразделение')
    position = db.Column(db.String(255), doc='Должность')
    rank = db.Column(db.String(255), doc='Звание')
    full_name = db.Column(db.String(255), doc='Фамилия Имя Отчество')


class TaskPerson(db.Model):
    """Личный состав для создания ТЗ"""
    __tablename__ = 'task_person'

    id = db.Column(UUID(as_uuid=True), primary_key=True)
    task_id = db.Column(UUID(as_uuid=True), db.ForeignKey('technical_task.id', ondelete='CASCADE'), 
                        nullable=False, doc='id ТЗ')
    task = db.relationship('TechnicalTask', passive_deletes = True, doc = 'ТЗ')

    person_id = db.Column(UUID(as_uuid=True), db.ForeignKey('person_info.id', ondelete='RESTRICT'),
                          nullable=False, doc='id человека')
    person = db.relationship('PersonInfo', passive_deletes=True, doc='Человек')

    role = db.Column(db.String(64), nullable=False, doc='роль человека в ТЗ')
    
    



    
