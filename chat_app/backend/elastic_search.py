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
def search_documents(index,query,model,model_names):
    results = {"result1": {} ,"result2": {"result": None}}

    print(type(model),len(model))

    model_dict = {
        "No":bm25_search,
        "BM25": bm25_search,
        "E5-large": lambda index, query: dense_search(index, query, model=model[0], large=True),
        "E5-small": lambda index, query: dense_search(index, query, model=model[1], large=False),
        "Hyblid": lambda index, query: hybrid_search(index, query, model=model[0]),
    }

    for i,model_name in enumerate(model_names):
        i += 1
        if model_name in model_dict:
            search_result, search_time = model_dict[model_name](index,query)
            results[f'result{i}'] = {
                "name": model_name,
                "result": search_result,
                "search_time": search_time
            }
    # print(results)
    print(len(results))
    print(results.keys())
    print(results["result1"].keys())
    return results

    # model_dict = {
    #     "BM25": bm25_search,
    #     "ベクトル検索（E5-large）": lambda idx, qry: dense_search(idx, qry, model),
    #     "ベクトル検索（E5-small）": lambda idx, qry: dense_search(idx, qry, model),
    #     "Hybrid": lambda idx, qry: hybrid_search(idx, qry, model)
    # }


    # model_dict = {"DPR": dense_search,"Hyblid":hyblid_search}
    # if model_name[1] == "No":
    #     if model_name[0] == "model1" or model_name[0] == "BM25":
    #         results["result1"]["result"],results["result1"]["search_time"] = bm25_search(index, query)
    #         results["result1"]["name"] = "BM25"
    #         return results
    #     else:
    #         results["result1"]["result"],results["result1"]["search_time"] = model_dict[model_name[0]](index, query, model)
    #         results["result1"]["name"] = model_name[0]
    #         return results
        
    # if model_name[0] == "BM25":
    #     results["result1"]["result"],results["result1"]["search_time"] = bm25_search(index, query)
    #     results["result1"]["name"] = "BM25"
    # elif  model_name[0] in model_dict.keys():
    #     results["result1"]["result"],results["result1"]["search_time"] = model_dict[model_name[0]](index, query, model)
    #     results["result1"]["name"] = model_name[0]

    # if model_name[1] == "BM25":
    #     results["result2"] = {}
    #     results["result2"]["result"],results["result2"]["search_time"] = bm25_search(index, query)
    #     results["result2"]["name"] = "BM25"
    # elif  model_name[1] in model_dict.keys():
    #     results["result2"] = {}
    #     results["result2"]["result"],results["result2"]["search_time"] = model_dict[model_name[1]](index, query, model)
    #     results["result2"]["name"] = model_name[1]

    # return results

def bm25_search(index,query,model=None):
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
    # print(res)
    return res['hits']['hits'],search_time

def dense_search(index,query,model,large=False):
    with torch.no_grad():
        encoded_query = model.generate_e5_embs("query: " + query)

    if large:
        field = "doc_vector_large" 
    else:
        field = "doc_vector"

    es_query = {
        "size": 100,
        "knn": {
            "field": field,
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

def hybrid_search(index,query,model):
    with torch.no_grad():
        encoded_query = model.generate_e5_embs("query: " + query)

    print("ここはOK")

    es_query = {
                "size": 100,
                "query": {"multi_match": {"query": query, "fields": ["subject_name", "course_overview"]}},
                "knn": {
                        "field": "doc_vector_large",
                        "query_vector": encoded_query.tolist()[0],
                        "k": 100,
                        "num_candidates": 1000,
                },
            }
    
    start = time.time()
    res = es.search(index=index,body=es_query)
    end = time.time()
    # print(res)
    search_time = end-start
    print(search_time)
    return res['hits']['hits'], search_time