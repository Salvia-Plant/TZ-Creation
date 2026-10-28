import os
import sys
import requests

# корень проекта, чтобы импортировать app
PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PATH)

from app.config import AppConfig

config = AppConfig()

TEMPLATE_IDENTIFIER = "TZ_na_ustranenie_neispravnosti"
TEMPLATE_NAME = "ТЗ на устранение неисправности"

def add_template():

    templates_path = os.path.join(PATH, "templates")
    template_path = os.path.join(templates_path,TEMPLATE_IDENTIFIER + ".odt")
    try:
        with open(template_path, "rb") as file:
            response = requests.post("http://{address}/DAFDAPI/templates".format(address=config.DAFD_ADDRESS),
                data={"name": TEMPLATE_NAME},files={"file": file})
        if response.ok:
            print("Шаблон успешно загружен в ДАФД")
        elif response.text == "Повторяющееся имя шаблона":
            print("Шаблон уже существует в ДАФД")
        else:
            print(response.text)
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