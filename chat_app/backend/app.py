from flask_cors import CORS
from flask import Flask, request, jsonify
from elasticsearch import Elasticsearch

from .elastic_search import search_documents
from .encoder import EncoderModel,E5ReteriveModel

import time 
import json

import torch

import logging

logging.basicConfig(filename='app.log', level=logging.DEBUG)

app = Flask(__name__)

class AppConfig:
    def __init__(self):
        self._model = None

    @property
    def model(self):
        if self._model is None:
            self._model = E5ReteriveModel.load(model_path="intfloat/multilingual-e5-large")
            self._model.lm.eval()
        return self._model

# モデルを持つためのインスタンス
config = AppConfig()

@app.route('/api/syllabus_search', methods=['GET'])
def search():
    print("ここまできたよ")
    query = request.args.get('q','')
    model_name_1 = request.args.get('model_name_1','')
    model_name_2 = request.args.get('model_name_2','')
    model_name = [model_name_1,model_name_2]
    model = config.model
    results = search_documents(query=query,index="syllabus-vector-index",model=model,model_name=model_name)
    print(results)
    return json.dumps(results,ensure_ascii=False)

if __name__ == '__main__':
    app.run(debug=True)
