from flask import Flask, render_template, request, jsonify
import json

app = Flask(__name__)

@app.route('/request', methods=['GET', 'POST'])
def requestfn():
    if request.method == 'GET':
        with open('data.json') as f:
            data = json.load(f)
        return jsonify(data)

    if request.method == 'POST':
        data = json.load(open('data.json'))
        for key in request.json:
            data.update({key: request.json[key]})
        with open('data.json', 'w') as f:
            json.dump(data, f)
        return 'ok', 200

@app.route('/')
def index():
    return render_template('index.html')

application = app
