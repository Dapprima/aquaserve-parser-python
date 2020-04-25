from lxml import etree
from requests import request
import re
from os import listdir
from os.path import isfile, join

from base import clear_text


class Parser:

    def __init__(self, url):
        self.response = request(method="GET", url=url)
        self.html = etree.HTML(self.response.content)
        self.text = self.response.text

    def expr_result(self, expr_type, expr, multy, prefix):
        value = None
        try:
            if expr_type == "xpath":
                if not multy:
                    value = clear_text(self.html.xpath(expr)[0])
                    if prefix:
                        value = prefix + value
                else:
                    if prefix:
                        value = [prefix + val for val in self.html.xpath(expr)]
                    else:
                        value = self.html.xpath(expr)

            if expr_type == "regex":
                if not multy:
                    value = re.search(expr, self.text)[0]
                    if prefix:
                        value = prefix + value
                else:
                    if prefix:
                        value = [prefix + val for val in re.findall(expr, self.text)]
                    else:
                        value = re.findall(expr, self.text)
        except Exception as e:
            print("{error} error in expr_result".format(error=e))
        finally:
            return value

    def use_field(self, field):
        local_field = dict()
        required = field.xpath("./@required")[0] == 'True' if True else False
        field_name = field.xpath("./@name")[0]
        expr_type = field.xpath("./@type")[0]
        expr = clear_text(field.xpath("./text()")[0])
        multy = field.xpath("./@multy")[0] == 'True' if True else False
        prefix = field.xpath("./@prefix")[0]

        value = self.expr_result(expr_type, expr, multy, prefix)

        # Якщо поле яке є обов'язковим не знайдено змінюємо шаблон
        if required and not value:
            return False
        else:
            local_field[field_name] = value
            return local_field

    def use_template(self, template):
        page_info = dict()
        xml = open(template, "rb").read()
        tree = etree.fromstring(xml)
        fields = tree.xpath("//field")

        for field in fields:
            value = self.use_field(field)

            if not value:
                return value

            page_info.update(value)
        # Тут потрібно зберігати результат в базу даннх і повертати статус
        # щоб припинити чи продовжити роботу з шаблонами поки що я просто повертаю інформацію
        return page_info

    def load_templates(self, path):
        templates = [path+f for f in listdir(path) if isfile(join(path, f))]

        for template in templates:
            info = self.use_template(template)
            print(info)
            if not info:
                # Якщо шаблоне підходить пробуємо новий
                continue
            else:
                # Якщо шаблон підійшов припиняемо
                break


# Запити для тесту
"""
    Запит на сторінку для конкретного міста:
        response = request(method="GET", url='https://www.aquaverve.com/state-water-cooler-delivery/alabama/roanoke.html')
    Запит на сторінку для конкретного штату:
        response = request(method="GET", url='https://www.aquaverve.com/state-water-cooler-delivery/alabama/index.html')
    Запит на сторінку до головної сторінки:
        response = request(method="GET", url='https://www.aquaverve.com/state-water-cooler-delivery/index.html')
"""

# Опції шаблону
"""
    required - опція яка відповідає за обов'язковість поля
    type - тип парсингу regex чи xpath
    name - им'я поля 
    multy - результат у вигляди масива
    prefix - модифікатор для отриманих даних 
"""

if __name__ == '__main__':
    parser = Parser(url='https://www.aquaverve.com/state-water-cooler-delivery/alabama/roanoke.html')
    # Перебираємо шаблони для сайту
    parser.load_templates('templates/aquaverve/')