import json


def cred():
    with open("credentials.json", 'r') as file:
        data = file.read()
        obj = json.loads(data)

    return {'api_id': obj['api_id'],
            'api_hash': obj['api_hash'],
            'bot_token': obj['bot_token'],
            'db_string': obj['db_string']}
