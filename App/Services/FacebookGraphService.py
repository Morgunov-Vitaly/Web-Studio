# Класс для работы с аккаунтом Facebook  с помощью Facebook Graph API
from App.Exceptions.AdsManager.AdAccountStatusNotFound import AdAccountStatusNotFound
import requests
import dynaconf


class FacebookGraphService:
    def __init__(self, access_token):
        self.access_token = access_token

        self.payload = {"access_token": dynaconf.settings.ACCESS_TOKEN}
        self.facebook_graph_api = dynaconf.settings.FACEBOOK_GRAPH_URL
        self.business_id = dynaconf.settings.BUSINESS_ID

    # Status of the account.
    # 1 = Active
    # 2 = Disabled
    # 3 = Unsettled
    # 7 = Pending Review
    # 9 = In Grace Period
    # 101 = temporarily unavailable
    # 100 = pending closure
    def get_ad_account_status(self, ad_account_id):
        # Загружаем данные аккаунта
        ads_payload = {"access_token": self.access_token,
                       "fields": ["account_status"]}
        response = requests.get(f'{self.facebook_graph_api}/act_{ad_account_id}', params=ads_payload).json()
        if 'account_status' not in response:
            raise AdAccountStatusNotFound('AdAccountID: {} status not found!'.format(ad_account_id))

        return response['account_status']

    def is_ad_account_active(self, ad_account_id):
        return self.get_ad_account_status(ad_account_id) == 1

    def get_user_id(self):
        ads_payload = {"access_token": self.access_token}
        return requests.get(f'{self.facebook_graph_api}/me', params=ads_payload).json()

    def get_user_ad_accounts(self, user_id):
        ads_payload = {"access_token": self.access_token}
        return requests.get(f'{self.facebook_graph_api}/{user_id}/adaccounts', params=ads_payload).json()

    def update_ad_account_data(self, ad_account_id, ads_payload):
        updating_request = requests.post(f'{self.facebook_graph_api}/act_{ad_account_id}', params=ads_payload).json()
        return updating_request

    def send_post_request(self, post_body):
        adding_ads_to_business = requests.post(f'{self.facebook_graph_api}/{self.business_id}/client_ad_accounts',
                                               params=self.payload,
                                               data=post_body).json()
        return adding_ads_to_business
