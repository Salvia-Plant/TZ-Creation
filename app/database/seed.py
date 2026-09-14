
from app import db
from app.database.models import RoleInfo


def roles():

    roles = [
        {   "id": "11111111-1111-1111-1111-111111111111",
            "name": "Руководитель",
            "code": "leader"
        },
        {   "id": "11111111-1111-1111-1111-111111111222",
            "name": "Офицер специальной службы",
            "code": "special_service_officer"
        },
        {   "id": "11111111-1111-1111-1111-111111111333",
            "name": "Офицер подготовки данных",
            "code": "data_preparation_officer"
        },
        {   "id": "11111111-1111-1111-1111-111111111444",
            "name": "Офицер сопровождения",
            "code": "support_officer"
        },
        {   "id": "11111111-1111-1111-1111-111111111555",
            "name": "Состав выездного расчёта",
            "code": "field_team"
        }
    ]

    for role_data in roles:
        role = RoleInfo.query.filter_by(code=role_data["code"]).first()
        if role is None:
            role = RoleInfo(id=role_data["id"],name=role_data["name"],code=role_data["code"])
            db.session.add(role)

    db.session.commit()