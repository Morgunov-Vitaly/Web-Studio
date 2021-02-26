import os
from sys import platform
from datetime import datetime


def get_settings_file():
    return os.path.abspath(os.path.join(get_project_dir(), 'settings.toml'))


def get_file_name_with_datetime_prefix(base_name):
    return get_datetime_prefix('-', '-') + base_name


def get_logs_full_path_with_datetime_prefix(filename):
    return get_full_filename(get_correct_path_to_folder('Logs'), get_file_name_with_datetime_prefix(filename))


def get_screenshots_full_path_with_datetime_prefix(filename):
    return get_full_filename(get_correct_path_to_folder('Screenshots'), get_file_name_with_datetime_prefix(filename))


def get_correct_full_logs_path(filename):
    return get_full_filename(get_correct_path_to_folder('Logs'), filename)


def get_correct_path_to_folder(folder_name):
    return os.path.abspath(os.path.join(get_project_dir(), folder_name))


def get_correct_path_separator():
    return os.sep


def get_current_directory():
    return os.curdir


def get_full_filename(path, filename):
    return str(os.path.normpath(path) + get_correct_path_separator() + filename)


def get_datetime_prefix(data_delimiter='-', time_delimiter=':'):
    now = datetime.now()
    return f"{now.year}{data_delimiter}{now.month}{data_delimiter}" \
           f"{now.day}_{now.hour}{time_delimiter}{now.minute}{time_delimiter}{now.second}"


def get_geckodriver_path():
    if platform.startswith("win32"):
        # Windows32
        return os.path.abspath(os.path.join(get_project_dir(), r'Geckodriver\win32\geckodriver.exe'))
    elif platform.startswith("cygwin"):
        # Windows/Cygwin
        return os.path.abspath(os.path.join(get_project_dir(), r'Geckodriver\win64\geckodriver.exe'))
    else:
        # linux, OS X
        return os.path.abspath(os.path.join(get_project_dir(), 'Geckodriver/linux/geckodriver'))


def normalise_path(filename):
    return os.path.abspath(filename)


def get_project_dir():
    # return os.path.join(os.getcwd(), os.curdir) #Ok
    # return os.path.abspath(os.curdir) # Ok
    return os.path.abspath(os.getcwd())
