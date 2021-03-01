from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QDir
from PyQt5.QtWidgets import QFileDialog

from App.Resources.ui import Ui_MainWindow
from App.Services import SourceParserService
from App.Services.FBAccountsService import FBAccountsService
import App.Services.PathService as Path
import App.Services.UiDialogsService as UiDialog


class AppWindowService(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, log, settings):
        super().__init__()
        self.setupUi(self)
        # main_window.show()

        # Dependency injection
        self.log = log
        # Внедряем сервис и инициализируем настройки
        self.settings_service = settings
        self.settings_service.set_settings_fields(self)

        self.set_event_listeners()

        # Путь до geckodriver
        self.driver_path = Path.get_geckodriver_path()
        if not self.driver_path:
            self.log.error('Geckodriver path not defined!')
            raise SystemExit('Geckodriver path not defined!')

        self.log.debug(f'Установлен путь geckodriver: {self.driver_path}')

        # Важные переменные
        self.access_token_aborted_requests = 0
        self.number_of_inactive_ad_account = 0
        self.fault_access_limit = int(
            self.settings_service.settings['default']['ACCESS_TOKEN_GETTING_FAULTS_LIMIT_NOTIFICATION']
        )

    def set_event_listeners(self):
        # Открыть диалог поиска файла с исходными данными пользователей
        self.accountsFilenameButton.clicked.connect(self.get_accounts_filename)

        # Открыть диалог поиска файла браузера
        self.browserLocationButton.clicked.connect(self.get_browser_location)

        # Запуск скрипта
        self.startScriptButton.clicked.connect(self.start_scrypt_event)

    def start_scrypt_event(self):
        self.settings_service.update_settings_from_fields(self)
        if self.settings_service.is_settings_changed:
           self.settings_service.save_settings_to_file()
           self.settings_service.is_settings_changed = False
        self.statusbar.showMessage('Script started')
        self.start()

    # Обновление поля с именем файла исходных даннфх пользователей с помощью диалога поиска файла
    def get_accounts_filename(self):
        dialog = QFileDialog(directory=Path.get_project_dir())
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.setFilter(QDir.Files)

        if dialog.exec_():
            file_name = dialog.selectedFiles()
            if file_name[0].endswith('.txt'):
                self.accountsFilenametInput.setText(file_name[0])

    # Обновление поля пути к браузеру с помощью диалога поиска файла
    def get_browser_location(self):
        dialog = QFileDialog(directory=Path.get_project_dir())
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.setFilter(QDir.Files)

        if dialog.exec_():
            file_name = dialog.selectedFiles()
            self.browserLocationInput.setText(file_name[0])

    def closeEvent(self, event):
        self.settings_service.update_settings_from_fields(self)
        if self.settings_service.is_settings_changed:
            self.statusbar.showMessage('Свойства были изменены')
            reply = QtWidgets.QMessageBox.information(self, 'Выход', 'Сохранить настройки перед выходом?',
                                                      QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                                      QtWidgets.QMessageBox.Yes)
            if reply == QtWidgets.QMessageBox.Yes:
                self.settings_service.save_settings_to_file()
                event.accept()
            else:
                event.accept()
        else:
            reply = QtWidgets.QMessageBox.information(self, 'Выход', 'Вы точно хотите выйти?',
                                                      QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                                      QtWidgets.QMessageBox.No)
            if reply == QtWidgets.QMessageBox.Yes:
                self.settings_service.save_settings_to_file()
                event.accept()
            else:
                event.ignore()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()

    def start(self):
        self.log.debug('**** Запуск скрипта... ****')

        # Парсим файл с данными пользователей
        with open(self.settings_service.settings['default']['ACCOUNTS_FILENAME'], 'r') as f:
            for line in f.read().splitlines():
                if not line.strip():
                    continue

                self.log.debug('*** Определяем нового пользователя... ***')
                divider = SourceParserService.get_divider(line)
                print(f'Divider: "{divider}"')

                if not divider:
                    print(line)
                    self.log.error('Произошла ошибка при попытке распарсить строку с исходными данными пользователя. '
                                   'Разделитель не определен.')
                    continue
                line = line.split(divider)

                password = ''

                email = str(line[0]).strip()
                self.log.debug('email: ' + email)

                if len(line) >= 2:
                    password = str(line[1]).strip()
                    self.log.debug('password: ' + password)
                    # Возможно тут нужно делать более глубокий парсинг uid? line[-1].split(':')[-1]
                    # но тогда предыдущее значение это что - id? чего?

                    if len(line) >= 3:
                        uid = str(line[2]).strip()
                        self.log.debug('uid:' + uid)

                if (not email) or (not password):
                    self.log.error('User {} data is not complete'.format(email))
                    continue

                try:
                    user_account = FBAccountsService(self.log, self.settings_service, self.driver_path, email, password,
                                                     self.number_of_inactive_ad_account)
                    self.number_of_inactive_ad_account = user_account.request_to_add_user_account_to_bm()
                except Exception as err:
                    self.log.error(err)
                    self.access_token_aborted_requests += 1

                    self.log.debug(f'Кол-во неудачных попыток: {self.access_token_aborted_requests}')

                    if self.access_token_aborted_requests >= self.fault_access_limit:
                        detailed_text = f'Кол-во неудачных попыток получения access_token клиента ' \
                                        f'достигло лимита ({self.fault_access_limit})!:' \
                                        f' {self.access_token_aborted_requests}'
                        self.log.warning(detailed_text)
                        message = f'Кол-во неудачных попыток: {self.access_token_aborted_requests}'
                        informative_text = 'Смените IP и нажмите Ok чтобы продолжить или Abort, ' \
                                           'чтобы завершить работу скрипта!'
                        x = UiDialog.abort_continue_notification_dialog(
                            message,
                            informative_text,
                            detailed_text)
                        if x == self.settings_service.abort_button_code:
                            self.log.error(f'Пользователь завершил работу скрипта.')
                            raise SystemExit('The End')

                        self.log.debug('Обнуляю счетчик неудачных попыток...')
                        self.access_token_aborted_requests = 0

                    continue

            UiDialog.pause_continue_notification_dialog('Нажмите Ok чтобы чтобы завершить работу программы!')
            raise SystemExit('The end')
