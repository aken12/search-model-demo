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
            self._model = []
            self._model.append(E5ReteriveModel.load(model_path="intfloat/multilingual-e5-large"))
            self._model.append(E5ReteriveModel.load(model_path="intfloat/multilingual-e5-small"))
        return self._model

# モデルを持つためのインスタンス
config = AppConfig()

@app.route('/api/syllabus_search', methods=['GET'])
def search():
    print("ここまできたよ")
    query = request.args.get('q','')
    model_name_1 = request.args.get('model_name_1','')
    model_name_2 = request.args.get('model_name_2','')
    model_names = [model_name_1,model_name_2]
    model = config.model
    results = search_documents(query=query,index="syllabus-vector-index",model=model,model_names=model_names)
    # print(results)
    return json.dumps(results,ensure_ascii=False)

if __name__ == '__main__':
    app.run(debug=True)

# from flask_cors import CORS
# from flask import Flask, request, jsonify
# from elasticsearch import Elasticsearch

# from backend.elastic_search import search_documents
# from backend.encoder import EncoderModel,E5ReteriveModel

# import time 
# import json

# import torch

# import logging

# logging.basicConfig(filename='app.log', level=logging.DEBUG)

# app = Flask(__name__)

# class AppConfig:
#     def __init__(self):
#         self._model1 = None
#         self._model2 = None
#         self._model1_path = None
#         self._model2_path = None
#         self._model_name_dict = {
#             "BM25": None,
#             "E5-small": "intfloat/multilingual-e5-small",
#             "E5-large": "intfloat/multilingual-e5-large"
#         }

#     def load_model(self, model_name, model_number):
#         if model_name in self._model_name_dict:
#             model_path = self._model_name_dict[model_name]
#             if model_number == 1 and (self._model1 is None or self._model1_path != model_path):
#                 self._model1 = E5ReteriveModel.load(model_path=model_path)
#                 self._model1.lm.eval()
#                 self._model1_path = model_path
#             elif model_number == 2 and (self._model2 is None or self._model2_path != model_path):
#                 self._model2 = E5ReteriveModel.load(model_path=model_path)
#                 self._model2.lm.eval()
#                 self._model2_path = model_path

#     @property
#     def model1(self):
#         return self._model1

#     @property
#     def model2(self):
#         return self._model2

# config = AppConfig()

# @app.route('/api/syllabus_search', methods=['GET'])
# def search():
#     print("ここまできたよ")
#     query = request.args.get('q','')
#     model_name_1 = request.args.get('model_name_1','')
#     model_name_2 = request.args.get('model_name_2','')

#     print(model_name_1,model_name_2)

#     if model_name_1 != '':
#         config.load_model(model_path=model_name_1, model_number=1)
#     if model_name_2 != '':
#         config.load_model(model_path=model_name_2, model_number=2)

#     model1 = config.model1
#     model2 = config.model2

#     model_name = [model_name_1,model_name_2]
#     model = [model1,model2]

#     results = search_documents(query=query,index="syllabus-vector-index",model=model,model_name=model_name)
#     print(results)
#     return json.dumps(results,ensure_ascii=False)

# if __name__ == '__main__':
#     app.run(host="0.0.0.0", port=5000,debug=True)
