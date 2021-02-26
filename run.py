from App.Controller.AccountController import AccountController
from App.Services import SourceParserService
from App.Services.LoggerService import Log
import dynaconf
from App.Services.PathService import Path

if __name__ == '__main__':

    # Кол-во неудачных попыток добавления рекламных аккаунтов клиентов в аккаунт BM
    access_token_aborted_requests = 0
    number_of_inactive_ad_account = 0
    fault_access_limit = dynaconf.settings.ACCESS_TOKEN_GETTING_FAULTS_LIMIT_NOTIFICATION

    log = Log()
    log.debug('**** ЗАПУСК СКРИПТА... ****')

    driver_path = Path.get_geckodriver_path()
    log.debug('Defined geckodriver path: ' + driver_path)
    if not driver_path:
        log.error('Geckodriver path not defined!')
        raise SystemExit('Geckodriver path not defined!')

    with open(dynaconf.settings.ACCOUNTS_FILENAME, 'r') as f:
        for line in f.read().splitlines():
            if not line.strip():
                continue

            log.debug('*** ОПРЕДЕЛЯЕМ НОВОГО ПОЛЬЗОВАТЕЛЯ... ***')
            divider = SourceParserService.get_divider(line)
            print(f'Divider: "{divider}"')

            if not divider:
                print(line)
                log.error('Произошла ошибка при попытке распарсить строку с исходными данными пользователя. '
                          'Разделитель не определен.')
                continue
            line = line.split(divider)

            password = uid = ''

            email = str(line[0]).strip()
            log.debug('email: ' + email)

            if len(line) >= 2:
                password = str(line[1]).strip()
                log.debug('password: ' + password)
                # Возможно тут нужно делать более глубокий парсинг uid? line[-1].split(':')[-1]
                # но тогда предыдущее значение это что - id? чего?

                if len(line) >= 3:
                    uid = str(line[2]).strip()
                    log.debug('uid:' + uid)

            if (not email) or (not password):
                log.error('User {} data is not complete'.format(email))
                continue

            try:
                user_account = AccountController(log, driver_path, email, password, number_of_inactive_ad_account)
                number_of_inactive_ad_account = user_account.request_to_add_user_account_to_bm()
            except Exception as err:
                log.error(err)
                access_token_aborted_requests += 1

                log.debug(f'Кол-во неудачных попыток: {access_token_aborted_requests}')

                if access_token_aborted_requests >= fault_access_limit:
                    log.warning(
                        f'Кол-во неудачных попыток получения access_token клиента '
                        f'достигло лимита ({fault_access_limit})!:'
                        f' {access_token_aborted_requests}'
                    )
                    input('Смените IP и нажмите Enter чтобы продолжить!')
                    log.debug('Обнуляю счетчик неудачных попыток...')
                    access_token_aborted_requests = 0
                continue

        input('Press Enter button to close the console app')
        raise SystemExit('The end')
