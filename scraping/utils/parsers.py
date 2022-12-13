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

    city_id = 1 # по умолчанию Москва

    for k in getAreas():
        if k[1] == city:
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
        js_obj = json.loads(getPage(language, city_id, page))

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
                'city': js_obj.get('area').get('name'),
                'language': language
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


