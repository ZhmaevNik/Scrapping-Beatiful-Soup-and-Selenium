# Scrapping-Beatiful-Soup-and-Selenium
Данный проект создан в учебных целях, он позволяет парсить вопросы и правильные ответы к ним с сайта https://tests24.su/ для подготовки к сдаче экзаменов в Ростехнадзоре.

## Краткое описание работы программы
Для работы кода нужно заполнить две переменные:
вставляем ссылку на страницу с выбором билетов (раздел), пример:
```url_page_tickets = 'https://tests24.su/b-2-4-burenie-neftyanyh-i-gazovyh-skvazhin/' ```

вставляем начало ссылки на каждый билет(паттерн) без номера билета, пример:
```url_ticket_pattern = 'https://tests24.su/b-2-4-bilet' ```

Программа переходит по адресу указанному в ```url_page_tickets``` и записывает все ссылки с паттерном ```url_ticket_pattern```, далее с помощью парсера BeautifulSoup и Selenium производится проход по ссылкам, и записываются правильные ответы на вопросы на последней странице билета, данную информацию записываем в файл Excel.

## Установка
Для корректной работы программы необходимо установить все пакеты согласно файлу requirements.txt:
```
pip install -r requirements.txt
```
В коде используется webdriver.Chrome для корректной работы необходимо загрузить соответсвующую версию веб драйвера с сайта:
https://chromedriver.chromium.org/downloads

положить драйвер или в корень с проектом, или указать иной путь:
```
driver = webdriver.Chrome(executable_path="chromedriver.exe", options=chrome_options)
```