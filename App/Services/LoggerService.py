from App.Services.PathService import Path
import logging


class OneLineExceptionFormatter(logging.Formatter):
    def formatException(self, exc_info):
        """
        Format an exception so that it prints on a single line.
        """
        result = super(OneLineExceptionFormatter, self).formatException(exc_info)
        return repr(result)  # or format into one line however you want to

    def format(self, record):
        s = super(OneLineExceptionFormatter, self).format(record)
        if record.exc_text:
            s = s.replace('\n', '') + '|'
        return s


class Log:
    def __init__(self):
        self.path = Path()

        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)
        f = OneLineExceptionFormatter('%(asctime)s|%(levelname)s|%(message)s',
                                      '%Y-%m-%d %H:%M:%S')

        # to log debug messages
        self.debug_log = logging.FileHandler(self.path.get_logs_path_with_datetime(' debug.log'), 'w', 'utf-8')
        self.debug_log.setLevel(logging.DEBUG)
        self.debug_log.setFormatter(f)

        # to log errors
        self.error_log = logging.FileHandler(self.path.get_logs_path_with_datetime(' error.log'), 'w', 'utf-8')
        self.error_log.setLevel(logging.ERROR)
        self.error_log.setFormatter(f)

        self.logger.addHandler(self.debug_log)
        self.logger.addHandler(self.error_log)

    def debug(self, message):
        self.logger.debug(message)
        print(message)

    def warning(self, message):
        self.logger.warning(message)
        print(message)

    def error(self, message):
        self.logger.error(message)
        print(message)

    def inactive_account(self, message):
        file = open(self.path.get_logs_path(" inactive-accounts.log"), "a")
        file.write(str(message) + '\n')
        file.close()

    def successfully_accepted_user(self, message):
        file = open(self.path.get_logs_path(" successfully-accepted-users"), "a")
        file.write(str(message) + '\n')
        file.close()
