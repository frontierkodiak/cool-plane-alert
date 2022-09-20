from subprocess import call
from utils.funcs import Params, call_api, filter_planes, get_info_for_icao_list, import_local_opensky_aircraft_database
import json 
import sqlite3 as sql
import pandas as pd


params = Params("config.yml")


# ac_db = load_ac_db(params.source_ac_db_path)

api_return = json.dumps(call_api(params.api_type, params.lat, params.lon, params.api_key, params.api_host).nearby_traffic)

ac_db_conn = import_local_opensky_aircraft_database(params.source_ac_db_path)

filtered_plane_icaos, filtered_plane_distances = filter_planes(api_return, params)
print(filtered_plane_icaos)
print(filtered_plane_distances)

filtered_plane_info_df = get_info_for_icao_list(filtered_plane_icaos, filtered_plane_distances, ac_db_conn) # returns df
print(filtered_plane_info_df)
