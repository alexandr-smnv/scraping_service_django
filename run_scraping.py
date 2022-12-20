import asyncio
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
    # (hh_parser, 'hhru'),
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
    print(_settings)
    for pair in _settings:
        tmp = {}
        tmp['city'] = pair[0]
        tmp['language'] = pair[1]
        tmp['url_data'] = url_dct[pair]
        urls.append(tmp)
    return urls


async def main(value):
    func, url, city, language = value
    job, err = await loop.run_in_executor(None, func, url, city, language)
    errors.extend(err)
    vacancy.extend(job)

settings = get_settings()
url_list = get_urls(settings)

vacancy = []
errors = []

loop = asyncio.get_event_loop()
tmp_tasks = []

for data in url_list:
    city = City.objects.get(id=data['city'])
    language = Language.objects.get(id=data['language'])
    for func, key in parsers:
        tmp_tasks.append((func, data['url_data'][key], [data['city'], str(city)], [data['language'], str(language)]))

tasks = asyncio.wait([loop.create_task(main(f)) for f in tmp_tasks])

loop.run_until_complete(tasks)
loop.close()

# for data in url_list:
#     city = City.objects.get(id=data['city'])
#     language = Language.objects.get(id=data['language'])
#     for func, key in parsers:
#         url = data['url_data'][key]
#         v, e = func(url, [data['city'], str(city)], [data['language'], str(language)])
#         vacancy += v
#         errors += e

# for job in vacancy:
#     try:
#         print(job)
#         v = Vacancy(**job)
#         v.save()
#     except:
#         print('Ошибка при записи в БД')
#
# if errors:
#     try:
#         er = Error(data=errors)
#         er.save()
#     except:
#         print('Ошибка при записи в БД')


with open('vacancies.json', 'w', encoding='utf-8') as file:
    json.dump(vacancy, file, indent=4, ensure_ascii=False)
