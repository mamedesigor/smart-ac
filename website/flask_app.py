from flask import Flask, render_template, request, jsonify

data = {}

app = Flask(__name__)

@app.route('/request', methods=['GET', 'POST'])
def requestfn():
    global data
    if request.method == 'GET':
        return jsonify(data)

    if request.method == 'POST':
        data = request.json
        return 'ok', 200

@app.route('/')
def index():
    return render_template('index.html')

application = app
