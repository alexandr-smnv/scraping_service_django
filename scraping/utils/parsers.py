import requests      # Для запросов по API
import json          # Для обработки полученных результатов
import time          # Для задержки между запросами


def hh_parser(url):
    # Результирующий список вакансий
    vacancy = []
    errors = []

    # список со ссылками на вакансии
    job_urls = []

    # Получение страницы с вакансиями
    def getPage(keyword, page_number=0):
        """
        Создаем метод для получения страницы со списком вакансий.
        Аргументы:
            page - Индекс страницы, начинается с 0. Значение по умолчанию 0, т.е. первая страница
        """

        # Справочник для параметров GET-запроса
        params = {
            'text': keyword,  # Текст фильтра. В имени должно быть слово "Язык программирования"
            'area': 2,  # Поиск осуществляется по вакансиям города Санкт-Петербург
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
        js_obj = json.loads(getPage('Python', page))

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
                # 'city': jsonObj.get('area').get('name'),
                # 'language': 'Python'  # исправить на входные параметры
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


