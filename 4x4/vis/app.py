
from flask import Flask, Response
from flask import render_template, request, jsonify
from data import get_graph, get_meta

import json
from random import randint


import json

app = Flask(__name__)




@app.route('/')
def index():
    return render_template("index.html")

@app.route('/getgraph')
def getgraph():
    graphid = int(request.args.get('id'))
    json = get_graph(graphid).to_json(orient='values')
    return json

@app.route('/getmeta')
def getmeta():
    return jsonify({'data':get_meta().tolist()})

if __name__ == "__main__":
    app.run(debug=True, port=8000)
