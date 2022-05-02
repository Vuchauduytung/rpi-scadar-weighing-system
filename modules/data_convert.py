import json

def json2dict(path):
    with open(path) as json_file:
        data = json.load(json_file)
    return data