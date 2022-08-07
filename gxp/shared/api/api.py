import requests

class Api:
    session = requests.session()
    
    def get(url, headers=headers):
        response = requests.get(url, headers=headers);
        body = response.json()
        return response

    def post(url, body):
        response = requests.post(url, body, headers=headers);
        body = response.json()
        return response