import os
from sys import platform
from datetime import datetime

import dynaconf


class Path:
    def __init__(self):
        self.screenshots_path = os.path.abspath(os.path.join(Path.get_project_dir(), 'Screenshots'))
        self.log_path = os.path.abspath(os.path.join(Path.get_project_dir(), 'Logs'))

    @staticmethod
    def get_project_dir():
        # return os.path.join(os.getcwd(), os.curdir) #Ok
        # return os.path.abspath(os.curdir) # Ok
        return os.path.abspath(os.getcwd())

    @staticmethod
    def get_sep():
        return os.sep

    @staticmethod
    def get_curdir():
        return os.curdir

    @staticmethod
    def get_full_filename(path, filename):
        return str(os.path.normpath(path) + Path.get_sep() + filename)

    @staticmethod
    def get_datetime_prefix(data_delimiter='-', time_delimiter=':'):
        now = datetime.now()
        return f"{now.year}{data_delimiter}{now.month}{data_delimiter}" \
               f"{now.day}_{now.hour}{time_delimiter}{now.minute}{time_delimiter}{now.second}"

    @staticmethod
    def get_geckodriver_path():
        if platform.startswith("win32"):
            # Windows32
            return os.path.abspath(os.path.join(Path.get_project_dir(), r'Geckodriver\win32\geckodriver.exe'))
        elif platform.startswith("cygwin"):
            # Windows/Cygwin
            return os.path.abspath(os.path.join(Path.get_project_dir(), r'Geckodriver\win64\geckodriver.exe'))
        else:
            # linux, OS X
            return os.path.abspath(os.path.join(Path.get_project_dir(), 'Geckodriver/linux/geckodriver'))

    @staticmethod
    def get_browser_location():
        return os.path.abspath(dynaconf.settings.BROWSER_LOCATION)

    def get_datetime_file_name(self, base_name):
        return self.get_datetime_prefix('-', '-') + base_name

    def get_logs_path_with_datetime(self, filename):
        return Path.get_full_filename(self.log_path, self.get_datetime_file_name(filename))

    def get_logs_path(self, filename):
        return Path.get_full_filename(self.log_path, filename)

    def get_screenshots_path(self, filename):
        return Path.get_full_filename(self.screenshots_path, self.get_datetime_file_name(filename))
