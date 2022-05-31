import os
from flask import Flask, jsonify, request
import requests
import pandas as pd

app = Flask(__name__,)
app.config['SECRET_KEY'] = os.urandom(12).hex()


@app.route("/get-all-stations",methods=['GET'])
def index():
    stations = dict(requests.get('https://velib-metropole-opendata.smoove.pro/opendata/Velib_Metropole/station_information.json').json())['data']['stations']
    df_loc = pd.DataFrame(data=stations)
    details = dict(requests.get('https://velib-metropole-opendata.smoove.pro/opendata/Velib_Metropole/station_status.json').json())['data']['stations']
    def reformatDict(dict):
        dict['ebikes_available'] = dict["num_bikes_available_types"][1]['ebike']
        dict['bikes_available'] = dict["num_bikes_available_types"][0]['mechanical']
        del dict['num_bikes_available_types']
        return dict
    details = [reformatDict(detail) for detail in details]
    df_details = pd.DataFrame(data=details).drop(columns=['is_installed','is_returning','is_renting','numDocksAvailable','numBikesAvailable','num_bikes_available','stationCode'])
    df_final = pd.merge(df_loc,df_details,how='inner',left_on='station_id',right_on='station_id')
    try:
        limit = int(request.args.get('limit'))
    except:
        limit = 0
    if limit==0 or limit is None or limit>=len(df_final): 
        return jsonify(df_final.drop(columns=['rental_methods']).to_dict('records'))
    else:
        return jsonify(df_final.drop(columns=['rental_methods']).iloc[:limit].to_dict('records'))
