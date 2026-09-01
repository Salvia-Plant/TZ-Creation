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
    organization_ref = db.Column(UUID(as_uuid=True),db.ForeignKey('organization.id', ondelete='CASCADE'), doc='id организации') #из мониторинга
    organization = db.relationship('Organization', passive_deletes=True)

    efo_ref = db.Column(UUID(as_uuid=True),db.ForeignKey('equipment.id', ondelete='CASCADE'), doc='id ЭФО')#из мониторинга
    efo = db.relationship('Equipment', passive_deletes=True)
    
    combat_impact = db.Column(db.Boolean, doc='Влияние на боевую готовность') #из мониторинга
    malfunction_time = db.Column(db.DateTime, doc='Дата обнаружения неисправности')#из мониторинга
    measurement_id = db.Column(db.Integer,unique=True ,doc='id записи из Monitoring')#из мониторинга
    doc_ref = db.Column(UUID(as_uuid=True), doc='id сгенерированного документа по данному ТЗ')

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
    """Название оборудования (ЭФО)"""

    __tablename__ = "equipment"

    id = db.Column(UUID(as_uuid=True), primary_key=True)
    parent_id = db.Column(UUID(as_uuid=True), doc='id родителя')
    equipment_name = db.Column(db.String(255), nullable=False, doc="Наименование оборудования")
    #technical_tasks = db.relationship("TechnicalTask", back_populates="equipment",passive_deletes=True)
    from_designation = db.Column(db.String(255), doc='обозначение формуляра')
    factory_number = db.Column(db.String(255), default=-1, doc = 'Заводской № продукта')
    esi_id = db.Column(UUID(as_uuid=True), doc='Ссылка на объект из ЭСИ')

    children = db.relationship('Equipment', primaryjoin=parent_id == id, foreign_keys=id,
                               remote_side=parent_id, uselist=True)


class PersonInfo(db.Model):
    """Сведения о должностном лице"""

    __tablename__= 'person_info'

    id = db.Column(UUID(as_uuid=True), primary_key=True)

    organization_id = db.Column(UUID(as_uuid=True), db.ForeignKey('organization.id', ondelete='SET NULL')) #Если организация меняется, человек как запись может остаться.
    organization = db.relationship('Organization', passive_deletes = True, doc='Войсковая часть')
    department = db.Column(db.String(255), doc='Подразделение')
    position = db.Column(db.String(255), doc='Должность')
    rank = db.Column(db.String(255), doc='Звание')
    full_name = db.Column(db.String(255), doc='Фамилия Имя Отчество')
    is_active = db.Column(db.Boolean, default = True, doc = 'Флаг активной записи для ЛС')



class TaskPerson(db.Model): #Какой человек в каком ТЗ в какой роли участвует?
    """Личный состав для создания ТЗ"""

    __tablename__ = 'task_person'

    id = db.Column(UUID(as_uuid=True), primary_key=True)
    task_id = db.Column(UUID(as_uuid=True), db.ForeignKey('technical_task.id', ondelete='CASCADE'), 
                        nullable=False, doc='id ТЗ')
    task = db.relationship('TechnicalTask', passive_deletes = True, doc = 'ТЗ')

    person_id = db.Column(UUID(as_uuid=True), db.ForeignKey('person_info.id', ondelete='RESTRICT'),
                          nullable=False, doc='id человека')
    person = db.relationship('PersonInfo', passive_deletes=True, doc='Человек')

    role_id = db.Column(UUID(as_uuid=True),db.ForeignKey('role_info.id', 
                            ondelete='RESTRICT'),nullable=False, doc='id роли')
    role = db.relationship('RoleInfo', passive_deletes = True, doc='роль')


class RoleInfo(db.Model):
    """Роли для личного состава в ТЗ"""

    __tablename__ = 'role_info'


    id = db.Column(UUID(as_uuid=True), primary_key=True)
    name = db.Column(db.String(255), nullable=False, doc='Наименование Роли')
    code = db.Column(db.String(64), nullable=False, unique=True, doc='Код роли') # для нас с катей



    
