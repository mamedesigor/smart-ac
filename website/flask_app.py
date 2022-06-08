from flask import Flask, render_template, request, jsonify
import json

data = {'temp1':'x'}

app = Flask(__name__)

@app.route('/request', methods=['GET', 'POST'])
def requestfn():
    global data
    if request.method == 'GET':
        with open('data.json') as f:
            data = json.load(f)
        return jsonify(data)

    if request.method == 'POST':
        data = request.json
        with open('data.json', 'w') as f:
            json.dump(data, f)
        return 'ok', 200

@app.route('/')
def index():
    return render_template('index.html')

application = app
