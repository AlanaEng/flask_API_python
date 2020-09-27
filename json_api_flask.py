import json
from flask_cors import CORS
from flask import jsonify, Flask
import datetime as dt
from datetime import timedelta

app = Flask(__name__) 
CORS(app) # configura o cors
app.config['JSON_AS_ASCII'] = False # configura a acentuação do português na api

# variáveis principais
current_nominal = 4.21  # Corrente nominal
start_value = dt.datetime.now() - timedelta(1) # data inicial
default_start = dt.datetime.strftime(start_value, '%d-%m-%Y') #data inicial padrão
end_value = dt.datetime.now() # data final
default_end = dt.datetime.strftime(end_value, '%d-%m-%Y') # data final padrão
machine = 'Machine_01' # define máquina
pre_end_ts = dt.datetime.now() - dt.timedelta(days=0) # data inicial predeterminada
pre_start_ts = pre_end_ts - dt.timedelta(days=7) #data final predeterminada


@app.route('/variable_calc/', defaults={'machine': machine, 'start_ts': default_start, 'end_ts': default_end}) # retorna dados padrões
@app.route('/variable_calc/<string:machine>/', defaults={'start_ts': default_start, 'end_ts': default_end}) # retorna maquina desejada e datas padrões
@app.route('/variable_calc/<string:machine>/<string:start_ts>/<string:end_ts>') # retorna dados desejados 
def variable_calc(machine: str, start_ts: str, end_ts: str):
    
    # efetua cálculo delta de temperatura de retorno - insuflamento
    temp_insufflation, __, __, current_measured, __, __, temp_return, estimated_consumption = ft.groupPoints(machine,
                                                                                                             'one') # retorna dataframes das variaveis da máquina desejada
    # retorna vetor dos valores do delta de insuflamento
    value_return = temp_return
    value_insufflation = temp_insufflation
    temp_return_insufflation = value_insufflation - value_return  # delta
    
    # retorna corrente futura
    predict_current = ft.load_current_future(machine, start_ts, end_ts)

    # Autotunning de correte, retorna status da corrente
    textValue_cur, textAnomaly_cur = ft.load_autunning_current(machine, start_ts, end_ts, current_nominal)
    overcurrent = textValue_cur

    # Anomalia de corrente
    cur_anomaly_status = textAnomaly_cur

    # Machine learning predict_temp_one, series, pd_graph_future, pd_vec_upper, pd_vec_lower
    predict_temp_one, __, __,__,__ = ft.load_temp_future(machine, start_ts, end_ts)
    temp_prediction = predict_temp_one

    # Autotunning temperatura
    textValue_temp, textAnomaly_temp, upper_bond_max, lower_bond_min = ft.load_autunning_temp(machine, start_ts, end_ts)
    temp_limits_status = textValue_temp

    # Anomalia de temperatura
    temp_anomaly_status = textAnomaly_temp
    
    # organiza arquivo JSON
    insights = [
            {
                "key": "Delta de temperatura",
                "value": str(temp_return_insufflation) + " °C"
            },
            {
               "key": "Consumo diário estimado",
               "value": str(estimated_consumption) + " kWh"
            },
            {
                "key": "Temperatura prevista",
                "value": str(temp_prediction) + " °C"
            },
            {
                "key": "Limite superior de temperatura",
                "value": str(upper_bond_max) + " °C"
            },
            {
                "key": "Limite inferior de temperatura",
                "value": str(lower_bond_min) + " °C"
            },
            {
                "key": "Status de limite",
                "value": str(temp_limits_status)
            },
            {
                "key": "Anomalia de temperatura",
                "value": str(temp_anomaly_status)
            },
            {
                "key": "Corrente prevista",
                "value": str(predict_current) + " A"
            },
            {
                "key": "Sobrecorrente",
                "value": str(overcurrent)
            },
            {
                "key": "Anomalia de corrente",
                "value": str(cur_anomaly_status)
            }

        ]
    
    group_calc = jsonify(insights=insights)
    return group_calc, 200
    
#RUN    
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8886, debug = True, use_reloader=False)
