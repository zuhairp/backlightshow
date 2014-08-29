import json

import requests

COLOR_DB_FILE = 'colors.json'

color_database = None

def __init_db():
    global color_database
    color_database = json.load(open(COLOR_DB_FILE))

def search_online(color_name):
    service_url = "http://www.colourlovers.com/api/colors"
    options = {'format':'json', 'numResults':1, 'keywords':color_name}
    response = requests.get(service_url, params=options)
    data = response.json() # Only returning 1 item

    if len(data) == 0:
        return None

    return data[0]['hex']

def get_rgb_by_name(color_name, raise_exception=False):
    return hex_to_rgb(get_hex_by_name(color_name, raise_exception))

def get_hex_by_name(color_name, raise_exception=False):
    global color_database
    if color_database is None:
        __init_db()
    
    #
    # Lowercase color_name and and strip surrounding quotes
    #
    color_name = color_name.lower()
    if color_name[0]=='"' and color_name[-1]=='"':
        color_name = color_name[1:-1]
    if color_name[0]=="'" and color_name[-1]=="'":
        color_name = color_name[1:-1]


    if color_name not in color_database:
        online_color = search_online(color_name)
        if online_color is None:
            if raise_exception: raise Exception("Color does not exist")
            else: return None
        color_database[color_name] = online_color
        with open(COLOR_DB_FILE, 'w') as database_file:
            json.dump(color_database, database_file) # Concurrency not supported ;-) 

    return color_database[color_name]

def hex_to_rgb(hex_color):
    red, green, blue = [int(hex_color[i:i+2], 16) for i in range(0, len(hex_color), 2)]
    return red, green, blue

def rgb_to_hex(red, green, blue):
    return "#%02X%02X%02X" % (red, green, blue)
		





