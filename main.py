from typing import List
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from slugify import slugify
from selenium import webdriver, common
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pandas as pd
from bs4 import BeautifulSoup
import requests
import re
import logging
import os


# настраиваем логирование
FORMAT = "%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(f'{__name__}.log', mode='a')
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter(FORMAT)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# глобальные переменные
count: int = 1
title: str = ''

# создание папок
if not os.path.exists('./screenshots'):
    os.mkdir('./screenshots')
if not os.path.exists('./html'):
    os.mkdir('./html')


def func_soup(url: str):
    """
    Принимает строку с url страницы, делает запрос на эту страницу и возвращает объект soup этой страницы
    :param url: str
    :return: object soup
    """
    logger.debug('Начало функции')
    # делаем запрос и получаем html
    html_text = requests.get(url).text

    # используем парсер lxml
    soup = BeautifulSoup(html_text, 'lxml')

    logger.debug('Завершение функции')
    return soup


def scrapping_link_ticket(url_get: str, url_pattern: str) -> List:
    """
    Принимает на вход url страницы и шаблон для поиска ссылок на странице, возвращает список найденных ссылок
    :param url_get: str
    :param url_pattern: str
    :return: List
    """
    logger.debug('Начало функции')

    soup = func_soup(url_get)

    # находим и сохраняем в переменную титул страницы
    global title
    title = slugify(soup.find(class_='entry-title').get_text())

    # находим ссылки на билеты
    all_url = soup.find_all(href=re.compile(url_pattern))
    url_list = [find_url.get('href') for find_url in all_url]

    logger.debug('Завершение функции. Создан список ссылок на билеты')
    return url_list


def scrapping_q_and_a(url: str) -> None:
    """
    Принимает на вход ссылку, парсит данные, сохраняет в файл
    :param url: str
    :return: None
    """
    global count
    logger.debug('Начало функции')

    # настройки драйвера, устанавливаем режим без визуального отображения браузера
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(executable_path="chromedriver.exe", options=chrome_options)

    # ссылка на билет
    driver.get(url)

    # собираем все возможные кнопки выбора ответа(типы радио и чекбокс)
    radio_elements = driver.find_elements(By.XPATH, "//input[@type='radio']")
    checkbox_elements = driver.find_elements(By.XPATH, "//input[@type='checkbox']")
    elements = radio_elements + checkbox_elements

    # указать кол-во циклов=вопросов в билете
    for i in range(200):
        logger.debug(f'Начало цикла № {i + 1}')

        # бежим по возможным ответам и пробуем нажать, если не получается переходим к следующему, ошибку пропускаем
        for e in elements:
            try:
                e.click()
                logger.debug(f'Клик 1 цикла № {i + 1}')
                break
            except common.ElementNotInteractableException as ex:
                pass

        # # скриншот
        # capture_path = f'shot_{i + 1}.png'
        # driver.save_screenshot(capture_path)

        # при нажатии кнопки 'следующий' если происходит исключение(значит последний слайд) нажимаем 'показать ответы'
        try:
            button_element = driver.find_element(By.XPATH, "//input[@type='button'][@value='Следующий >']")
            button_element.click()
            logger.debug(f'Клик 2 цикла № {i + 1}')
        except common.ElementNotInteractableException as ex:
            button_element = driver.find_element(By.XPATH, "//input[@id='action-button']")
            button_element.click()
            logger.debug(f'Завершающий клик, цикл № {i + 1}')
            break

    # таймер для загрузки страницы
    logger.debug(f'Ждем загрузки страницы')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "show-question-choices")))

    # сохраняем html в файл
    page_source = driver.page_source

    # скриншот
    capture_path = f'./screenshots/shot_final_page_{count}.png'
    count += 1
    driver.save_screenshot(capture_path)

    # закрываем браузер
    driver.close()

    logger.debug('Завершение функции')

    with open('./html/temp_data.html', 'w', encoding='utf-8') as td:
        td.write(page_source)


if __name__ == '__main__':
    logger.debug('Начало исполнения кода программы')

    # вставляем ссылку на страницу с выбором билетов (раздел)
    url_page_tickets = 'https://tests24.su/b-2-4-burenie-neftyanyh-i-gazovyh-skvazhin/'
    # вставляем начало ссылки на каждый билет(паттерн) без номера билета
    url_ticket_pattern = 'https://tests24.su/b-2-4-bilet'

    # создаем список ссылок на все билеты раздела
    list_urls = scrapping_link_ticket(url_page_tickets, url_ticket_pattern)

    questions_list = []
    # парсим все вопросы и правильные ответы
    for u in list_urls:
        # получаем html код
        scrapping_q_and_a(u)

        # парсим из кода
        with open("./html/temp_data.html", 'r', encoding='utf-8') as hs:
            data = hs.read()
            soup = BeautifulSoup(data, 'lxml')
        q_and_a = soup.find_all(class_='show-question')
        logger.debug('Собрали данные из кода')

        # наполняем список кортежами с полученными данными
        for i in q_and_a:
            q = i.find('div', class_=re.compile('show-question-content'))
            a = i.find_all('li', class_=re.compile('correct-answer'))
            a = [x.span.get_text() for x in a]
            a = ', '.join(a)
            questions_list.append((q.strong.get_text(), a))
        logger.debug('Наполнили список')

    # создаем датафрейм с данными
    df = pd.DataFrame(questions_list, columns=['Question', 'Answer'])
    logger.debug('Создали датафрейм')

    # импортируем данные в excel
    df.to_excel(f"{title}.xlsx")
    logger.debug('Сохранили данные в Excel')
    logger.debug('Завершение программы')
