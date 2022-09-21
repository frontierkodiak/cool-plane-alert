import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
from subprocess import call
from utils.funcs import Params, monitor_skies, vocalization_string, call_api, filter_planes, get_info_for_icao_list, import_local_opensky_aircraft_database
import json 
import sqlite3 as sql
import pandas as pd
import subprocess


params = Params("config.yml")

api_return = json.dumps(call_api(params.api_type, params.lat, params.lon, params.api_key, params.api_host).nearby_traffic)

ac_db_conn = import_local_opensky_aircraft_database(params.source_ac_db_path)

monitor_skies(ac_db_conn, params, 60)