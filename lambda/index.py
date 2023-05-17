import requests
import json

def handler(event, context):
    URL = "https://httpbin.org/get"
    HEADERS = {
        "accept": "application/json",
    }

    r = requests.get(URL, headers=HEADERS)
    print(r.status_code)
    print(r.json())

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps(r.json(), indent=4, sort_keys=True),
    }