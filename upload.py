import requests
import json

def post_data(url, attendance):
    headers = {'Content-type': 'application/json'}
    response = None
    try:
        response = requests.post(url, data = json.dumps(attendance), headers = headers, timeout=5)
        print(response.status_code)
        print(response.content)
    except Exception as ex:
        print(ex.__str__())
        return 0
    else:
        if response is not None and response.status_code == 200:
            return 1
        return 0
