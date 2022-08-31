from flask import Flask, render_template, request, jsonify
import json
import matplotlib.pyplot as plt, mpld3
from datetime import datetime
import sqlite3
import matplotlib
matplotlib.use('Agg')

data = {}

db = sqlite3.connect("sqlite3.db")
cursor = db.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
for table_name in tables:
    cursor.execute("SELECT * FROM " + table_name[0])
    table = cursor.fetchall()
    data.update({table_name[0]: table})
cursor.close()
db.close()

def deserialize_datetime(dt):
    line = dt.split()
    date = line[0].split('-')
    time = line[1].split(':')

    year = int(date[0])
    month = int(date[1])
    day = int(date[2])
    hour = int(time[0])
    minute = int(time[1])
    second = int(time[2])
    return datetime(year, month, day, hour, minute, second)

def get_timestamp(timestamp):
    timestamp = timestamp.split("-")
    return datetime(2022, 8, int(timestamp[0]), int(timestamp[1]), int(timestamp[2]))

app = Flask(__name__)

@app.route('/plot')
def plotfn():
    begin = request.args.get("begin")
    end = request.args.get("end")
    pq = request.args.get("pq")

    #SPECIFIC PLOT DATA
    if pq == "temp1":
        measurement = "bmp280"
        y_label = "temperatura (°C)"
        y_index = 0
        x_index = 2
    elif pq == "amps":
        measurement = "sct013"
        y_label = "corrente (A)"
        y_index = 0
        x_index = 1
    elif pq == "temp2":
        measurement = "htu21d"
        y_label = "temperatura (°C)"
        y_index = 0
        x_index = 2
    elif pq == "pressure":
        measurement = "bmp280"
        y_label = "pressão (hPa)"
        y_index = 1
        x_index = 2
    elif pq == "humidity":
        measurement = "htu21d"
        y_label = "humidade relativa (%RH)"
        y_index = 1
        x_index = 2
    elif pq == "eco2":
        measurement = "ccs811"
        y_label = "eCO2 (ppm)"
        y_index = 0
        x_index = 2
    elif pq == "tvoc":
        measurement = "ccs811"
        y_label = "TVOC (ppb)"
        y_index = 1
        x_index = 2
    elif pq == "motion1":
        measurement = "hcsr501_1"
        y_label = "movimento detectado"
        y_index = 0
        x_index = 1
    elif pq == "motion2":
        measurement = "hcsr501_2"
        y_label = "movimento detectado"
        y_index = 0
        x_index = 1
    elif pq == "pm25":
        measurement = "sds011"
        y_label = "pm25 (µg/m³)"
        y_index = 1
        x_index = 2
    elif pq == "pm10":
        measurement = "sds011"
        y_label = "pm10 (µg/m³)"
        y_index = 0
        x_index = 2
    elif pq == "door1":
        measurement = "mc38_1"
        y_label = "porta aberta/fechada"
        y_index = 0
        x_index = 1
    elif pq == "door2":
        measurement = "mc38_2"
        y_label = "porta aberta/fechada"
        y_index = 0
        x_index = 1
    elif pq == "luxes":
        measurement = "bh1750"
        y_label = "iluminância (lx)"
        y_index = 0
        x_index = 1
    elif pq == "instructions":
        measurement = "instructions"
        y_label = "Instruções"
        y_index = 0
        x_index = 1

    sensor_data = data.get(measurement)
    begin = get_timestamp(begin)
    end = get_timestamp(end)
    x = []
    y = []
    x_label = "tempo (h)"
    for line in sensor_data:
        timestamp = deserialize_datetime(line[x_index])
        if timestamp > begin and timestamp < end:
            x.append(timestamp)
            if measurement == "door1" or measurement == "door2":
                if line[y_index] == "open":
                    y.append("aberta")
                else :
                    y.append("fechada")
            else:
                y.append(line[y_index])

    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.plot(x, y)
    fig = plt.figure(1)
    dict_graph = mpld3.fig_to_dict(fig)
    dict_graph.update(width = 1200)
    fig.clear()
    return dict_graph

@app.route('/request', methods=['GET', 'POST'])
def requestfn():
    if request.method == 'GET':
        with open('data.json') as f:
            data = json.load(f)
        return jsonify(data)

    if request.method == 'POST':
        try:
            data = json.load(open('data.json'))
        except:
            data = {}
        for key in request.json:
            data.update({key: request.json[key]})
        with open('data.json', 'w') as f:
            json.dump(data, f)
        return 'ok', 200

@app.route('/')
def index():
    return render_template('index.html')

application = app
