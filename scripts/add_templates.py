import requests
import os
import sys

sys.path.insert(0, os.path.dirname(os.getcwd())) #корень проекта чтобы импортировтаь app

from app.config import AppConfig

config = AppConfig()

TEMPLATE_IDENTIFIER = "TZ_na_ustranenie_neispravnosti"
TEMPLATE_NAME = "ТЗ на устранение неисправности"

def add_template():

    path_templates = os.path.dirname(os.getcwd())
    path_templates = os.path.join(path_templates, 'templates')

    template_path = os.path.join(path_templates,TEMPLATE_IDENTIFIER + '.odt')
    try:
        with open(template_path, "rb") as file:
            req = requests.post("http://{address}/DAFDAPI/templates".format(address=config.DAFD_ADDRESS),
                data={"name": TEMPLATE_NAME},files={"file": file})
        if req.ok and req.text:
            pass
        else:
            if req.text!= 'Повторяющееся имя шаблона':
                print(req.text)
                raise Exception("Ошибка при загрузке шаблона")

        #получаем ref загруженного шаблона
        answer = requests.get("http://{address}/DAFDAPI/templates/search/{identifier}".format(
                address=config.DAFD_ADDRESS,
                identifier=TEMPLATE_IDENTIFIER))

        template_ref = answer.json().get("ref")
        if template_ref is None:
            raise Exception("Не удалось получить ref шаблона из ДАФД")

        print("Шаблон найден")
        print("ref:", template_ref)

    except Exception as ex:
        print(ex)

if __name__ == "__main__":
    add_template()