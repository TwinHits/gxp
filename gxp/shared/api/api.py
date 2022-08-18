import requests


class Api:
    session = requests.session()

    def get(url, headers=None):
        response = requests.get(url, headers=headers)
        body = response.json()
        return body

    def post(url, data=None, headers=None, json=None):
        response = requests.post(url, data=data, headers=headers, json=json)
        if response.status_code == requests.codes.ok:
            return response.json()
        else:
            print(response.status_code)
