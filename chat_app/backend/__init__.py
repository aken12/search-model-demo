from flask_cors import CORS
from flask import Flask, request, jsonify
from elasticsearch import Elasticsearch

from .elastic_search import search_documents
from.encoder import EncoderModel

import time 
import json

app = Flask(__name__)
#CORS(app)
CORS(app)
print("起動")
start = time.time()
model_path = "/Users/mk042/chat_app/backend/checkpoint-40000"
model = EncoderModel.load(model_path)
model.eval()
print(model)
end = time.time()
print(f'時間: {end-start}')

@app.route('/syllabus_search', methods=['GET'])
def search():
    print("ここまできたよ")
    query = request.args.get('q','')
    model_name_1 = request.args.get('model_name_1','')
    model_name_2 = request.args.get('model_name_2','')
    model_name = [model_name_1,model_name_2]
    results = search_documents(query=query,index="syllabus-vecotor-index",model=model,model_name=model_name)
    print(results)
    print(model_name)
    return json.dumps(results,ensure_ascii=False)

if __name__ == '__main__':
    app.run(debug=True)
