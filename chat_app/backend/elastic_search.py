from elasticsearch import Elasticsearch
from.encoder import EncoderModel,E5ReteriveModel

import torch
import os
import time

import logging

logging.basicConfig(filename='app.log', level=logging.DEBUG)

es_user = os.environ.get('ES_USER')
es_password = os.environ.get('ELASTIC_PASSWORD')
es_path = os.environ.get('ES_HOME')

# その他の設定
es_host = "localhost"
es_port = 9200
ca_certs = os.path.join(es_path,"config/certs/http_ca.crt")

es = Elasticsearch(
    [
        {'host': es_host, 'port': es_port, "scheme": "https"}
    ],
    basic_auth=(es_user, es_password),
    verify_certs=True,
    ca_certs=ca_certs,
)

## 要修正
def search_documents(index,query,model,model_name):
    results = {"result1": {} ,"result2": {"result": None}}

    model_dict = {"DPR": dense_search,"Hyblid":hyblid_search}

    if model_name[1] == "No":
        if model_name[0] == "model1" or model_name[0] == "BM25":
            results["result1"]["result"],results["result1"]["search_time"] = bm25_search(index, query)
            results["result1"]["name"] = "BM25"
            return results
        else:
            results["result1"]["result"],results["result1"]["search_time"] = model_dict[model_name[0]](index, query, model)
            results["result1"]["name"] = model_name[0]
            return results
        
    if model_name[0] == "BM25":
        results["result1"]["result"],results["result1"]["search_time"] = bm25_search(index, query)
        results["result1"]["name"] = "BM25"
    elif  model_name[0] in model_dict.keys():
        results["result1"]["result"],results["result1"]["search_time"] = model_dict[model_name[0]](index, query, model)
        results["result1"]["name"] = model_name[0]

    if model_name[1] == "BM25":
        results["result2"] = {}
        results["result2"]["result"],results["result2"]["search_time"] = bm25_search(index, query)
        results["result2"]["name"] = "BM25"
    elif  model_name[1] in model_dict.keys():
        results["result2"] = {}
        results["result2"]["result"],results["result2"]["search_time"] = model_dict[model_name[1]](index, query, model)
        results["result2"]["name"] = model_name[1]

    return results

def bm25_search(index,query):
    body={
        "size": 10,
        'query':{
            'bool':{
                'should':[
                    {'match': {'subject_name': query}},
                    {'match':{'course_overview': query}}
                    ]
                }
            },
            "from" : 0,
            "size" : 100
        }

    start = time.time()
    res = es.search(index=index,body=body)
    end = time.time() 

    search_time = end-start
    print(res)
    return res['hits']['hits'],search_time

def dense_search(index,query,model):
    with torch.no_grad():
        encoded_query = model.generate_e5_embs(query)

    es_query = {
        "size": 100,
        "knn": {
            "field": "doc_vector",
            "query_vector": encoded_query.tolist()[0],
            "k":100,
            "num_candidates":1000
        }
    }

    start = time.time()
    res = es.search(index=index,body=es_query)
    end = time.time()
    search_time = end-start
    return res['hits']['hits'], search_time

def hyblid_search(index,query,model):
    with torch.no_grad():
        encoded_query = model.generate_e5_embs(query)

    es_query = {
                "size": 100,
                "query": {"multi_match": {"query": query, "fields": ["subject_name", "course_overview"]}},
                "knn": {
                        "field": "doc_vector",
                        "query_vector": encoded_query.tolist()[0],
                        "k": 100,
                        "num_candidates": 1000,
                },
            }
    
    start = time.time()
    res = es.search(index=index,body=es_query)
    end = time.time()
    print(res)
    search_time = end-start
    print(search_time)
    return res['hits']['hits'], search_time