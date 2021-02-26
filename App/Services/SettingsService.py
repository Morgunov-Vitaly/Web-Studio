import toml
from PyQt5 import QtWidgets
import App.Services.PathService as Path


class SettingsService:
    def __init__(self, log):
        # Dependency injection
        self.log = log

        self.abort_button_code = 262144

        # Путь к файлу настроек
        self.settings_file = Path.get_settings_file()

        # Читаем настройки из файла
        self.settings = self.get_settings_from_file()

        # Флаг изменения настроек пользователем
        self.is_settings_changed = False

        self.settings_map = {
            'appIdInput': 'APP_ID',
            'appSecretInput': 'APP_SECRET',
            'accessTokenInput': 'ACCESS_TOKEN',
            'bMAccountIdtInput': 'BUSINESS_ID',
            'accountsFilenametInput': 'ACCOUNTS_FILENAME',
            'sleepTimeIdInput': 'SLEEP_TIME',
            'hideBrowserCheckBox': 'HIDE_BROWSER',
            'browserLocationInput': 'BROWSER_LOCATION',
            'accessTokenFaultsLimitInput': 'ACCESS_TOKEN_GETTING_FAULTS_LIMIT_NOTIFICATION',
            'inactiveAccountsLimitNotificationInput': 'INACTIVE_ACCOUNTS_LIMIT_NOTIFICATION',
            'facebookGraphUrlInput': 'FACEBOOK_GRAPH_URL',
            'facebookUrlInput': 'FACEBOOK_URL',
            'loginFormEmailFieldInput': 'LOGIN_FORM_EMAIL_FIELD',
            'loginFormPasswordFieldInput': 'LOGIN_FORM_PASSWORD_FIELD',
            'loginFormSubmitButtonInput': 'LOGIN_FORM_SUBMIT_BUTTON',
            'confirmRequestButtonInput': 'CONFIRM_REQUEST_BUTTON',
            'confirmRequestLinkInput': 'CONFIRM_REQUEST_LINK'
        }

    @staticmethod
    def get_checkbox_state(state):
        # 0 - Unchecked
        # 1 - PartiallyChecked
        # 2 - Checked
        if state or state == 1 or str(state).lower() == 'true':
            return 2
        return 0

    def get_settings_from_file(self):
        try:
            settings = toml.load(self.settings_file)
        except Exception as err:
            self.log.error(err)
            raise SystemExit(f'Программа завершилась с ошибкой: {err}')
        return settings

    def update_settings_from_fields(self, fields):
        # Обходим все поля и считываем параметры - заносим в словарь настроек используя карту сопоставлений
        for element in self.settings_map:
            setting_name = self.settings_map[element]

            if type(getattr(fields, element)) == QtWidgets.QLineEdit:
                value = getattr(fields, element).text()
            elif type(getattr(fields, element)) == QtWidgets.QPlainTextEdit:
                value = getattr(fields, element).toPlainText()
                # print('QTextEdit')
                # print(value)
            elif type(getattr(fields, element)) == QtWidgets.QCheckBox:
                # 0 - Unchecked
                # 1 - PartiallyChecked
                # 2 - Checked
                # value = getattr(self, element).checkState()
                # True
                # False
                value = getattr(fields, element).isChecked()
                # print('QCheckBox:')
                # print(value)
            else:
                value = None

            # Обновляем словарь настроек
            if self.settings['default'][setting_name] != value:
                self.is_settings_changed = True
            self.settings['default'][setting_name] = value

    def set_settings_fields(self, fields):
        # ACCOUNTS_FILENAME
        fields.accountsFilenametInput.setText(self.settings['default']['ACCOUNTS_FILENAME'])
        # BUSINESS_ID
        fields.bMAccountIdtInput.setText(self.settings['default']['BUSINESS_ID'])
        # APP_SECRET
        fields.appSecretInput.setText(self.settings['default']['APP_SECRET'])
        # APP_ID
        fields.appIdInput.setText(self.settings['default']['APP_ID'])
        # ACCESS_TOKEN
        fields.accessTokenInput.setPlainText(self.settings['default']['ACCESS_TOKEN'])
        # BROWSER_LOCATION
        fields.browserLocationInput.setText(self.settings['default']['BROWSER_LOCATION'])
        # HIDE_BROWSER
        fields.hideBrowserCheckBox.setCheckState(self.get_checkbox_state(self.settings['default']['HIDE_BROWSER']))
        # SLEEP_TIME
        fields.sleepTimeIdInput.setText(self.settings['default']['SLEEP_TIME'])
        # ACCESS_TOKEN_GETTING_FAULTS_LIMIT_NOTIFICATION
        fields.accessTokenFaultsLimitInput.setText(
            self.settings['default']['ACCESS_TOKEN_GETTING_FAULTS_LIMIT_NOTIFICATION']
        )
        # INACTIVE_ACCOUNTS_LIMIT_NOTIFICATION
        fields.inactiveAccountsLimitNotificationInput.setText(
            self.settings['default']['INACTIVE_ACCOUNTS_LIMIT_NOTIFICATION'])
        # FACEBOOK_GRAPH_URL
        fields.facebookGraphUrlInput.setText(self.settings['default']['FACEBOOK_GRAPH_URL'])
        # FACEBOOK_URL
        fields.facebookUrlInput.setText(self.settings['default']['FACEBOOK_URL'])
        # LOGIN_FORM_EMAIL_FIELD
        fields.loginFormEmailFieldInput.setText(self.settings['default']['LOGIN_FORM_EMAIL_FIELD'])
        # LOGIN_FORM_PASSWORD_FIELD
        fields.loginFormPasswordFieldInput.setText(self.settings['default']['LOGIN_FORM_PASSWORD_FIELD'])
        # LOGIN_FORM_SUBMIT_BUTTON
        fields.loginFormSubmitButtonInput.setText(self.settings['default']['LOGIN_FORM_SUBMIT_BUTTON'])
        # CONFIRM_REQUEST_BUTTON
        fields.confirmRequestButtonInput.setText(self.settings['default']['CONFIRM_REQUEST_BUTTON'])
        # CONFIRM_REQUEST_LINK
        fields.confirmRequestLinkInput.setText(self.settings['default']['CONFIRM_REQUEST_LINK'])

        fields.statusbar.showMessage('Готово')

    # Сохранение всех параметров в файл
    def save_settings_to_file(self):
        # Сохраняем в файл словарь настроек
        try:
            with open(self.settings_file, 'w') as f:
                toml.dump(self.settings, f)
        except Exception as err:
            self.log.error(err)
            raise SystemExit(f'Программа завершилась с ошибкой: {err}')
        # print(self.settings_service)
