import os
import sys
import datetime
from dotenv import load_dotenv


from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives


proj = os.path.dirname(os.path.abspath('manage.py'))
sys.path.append(proj)
os.environ["DJANGO_SETTINGS_MODULE"] = 'core.settings'

import django
django.setup()

from scraping.models import Vacancy, Error
from core.settings import EMAIL_HOST_USER

# Дата отправки
today = datetime.date.today()

ADMIN_USER = os.getenv('ADMIN_USER')

# Заголовок письма
subject = f'Рассылка вакансий за { today }'
text_content = f'Рассылка вакансий { today }'
from_email = EMAIL_HOST_USER

# Пустое сообщение
empty = '<h2>К сожалению на сегодня по Вашим предпочтениям данных нет</h2>'


User = get_user_model()
# получение всех пользователей согласившихся на рассылку
# [{'city': 1, 'language': 1, 'email': em@email.com}, ... ]
qs = User.objects.filter(send_email=True).values('city', 'language', 'email')

# {(1, 1): ['email1@com', 'email2@com'], ...}
users_dct = {}
for i in qs:
    users_dct.setdefault((i['city'], i['language']), [])
    users_dct[(i['city'], i['language'])].append(i['email'])

if users_dct:
    # параметры для фильтрации вакансий
    # {'city_id__in': [1, 2, 1], 'language_id__in': [1, 1, 2]
    params = {'city_id__in': [], 'language_id__in': []}

    for pair in users_dct.keys():
        params['city_id__in'].append(pair[0])
        params['language_id__in'].append(pair[1])
    # фильтрация вакансий по заданным параметрам
    qs = Vacancy.objects.filter(**params).values()[:30]
    print(qs)

    # vacancies { (city_id, language_id): вакансии..., (): вакансии...}
    vacancies = {}
    for i in qs:
        vacancies.setdefault((i['city_id'], i['language_id']), [])
        vacancies[(i['city_id'], i['language_id'])].append(i)

    for keys, emails in users_dct.items():
        # получение вакансий по (city_id, language_id)
        rows = vacancies.get(keys, [])
        html = ''
        # формирование сообщения
        for row in rows:
            html += f'<h5><a href="{ row["url"] }">{ row["title"] }"</a></h5>'
            html += f'<p>{row["description"]}</p>'
            html += f'<p>{row["company"]}</p><br><hr>'
        _html = html if html else empty

        # отправка пользователю списка вакансий
        for email in emails:
            to = email
            msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
            msg.attach_alternative(_html, "text/html")
            msg.send()


# проверка наличия ошибок и отправка их
qs_error = Error.objects.filter(timestamp=today)
if qs_error.exists():
    error = qs_error.first()
    data = error.data
    _html = ''
    for i in data:
        _html += f'<p><a href="{ i["url"] }">Error" { i["title"] }"</a></p>'
    subject = f"Ошибки парсинга на {today}"
    text_content = "Ошибки парсинга"
    to = ADMIN_USER
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(_html, "text/html")
    msg.send()
