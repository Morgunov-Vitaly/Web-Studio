import dynaconf
from App.Exceptions.AdsManager.AdAccountIdNotFound import AdAccountIdNotFound
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from App.Exceptions.AdsManager.AdsManagerAccessTokenNotFound import AdsManagerAccessTokenNotFound
from App.Exceptions.AdsManager.BrowserFormElementNotFound import BrowserFormElementNotFound
from time import sleep

from App.Exceptions.AdsManager.RequestFromBmToAdsManagerFault import RequestFromBmToAdsManagerFault
from App.Exceptions.AdsManager.UserIdNotFound import UserIdNotFound
from App.Services.PathService import Path
from App.Services.FacebookGraphService import FacebookGraphService


class AccountController:
    def __init__(self, log, driver_path, email, password, number_of_inactive_ad_account):
        # Параметры пользователя
        self.email = email
        self.password = password
        self.access_token = ''
        self.user_id = ''
        self.username = ''

        self.number_of_inactive_ad_account = number_of_inactive_ad_account

        # Внедренные зависимости
        self.path = Path()
        self.log = log

        # Опции работы программы
        self.sleep_time = int(dynaconf.settings.SLEEP_TIME)
        self.facebook_url = dynaconf.settings.FACEBOOK_URL
        self.inactive_accounts_limit = dynaconf.settings.INACTIVE_ACCOUNTS_LIMIT_NOTIFICATION

        # Browser settings
        self.options = Options()
        # Опция отвечает за фоновый режим работы браузера
        self.options.headless = bool(dynaconf.settings.HIDE_BROWSER)
        self.options.binary_location = Path.get_browser_location()

        try:
            self.browser = webdriver.Firefox(executable_path=driver_path, firefox_options=self.options)
        except Exception as err:
            raise SystemExit(f'Check the Firefox location option BROWSER_LOCATION in settings! {err}')

    def get_ad_manager_access_token(self):
        self.log.debug('***Trying to login Facebook.com...***')

        self.browser.get(self.facebook_url)
        self.browser.implicitly_wait(self.sleep_time)
        # sleep(self.sleep_time)

        # Авторизация на https://www.facebook.com
        self.log.debug('Facebook Opened')

        # "email"
        email_field = self.browser.find_element_by_id(dynaconf.settings.LOGIN_FORM_EMAIL_FIELD)

        repeats = 0
        while not email_field and repeats < 3:
            sleep(self.sleep_time)
            # повторная попытка найти элемент "email"
            email_field = self.browser.find_element_by_id(dynaconf.settings.LOGIN_FORM_EMAIL_FIELD)
            repeats += 1

        if not email_field:
            self.log.debug('Закрываем браузер..')
            self.browser.quit()
            raise SystemExit(f'Возникли проблемы с загрузкой страницы с формой входа!')

        email_field.send_keys(self.email)
        self.log.debug('Email passed')

        # "pass"
        password_field = self.browser.find_element_by_id(dynaconf.settings.LOGIN_FORM_PASSWORD_FIELD)
        password_field.send_keys(self.password)
        self.log.debug('Password passed')

        # Ищем кнопку submit разными способами

        # Альтернативный способ 1st element with name = "login":
        submit = self.browser.find_elements_by_name('login')[0]
        if not submit:
            # deprecated for now  "u_0_d"
            submit = self.browser.find_element_by_id(dynaconf.settings.LOGIN_FORM_SUBMIT_BUTTON)
            if not submit:
                # Иногда это работает, иногда - нет
                submit = self.browser.find_element_by_id("u_0_b")
                if not submit:
                    by_xpath = "//button[(@type='submit') and (@name = 'login')]"
                    submit = self.browser.find_element_by_xpath(by_xpath)
                    if not submit:
                        # Давно устаревший способ
                        submit = self.browser.find_element_by_id("loginbutton")

        if not submit:
            self.log.debug('Закрываем браузер..')
            self.browser.quit()
            raise BrowserFormElementNotFound("Could not find a Submit button element on the form")

        submit.click()
        self.log.debug('Signed In')

        # Getting User Access Token
        self.log.debug('***Trying to get an access token...***')
        sleep(self.sleep_time)

        # Переходим в кабинет рекламодателя Ads manager account
        # В качестве альтернативы можно использовать https://www.facebook.com/adsmanager/manage/
        self.browser.get(f'{self.facebook_url}/ads/manager/')

        # X seconds to make sure Ads Manager loaded successfully
        sleep(self.sleep_time)

        access_token = self.browser.execute_script("return window.__accessToken;")

        if not access_token:
            self.log.debug('Закрываем браузер..')
            self.browser.quit()
            raise AdsManagerAccessTokenNotFound("User: {}. Access Token not found!".format(self.email))

        self.log.debug("User: {} AdsAccessToken has been found successfully!".format(self.email))
        # self.log.access_token("User: {} | AdsAccessToken: {}".format(self.email, access_token))

        return access_token

    def process_request_from_bm_to_ads_manager(self, ad_account, ad_account_id):
        self.log.debug('***Sending BM request to the Ads Manager...***')
        post_body = {
            'adaccount_id': f'act_{ad_account_id}',
            'permitted_tasks': "['MANAGE','ADVERTISE','ANALYZE']",
        }
        adding_ads_to_business = ad_account.send_post_request(post_body)
        print(adding_ads_to_business)

        while adding_ads_to_business.get("access_status") != "PENDING":
            # Что-то пошло не так...
            error_object = adding_ads_to_business.get("error")
            error_message = error_user_title = error_user_msg = ''

            if error_object:
                error_message = error_object.get("message") or ''
                error_user_title = error_object.get("error_user_title") or ''
                error_user_msg = error_object.get("error_user_msg") or ''
            self.log.error(f'Ошибка: {error_message} - {error_user_title} : {error_user_msg}')
            x = input('Проверьте статусы запросов в BM аккаунте. '
                      'При необходимости отмените непринятые приглашения. '
                      'После устранения причины ошибки - введите "c" для продолжения '
                      'или "s" для прекращения работы скрипта...')
            if x.lower() == 's':
                if adding_ads_to_business.get("access_status") != "PENDING":
                    self.log.debug('Закрываем браузер..')
                    self.browser.quit()
                    raise SystemExit(f'Проблема с аккаунтом BM так и не была устранена. Завершаю работу программы...')
            self.log.debug('***Повторная попытка отправить BM request to the Ads Manager...***')
            # Повторный запрос...
            adding_ads_to_business = ad_account.send_post_request(post_body)
            print(adding_ads_to_business)

        self.log.debug('BM Request is sent to the Ads Manager successfully')
        self.log.debug('***Trying to accept the request...***')

        self.browser.get(
            f'{self.facebook_url}/ads/manager/account_settings/information/?act={ad_account_id}')
        sleep(self.sleep_time)

        # Делаем скриншот экрана браузера
        # self.browser.save_screenshot(self.path.get_screenshots_path('_accept_request.png'))

        # Look up the business manager request
        element = self.browser.find_element_by_css_selector(dynaconf.settings.CONFIRM_REQUEST_BUTTON)
        repeats = 0
        while not element and repeats < 3:
            sleep(self.sleep_time)
            # повторная попытка найти элемент 'a._42ft'
            element = self.browser.find_element_by_css_selector(dynaconf.settings.CONFIRM_REQUEST_BUTTON)
            repeats += 1

        if not element:
            raise RequestFromBmToAdsManagerFault(f'Не удалось найти кнопку (элемент '
                                                 f'{dynaconf.settings.CONFIRM_REQUEST_BUTTON}) '
                                                 f'для подтверждения запроса!')
        # Кликаем по кнопке
        element.click()

        # Opening Modal Window and accepting the request
        sleep(self.sleep_time)
        request_accepting_link = self.browser.find_element_by_css_selector(
            dynaconf.settings.CONFIRM_REQUEST_LINK).get_attribute('href')
        repeats = 0
        while not request_accepting_link and repeats < 3:
            sleep(self.sleep_time)
            # повторная попытка найти элемент '._3m_7 > a:nth-child(1)'
            request_accepting_link = self.browser.find_element_by_css_selector(
                dynaconf.settings.CONFIRM_REQUEST_LINK).get_attribute('href')
            repeats += 1

        if not request_accepting_link:
            # Делаем скриншот экрана браузера
            # self.browser.save_screenshot(self.path.get_screenshots_path('_modal_accept_link.png'))
            raise RequestFromBmToAdsManagerFault(f'Не удалось найти ссылку для подтверждения запроса!'
                                                 f' Элемент {dynaconf.settings.CONFIRM_REQUEST_LINK}')

        print(request_accepting_link)
        # Переходим по ссылке подтверждения
        self.browser.get(request_accepting_link)

        # Done
        self.log.debug('The request accepted successfully!')
        self.log.successfully_accepted_user(
            f'User: {self.username} | {self.email} | Ad Account Id: {ad_account_id} request accepted successfully!')

    def request_to_add_user_account_to_bm(self):
        self.access_token = self.get_ad_manager_access_token()
        # self.browser.implicitly_wait(5)

        # Получаем данные рекламного аккаунта с помощью Facebook Graph API
        # Создаем экземпляр класса FacebookGraphService
        ad_account = FacebookGraphService(self.access_token)

        # Получим ID пользователя
        self.log.debug('***Getting UserId...***')
        response = ad_account.get_user_id()
        print(response)
        if 'id' not in response:
            self.log.debug('Закрываем браузер..')
            self.browser.quit()
            raise UserIdNotFound(f'User: {self.email} ID not found!')

        self.user_id = response['id']
        self.username = response.get('name') or ''
        self.log.debug(f'User: {self.username} {self.email} ID={self.user_id} has been found successfully!')

        # Получить список рекламных аккаунтов
        self.log.debug('***Getting list of User Ad accounts...***')
        ads_accounts = ad_account.get_user_ad_accounts(self.user_id)
        print(ads_accounts)

        if 'data' not in ads_accounts:
            self.log.debug('Закрываем браузер..')
            self.browser.quit()
            raise AdAccountIdNotFound(f'User: {self.username} {self.email}. '
                                      f'There is no Ads Manager on this Facebook account')
        self.log.debug(f'The list of User {self.username} {self.email} Ad accounts has been found successfully!')

        # Обход списка рекламных аккаунтов
        for ads_account in ads_accounts['data']:
            # Проверка статуса аккаунта(ов)
            self.log.debug(f"***Checking AdAccount {ads_account['id']} Status...***")

            if not ad_account.is_ad_account_active(ads_account['account_id']):
                self.log.inactive_account(
                    'User: {} {} | AdAccountId: {}'.format(self.username, self.email, ads_account['id']))
                self.log.warning(
                    f'User: {self.username} {self.email} AdAccount: {ads_account["id"]} is INACTIVE!')
                self.number_of_inactive_ad_account += 1
                self.log.debug(f'Общее кол-во обнаруженных неактивных аккаунтов: {self.number_of_inactive_ad_account}')
                if self.number_of_inactive_ad_account >= self.inactive_accounts_limit:
                    self.log.warning(
                        f'Кол-во обнаруженных неактивных рекламных аккаунтов клиентов '
                        f'достигло лимита ({self.inactive_accounts_limit})!:'
                        f' {self.number_of_inactive_ad_account}'
                    )
                    input('Смените IP и нажмите Enter чтобы продолжить!')
                    self.log.debug('Обнуляю счетчик...')
                    self.number_of_inactive_ad_account = 0

                continue

            # Аккаунт активен! Настраиваем его и отправляем запрос на добавление под управление BM
            self.log.debug(
                f'User: {self.username} {self.email} '
                f'AdAccount: {ads_account["account_id"]} is active! '
                f'Status code: {ad_account.get_ad_account_status(ads_account["account_id"])}')

            # Сhanging of timezone and currency
            self.log.debug('***Updating currency and timezone...***')
            ads_payload = {
                'currency': 'USD',
                'timezone_id': 116,
                'access_token': self.access_token,
            }
            updating_request = ad_account.update_ad_account_data(ads_account['account_id'], ads_payload)
            print(updating_request)

            # Sending BM request
            # Отправка запроса Ads Manager'у от BM на добавление рекламного аккаунта в его управление
            try:
                self.process_request_from_bm_to_ads_manager(ad_account, ads_account['account_id'])
            except RequestFromBmToAdsManagerFault as err:
                self.log.error(err)
                continue

        # Закрываем браузер
        self.log.debug('Закрываем браузер..')
        self.browser.quit()
        return self.number_of_inactive_ad_account
