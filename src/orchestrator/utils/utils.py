import json
import os

#json notes - json methods expects a python file pointer object to use that path. does not work with string as a path.

def save_json(data, path):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_json(path):
    if not os.path.exists(path):
        return None 
    with open(path,'r',encoding='utf-8') as f:
        return  json.load(f)
    