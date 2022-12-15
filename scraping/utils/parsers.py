import requests      # Для запросов по API
import json          # Для обработки полученных результатов
import time          # Для задержки между запросами


def hh_parser(url, city, language):
    # Результирующий список вакансий
    vacancy = []
    errors = []

    # список со ссылками на вакансии
    job_urls = []

    # Получение городов
    def getAreas():
        try:
            req = requests.get('https://api.hh.ru/areas')
            data = req.content.decode()
            req.close()
            jsObj = json.loads(data)
            rus = []
            # Получение страны Россия
            for obj in jsObj:
                if obj.get('id') == '113':
                    rus = obj.get('areas')

            # список кортежей ('id', 'Город')
            areas = []

            def recurse(area_list):
                for area in area_list:
                    if len(area.get('areas')) > 0:
                        areas.append((area.get('id'), area.get('name')))
                        recurse(area.get('areas'))
                    else:
                        areas.append((area.get('id'), area.get('name')))

            recurse(rus)

            return areas

        except requests.exceptions.HTTPError as error:
            print("Http Error:", error)
            errors.append({'url': url, 'error': error})
        except requests.exceptions.ConnectionError as error:
            print("Error Connecting:", error)
            errors.append({'url': url, 'error': error})
        except requests.exceptions.Timeout as error:
            print("Timeout Error:", error)
            errors.append({'url': url, 'error': error})
        except requests.exceptions.RequestException as error:
            print("OOps: Something Else", error)
            errors.append({'url': url, 'error': error})


    city_id = None

    for k in getAreas():
        if k[1] == city[1]:
            city_id = k[0]

    # Получение страницы с вакансиями
    def getPage(keyword, area, page_number=0):
        """
        Создаем метод для получения страницы со списком вакансий.
        Аргументы:
            page - Индекс страницы, начинается с 0. Значение по умолчанию 0, т.е. первая страница
        """

        # Справочник для параметров GET-запроса
        params = {
            'text': keyword,  # Текст фильтра. В имени должно быть слово "Язык программирования"
            'area': area,  # Поиск осуществляется по вакансиям города Санкт-Петербург
            'page': page_number,  # Номер страницы поиска на HH
            'per_page': 100,  # Кол-во вакансий на 1 странице
            'search_field': 'name'
        }
        try:
            res = requests.get(url, params)  # Запрос к API
            res_data = res.content.decode()  # Декодируем его ответ, чтобы Кириллица отображалась корректно
            res.close()
            return res_data
        except requests.exceptions.HTTPError as error:
            print("Http Error:", error)
            errors.append({'url': url, 'error': error})
        except requests.exceptions.ConnectionError as error:
            print("Error Connecting:", error)
            errors.append({'url': url, 'error': error})
        except requests.exceptions.Timeout as error:
            print("Timeout Error:", error)
            errors.append({'url': url, 'error': error})
        except requests.exceptions.RequestException as error:
            print("OOps: Something Else", error)
            errors.append({'url': url, 'error': error})

    # Считываем первые 2000 вакансий
    for page in range(0, 20):
        # Преобразуем текст ответа запроса в справочник Python
        js_obj = json.loads(getPage(language[1], city_id, page))

        # Формируем список ссылок на каждую вакансию
        for obj in js_obj.get('items'):
            job_urls.append(obj.get('url'))

        # Проверка на последнюю страницу, если вакансий меньше 2000
        if (js_obj['pages'] - page) <= 1:
            break

    count = 0
    len_jobs = len(job_urls)
    # Проходимся по ссылкам с вакансиями и получаем необходимые данные
    for url in job_urls:
        try:
            req = requests.get(url)
            data = req.content.decode()
            js_obj = json.loads(data)
            req.close()

            vacancy.append({
                'title': js_obj.get('name'),
                'url': js_obj.get('alternate_url'),
                'company': js_obj.get('employer').get('name'),
                'description': js_obj.get('description'),
                'city_id': city[0],
                'language_id': language[0]
            })
            count += 1
            print(f'{count} из {len_jobs} вакансий записана')
            time.sleep(0.25)

        except requests.exceptions.HTTPError as error:
            print("Http Error:", error)
            errors.append({'url': url, 'error': error})
        except requests.exceptions.ConnectionError as error:
            print("Error Connecting:", error)
            errors.append({'url': url, 'error': error})
        except requests.exceptions.Timeout as error:
            print("Timeout Error:", error)
            errors.append({'url': url, 'error': error})
        except requests.exceptions.RequestException as error:
            print("OOps: Something Else", error)
            errors.append({'url': url, 'error': error})

    return vacancy, errors


def superjob_parser(url, city, language):
    # Результирующий список вакансий
    vacancy = []
    errors = []

    headers = {
        'X-Api-App-Id': 'v3.r.133423322.00a4eea925b648b578e5f1dab4c5e513a9c1732b.d8ab8ceb7c9f1b18cb0f5f0fdace9cc6967536b9'
    }

    def getCity(city_title):
        try:
            params = {
                'all': True,
            }
            res = requests.get(f'{url}/towns/', params=params)
            data = res.content.decode()
            res.close()
            city_objects = json.loads(data).get('objects')
            city_id = None

            for city_object in city_objects:
                if city_object.get('title') == city_title:
                    city_id = city_object.get('id')
                    break

            return city_id

        except requests.exceptions.HTTPError as error:
            print("Http Error:", error)
            errors.append({'url': url, 'error': error})
        except requests.exceptions.ConnectionError as error:
            print("Error Connecting:", error)
            errors.append({'url': url, 'error': error})
        except requests.exceptions.Timeout as error:
            print("Timeout Error:", error)
            errors.append({'url': url, 'error': error})
        except requests.exceptions.RequestException as error:
            print("OOps: Something Else", error)
            errors.append({'url': url, 'error': error})

    def get_all_objects():
        all_objects = []
        """
        Создаем метод для получения страницы со списком вакансий.
        Аргументы:
            page - Индекс страницы, начинается с 0. Значение по умолчанию 0, т.е. первая страница
        """
        # Справочник для параметров GET-запроса

        params = {
            'town': getCity(city[1]),
            'keywords': [1, 'or', language[1]],
            'page': 0,
        }

        while True:
            try:
                res = requests.get(f'{url}/vacancies/', params=params, headers=headers)  # Посылаем запрос к API
                data = res.content.decode()  # Декодируем его ответ, чтобы Кириллица отображалась корректно
                vacancies = json.loads(data).get('objects')
                all_objects.extend(vacancies)
                res.close()
                params['page'] += 1
                if len(vacancies) < 20:
                    break

            except requests.exceptions.HTTPError as error:
                print("Http Error:", error)
                errors.append({'url': url, 'error': error})
            except requests.exceptions.ConnectionError as error:
                print("Error Connecting:", error)
                errors.append({'url': url, 'error': error})
            except requests.exceptions.Timeout as error:
                print("Timeout Error:", error)
                errors.append({'url': url, 'error': error})
            except requests.exceptions.RequestException as error:
                print("OOps: Something Else", error)
                errors.append({'url': url, 'error': error})

        return all_objects

    for vac in get_all_objects():

        vacancy.append({
            'title': vac.get('profession'),
            'url': vac.get('link'),
            'company': vac.get('client').get('title'),
            'description': vac.get('vacancyRichText'),
            'city_id': city[0],
            'language_id': language[0]  # исправить на входные параметры
        })

    print('Количество собранных вакансий:', len(vacancy))

    # Запись в json
    with open('vacancies.json', 'w', encoding='utf-8') as file:
        json.dump(vacancy, file, indent=4, ensure_ascii=False)

    return vacancy, errors
