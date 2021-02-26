from App.Services.AppWindowService import AppWindowService
from PyQt5 import QtWidgets
from App.Services.SettingsService import SettingsService

import sys


class ScriptController(object):
    def __init__(self, log):
        # Di
        self.log = log
        self.settings_service = SettingsService(log)

        # Инициализируем GUI
        self.app = QtWidgets.QApplication(sys.argv)
        self.main_window = QtWidgets.QMainWindow()
        self.w = AppWindowService(log, self.settings_service)
        self.w.show()
        sys.exit(self.app.exec_())
