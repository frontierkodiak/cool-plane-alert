from subprocess import call
from utils.funcs import Params, call_api, filter_planes
import json 

params = Params("config.yml")


api_return = json.dumps(call_api(params.api_type, params.lat, params.lon, params.api_key, params.api_host).nearby_traffic)



filtered_planes = filter_planes(api_return, params)
print(filtered_planes)