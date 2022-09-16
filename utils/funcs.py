import http.client
import yaml
import pathlib
import json

class Params:
    def __init__(self, config_file):
        self.config_file = config_file
        self.config = Params.read_config_yml()
        self.api_type = self.config['api_type']
        self.api_key = self.config['api_key']
        self.api_host = self.config['api_host']
        self.lat = self.config['default_lat']
        self.lon = self.config['default_lon']
        self.criteria = self.config['criteria']
        self.max_distance = self.config['max_distance']
    def read_config_yml():
        with open("config.yml", 'r') as ymlfile:
            cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)
        return cfg

class call_api:
    'Return unparsed JSON from X-Plane API'
    def __init__(self, api_type, lat, lon, api_key, api_host):
        self.api_type = api_type
        self.lat = lat
        self.lon = lon
        self.api_key = api_key
        self.api_host = api_host
        self.nearby_traffic = self.get_nearby_traffic()
    def get_nearby_traffic(self):
        if self.api_type == "X-Plane":
            api_return = get_nearby_traffic_xplane(self.lat, self.lon, self.api_key, self.api_host)
        elif self.api_type == "openaip":
            print("OpenAIP API not yet implemented")
        else:
            print("Invalid API type")
        return api_return


def get_nearby_traffic_xplane(lat, lon, api_key, api_host):
    conn = http.client.HTTPSConnection(str(api_host))
    headers = {
    'X-RapidAPI-Key': str(api_key),
    'X-RapidAPI-Host': str(api_host)
    }
    request_string = "/api/aircraft/json/lat/" + str(lat) + "/lon/" + str(lon) + "/dist/25/"
    conn.request("GET", request_string, headers=headers)

    res = conn.getresponse()
    data = res.read()
    decoded = data.decode("utf-8")
    planes = json.loads(decoded)
   # planes = planes["ac"]
    return planes

def filter_planes(api_return, params):
    max_distance = params.max_distance
    planes = json.loads(api_return)['ac']
    filtered_planes = []
    if params.criteria == 'mil':
        criteria_key = 'mil'
        criteria_value = 1
    elif params.criteria == 'civil':
        criteria_key = 'mil'
        criteria_value = 0
    elif params.criteria == 'all':
        criteria_key = None
    else:
        print("Invalid criteria")
    # loop through all planes
    for plane in planes:
        # loop through all criteria
        if criteria_key == None:
            if float(plane['dst']) <= float(max_distance):
                filtered_planes.append(plane)
        else:
            if float(plane['dst']) <= float(max_distance) and plane[criteria_key] == criteria_value:
                filtered_planes.append(plane)
    print("Found " + str(len(filtered_planes)) + " planes")
    return filtered_planes