import requests
class VkInfo:
    def __init__(self, token):
        self.token = token
        self.base_url = 'https://api.vk.com/method/'
        self.params_default = {
            'access_token': self.token,
            'v': '5.131'
        }

    def execute_method(self, method, params):
        url = self.base_url + method
        params.update(self.params_default)
        return requests.get(url, params=params)