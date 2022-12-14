import http.client
from multiprocessing.connection import wait
import time
import yaml
import pathlib
import json
import pandas as pd
import sqlite3 as sql
import os
import subprocess
import random
import re
import datetime

class Params:
    def __init__(self, config_file):
        self.config_file = config_file
        self.config = Params.read_config_yml()
        self.api_type = self.config['api_type']
        self.api_key = self.config['api_key']
        self.api_host = self.config['api_host']
        self.source_ac_db_path = self.config['source_ac_db_path']
        self.lat = self.config['default_lat']
        self.lon = self.config['default_lon']
        self.criteria = self.config['criteria']
        self.max_distance = self.config['max_distance']
        self.min_altitude = self.config['min_altitude']
        self.max_altitude = self.config['max_altitude']
        self.do_not_repeat_for = self.config['do_not_repeat_for']
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

class vocalization_string:
    def __init__(self, filtered_plane_info_df):
        self.filtered_plane_info_df = filtered_plane_info_df
        self.vocalization_string = self.get_vocalization_string()

    def get_vocalization_string(self):
        manufacturer = str(self.filtered_plane_info_df['manufacturername'])
        manufacturer = manufacturer.split(' ')[0]         # take just the first word of the manufacturer name
        if manufacturer == 'nan':
            manufacturer = 'unknown'
        model = str(self.filtered_plane_info_df['model'])
        # strip dashes from model name
        model = model.replace('-', '')
        distance = float(self.filtered_plane_info_df['distance'])
        distance = round(distance, 1)
        print("distance: " + str(distance))
        if model == 'nan':
            model_ssml = 'aircraft'
        else:
            # split model name into separate strings, based on letters and numbers
            model = re.findall(r'[a-zA-Z]+|\d+', model)
            # make ssml tags for each string. If string is a number, make it a cardinal number. If string is a letter, make it a word.
            model_ssml = []
            for i in model:
                if i.isdigit():
                    model_ssml.append('<say-as interpret-as="number" format="cardinal">' + i + "</say-as>")
                else:
                    model_ssml.append("<say-as interpret-as='spell-out'>" + i + "</say-as>" + '<break time="0.1s">' + '</break>')
            # join the ssml tags into a single string
            print(model_ssml)
            model_ssml = ' '.join(model_ssml)
        if str(distance) == 'nan':
            vocalization_string = "<speak>There is a " + manufacturer + " " + model_ssml + " " + "nearby. </speak>"
        else:
            vocalization_string = "<speak>There is a " + manufacturer + " " + model_ssml + " " + '<say-as interpret-as="number" format="cardinal">' + str(round(distance)) +'</say-as>'  + " miles away.</speak>"
        return vocalization_string

def get_nearby_traffic_xplane(lat, lon, api_key, api_host):
    conn = http.client.HTTPSConnection(str(api_host))
    headers = {
    'X-RapidAPI-Key': str(api_key),
    'X-RapidAPI-Host': str(api_host)
    }
    request_string = "/api/aircraft/json/lat/" + str(lat) + "/lon/" + str(lon) + "/dist/25/"
    time.sleep(random.uniform(0.1, 4.5))
    conn.request("GET", request_string, headers=headers)
    res = conn.getresponse()
    data = res.read()
    decoded = data.decode("utf-8")
    planes = json.loads(decoded)
   # planes = planes["ac"]
    return planes

def filter_planes(api_return, params):
    '''Return filtered list of icao24 codes from api_return, given params'''
    max_distance = params.max_distance
    planes = json.loads(api_return)['ac']
    filtered_planes = []
    filtered_distances = []
    filtered_altitudes = []
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
            if float(plane['dst']) <= float(max_distance) and float(plane['alt']) >= float(params.min_altitude) and float(plane['alt']) <= float(params.max_altitude):
                icao = plane['icao']
                filtered_planes.append(icao)
                filtered_distances.append(plane['dst'])
                filtered_altitudes.append(plane['alt'])
        else:
            if float(plane['dst']) <= float(max_distance) and int(plane[criteria_key]) == int(criteria_value) and float(plane['alt']) >= float(params.min_altitude) and float(plane['alt']) <= float(params.max_altitude):
                icao = plane['icao']
                filtered_planes.append(icao)
                filtered_distances.append(plane['dst'])
                filtered_altitudes.append(plane['alt'])
    now = str(datetime.datetime.now())
    print(now + ": Found " + str(len(filtered_planes)) + " planes")
    return filtered_planes, filtered_distances, filtered_altitudes

def import_local_opensky_aircraft_database(path):
    '''Import local opensky aircraft database, creates ac_db.db if it doesn't exist'''
    # TODO: check if ac_db.db is up to date, etc.
    # check if ac_db.db exists
    ac_db_name = 'ac_db' # TODO: make this a param, which can be updated if using different data source, or if updating names by date etc. 
    ac_db_fullname = ac_db_name + '.db'
    if os.path.isfile(ac_db_fullname):
        print("ac_db.db exists")
        # if it does, connect to it
        conn = sql.connect(ac_db_fullname)
    else:
        print(ac_db_fullname + " does not exist, creating from " + path)
        col_names = ['icao24', 'registration', 'manufacturericao', 'manufacturername', 'model', 'typecode', 'serialnumber', 'linenumber', 'icaoaircrafttype', 'operator', 'operatorcallsign', 'operatoricao', 'operatoriata', 'owner', 'testreg']
        # load csv into pandas df
        df = pd.read_csv(path, names=col_names,on_bad_lines="warn") #, encoding='cp1252'
        # convert pandas df to sqlite db
        conn = sql.connect(ac_db_fullname)
        df.to_sql(ac_db_name, conn, if_exists='replace', index=False)
    return conn

def get_info_for_icao_list(icao_list, filtered_plane_distances, filtered_plane_altitudes, ac_db_conn):
    '''Return pandas df of aircraft info for list of icao24 codes'''
    # create empty df
    df = pd.DataFrame()
    # loop through icao_list
    i = 0
    for icao in icao_list:
        dist = float(filtered_plane_distances[i])
        alt = float(filtered_plane_altitudes[i])
        # get info for each icao
        df = df.append(get_plane_info_from_opensky(icao, ac_db_conn))
        df = df.append({'distance': dist, 'altitude': alt}, ignore_index=True)
        # add distance and altitude to df
        # df.loc[df['icao24'] == icao.lower(), 'distance'] = dist
        # df.loc[df['icao24'] == icao.lower(), 'altitude'] = alt
        i += 1
    return df

def get_plane_info_from_opensky(icao, ac_db_conn):
    # given icao, get plane info from ac_db
    lowercase_icao = icao.lower()
    query = "SELECT * FROM ac_db WHERE icao24 = '" + lowercase_icao + "'"
    df = pd.read_sql_query(query, ac_db_conn)
    # then, we'll add columns for distance and altitude. 
    return df



def monitor_skies(ac_db_conn, params, interval):
    monitoring = True
    while monitoring == True:
        t0 = time.time()
        api_return = json.dumps(call_api(params.api_type, params.lat, params.lon, params.api_key, params.api_host).nearby_traffic)
        if api_return == "[]":
            print("No planes found")
            time.sleep(wait_time)
            continue
        else:
            filtered_plane_icaos, filtered_plane_distances, filtered_plane_altitudes = filter_planes(api_return, params)
            filtered_plane_info_df = get_info_for_icao_list(filtered_plane_icaos, filtered_plane_distances, filtered_plane_altitudes, ac_db_conn) # returns df
            for i in range(len(filtered_plane_info_df)):
                script = vocalization_string(filtered_plane_info_df.iloc[i])
                print(script.vocalization_string)
                subprocess.run(["larynx", "--ssml", "-v", "southern_english_male", "-q", "high", "--length-scale", "1.6", str(script.vocalization_string)])
            tf = time.time()
            vocalizing_time = tf - t0
            wait_time = float(interval - vocalizing_time)
            time.sleep(wait_time)
