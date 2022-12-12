import json
import os
import sys

from django.db import DatabaseError

proj = os.path.dirname(os.path.abspath('manage.py'))
sys.path.append(proj)

os.environ["DJANGO_SETTINGS_MODULE"] = 'core.settings'

import django
django.setup()

from scraping.utils.parsers import hh_parser
from scraping.models import Vacancy, City, Language, Error

city = City.objects.get(slug='sankt-peterburg')
language = Language.objects.get(slug='python')


parsers = (
    (hh_parser, 'https://api.hh.ru/vacancies'),
)

vacancy = []
errors = []
for func, url in parsers:
    v, e = func(url)
    vacancy += v
    errors += e

for job in vacancy:
    try:
        v = Vacancy(**job, city=city, language=language)
        v.save()
    except DatabaseError():
        print('Ошибка при записи в БД')

if errors:
    try:
        er = Error(data=errors)
        er.save()
    except DatabaseError():
        print('Ошибка при записи в БД')


with open('vacancies.json', 'w', encoding='utf-8') as file:
    json.dump(vacancy, file, indent=4, ensure_ascii=False)
