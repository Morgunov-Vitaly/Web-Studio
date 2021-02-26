
# Facebook Ads Manager BM request 
## Как запустить версию с GUI:
1. Запустите приложение.
2. Проверьте что все настройки на вкладке Настройки - корректны
3. Укажите путь до файла с дланными аккаунтов пользователей на главной вкладке
4. Нажмите кнопку Старт для запуска скрипта
5. Просмотрите логи в консоле во время выполнения и в папке Logs

## Как запустить консольную версию:
Приложение представлено в двух вариантах - скрипт Python3 а также исполняемый .exe файл

##### Для работы софта необходимо:
1. Установить Mozilla Firefox. Софт использует Selenium Headless Webdriver
этого браузера, что бы снизить риск определения софта как automation tool Facebook-ом. 
https://www.mozilla.org/en-US/firefox/new/

2. Настроить конфигурационный файл settings.toml в корневой папке софта.

3. Прописать исходные данные клиентов access.txt (email; password)

4. (для версии .exe) Скопировать geckodriver и настроить пути
   
5. (для .py версии) Установить Python не ниже 3.8.2
https://www.python.org/downloads/release/python-382/


#### Запуск на Linux, MacOS
python run.py

#### Windows
run.exe

### Настройка ПК (Windows)
Папку со скриптом положить в корень диска С

Назвать ее facebook-api в нее же закинуть geckodriver https://github.com/mozilla/geckodriver/releases

Закинуть в корень диска С в папку geckodriver

Установить mozilla https://www.mozilla.org/en-US/firefox/new/

Добавить в среды окружения переменную path и прописать в ней значения:
<pre>C:\facebook-api;C:\geckodriver</pre>

#### Установка Python
Установить питон https://www.python.org/downloads/release/python-382/

Добавить в среды окружения переменную path и прописать в ней значения:
<pre>C:\Users\Admin\AppData\Local\Programs\Python\Python38\Scripts\;C:\Users\Admin\AppData\Local\Programs\Python\Python38\;</pre>

### Подготовка BM Facebook
Ссылка на инструкцию:
https://docs.google.com/document/d/1NZ9xAIdFKxndZSKS_VyydkcxmqsvqtRWfqrqIL6ZByM/edit?usp=sharing

### Обновление User Access Token
Детали User Access Token BM, на котором работает софт(использует Facebook SDK)
https://developers.facebook.com/tools/debug/accesstoken/?access_token=<ACCESS_TOKEN_FROM_settings.toml>

### В случае бана БМ
1. Создать новый акк Facebook с BM'ом
2. Зарегать Developer-ский app на https://developers.facebook.com
3. Скопировать ACCESS TOKEN, вставить его в ссылку(вместо <ACCESS_TOKEN>) и перейти по ней
https://developers.facebook.com/tools/debug/accesstoken/?access_token=<ACCESS_TOKEN>
4. Получить Long Term Access Token.
5. Скопировать значения APP_ID, APP_SECRET, ACCESS_TOKEN, BUSINESS_ID в settings.toml

### Принцип работы скрипта
1. Парсим файл с данными клиентов accs.txt - вычленяем имейл и пароль
2. С помощью Selenium + Geckodriver имитируем вход пользователя в аккаунт facebook.com
3. Получаем access_token (с помощью JS скрипта window.__accessToken) и user_id с помощью Facebook Graph API
4. Получаем список рекламных аккаунтов для данного пользователя
5. Проходим циклом по списком рекламных аккаунтов и выполняем ряд действий:
    1) проверяем статус рекламного аккаунта
    2) если аккаунт неактивен - увеличиваем счетчик оповещения о превышении обнаружения неактивных аккаунтов 
       и переходим к следующей итерации. Если превышен лимит счетчика - выводим сообщение с просьюой поменять IP  
    3) если статус рекламного аккаунта активный, то выполняем ряд действий:
        - меняем настроики валюты и часового пояса
        - отправляем запрос на добавление рекламного аккаунта под управление BM (бизнес-менеджера)
        - с помощью Selenium + Geckodriver загружаем страницу настроек /ads/manager/account_settings/information/,
          находим запрос бизнес-менеджера находим кнопку по css селектору 'a._42ft' и кликаем на нее. 
        - Открывается модальное окно, мы находим элемент по css селектору '._3m_7 > a:nth-child(1)' копируем из него 
          ссылку
        - Переходим по скопированной ссылке    
