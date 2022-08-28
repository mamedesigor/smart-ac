from flask import Flask, render_template, request, jsonify
import json
import matplotlib.pyplot as plt, mpld3

app = Flask(__name__)

@app.route('/plot')
def plotfn():
    x = [1,2,3,4]
    y = [1,2,3,4]
    plt.plot(x, y)
    fig = plt.figure(1)
    html_graph = mpld3.fig_to_html(fig)
    return html_graph

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
