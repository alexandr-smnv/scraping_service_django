import json
import os
import sys

from django.contrib.auth import get_user_model

proj = os.path.dirname(os.path.abspath('manage.py'))
sys.path.append(proj)

os.environ["DJANGO_SETTINGS_MODULE"] = 'core.settings'

import django
django.setup()

from scraping.utils.parsers import hh_parser, superjob_parser
from scraping.models import Vacancy, City, Language, Error, Url

# автоматическое получение авторизованного пользователя
User = get_user_model()

# список парсеров
parsers = (
    (hh_parser, 'hhru'),
    (superjob_parser, 'superjob'),
)


# параметры для парсинга из предпочтений пользователей
def get_settings():
    # .values() возвращает список словарей
    qs = User.objects.filter(send_email=True).values()
    # формирование кортежа ('city_id', 'language_id') из данных о пользователе
    settings_lst = set((q['city_id'], q['language_id']) for q in qs)
    return settings_lst


def get_urls(_settings):
    qs = Url.objects.all().values()
    # формирование объекта { ('city_id', 'language_id'): {'hhru': 'url', ... }
    url_dct = {(q['city_id'], q['language_id']): q['url_data'] for q in qs}
    urls = []
    for pair in _settings:
        tmp = {
            'city': pair[0],
            'language': pair[1],
            'url_data': url_dct[pair]
        }
        urls.append(tmp)
    return urls


settings = get_settings()
url_list = get_urls(settings)

import time
start = time.time()
vacancy = []
errors = []

for data in url_list:
    city = City.objects.get(id=data['city'])
    language = Language.objects.get(id=data['language'])
    for func, key in parsers:
        url = data['url_data'][key]
        v, e = func(url, [data['city'], str(city)], [data['language'], str(language)])
        vacancy += v
        errors += e

print(time.time()-start)

for job in vacancy:
    try:
        print(job)
        v = Vacancy(**job)
        v.save()
    except:
        print('Ошибка при записи в БД')

if errors:
    try:
        er = Error(data=errors)
        er.save()
    except:
        print('Ошибка при записи в БД')


with open('vacancies.json', 'w', encoding='utf-8') as file:
    json.dump(vacancy, file, indent=4, ensure_ascii=False)
