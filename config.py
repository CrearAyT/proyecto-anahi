import os
import json


CONF = os.path.join(os.path.dirname(__file__), 'settings')
__data = {}

def load():
    fh = open(CONF, 'rw')
    try:
        __data = json.loads(fh.read())
    except ValueError:
        __data = {}
    fh.close()

def get(modname):
    if modname not in __data:
        __data[modname] = {}

    return __data[modname]

def save():
    fh = open(CONF, 'w')
    json_data = json.dumps(__data, sort_keys=True, indent=4)
    fh.write(json_data + "\n")

