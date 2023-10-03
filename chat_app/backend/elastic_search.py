from elasticsearch import Elasticsearch

es = Elasticsearch(hosts=[{'host': 'localhost', 'port': 9200,'scheme': 'http'}])
#es = Elasticsearch("http://localhost:9200", http_auth=('elastic', 'password')) 
def search_documents(index,query,model,model_name):
    results = {"result1": {} ,"result2": {"result": None}}
    model_dict = {"DPR": dense_search,"ColBERT":colbert_search}

    if model_name[1] == "No":
        if model_name[0] == "model1" or model_name[0] == "BM25":
            results["result1"]["result"] = bm25_search(index, query)
            results["result1"]["name"] = "BM25"
            return results
        else:
            results["result1"]["result"] = model_dict[model_name[0]](index, query, model)
            results["result1"]["name"] = model_name[0]
            return results
        
    if model_name[0] == "BM25":
        results["result1"]["result"] = bm25_search(index, query)
        results["result1"]["name"] = "BM25"
    elif  model_name[0] in model_dict.keys():
        results["result1"]["result"] = model_dict[model_name[0]](index, query, model)
        results["result1"]["name"] = model_name[0]

    if model_name[1] == "BM25":
        results["result2"] = {}
        results["result2"]["result"] = bm25_search(index, query)
        results["result2"]["name"] = "BM25"
    elif  model_name[1] in model_dict.keys():
        results["result2"] = {}
        results["result2"]["result"] = model_dict[model_name[1]](index, query, model)
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
    res = es.search(index=index,body=body)
    return res['hits']['hits']

def dense_search(index,query,model):
    tokenzized_query = model.tokenizer.encode_plus(query, return_tensors='pt', max_length=32)

    encoded_query,_ = model(tokenzized_query,None)

    es_query = {
        "size": 100,
        "knn": {
            "field": "doc_vector",
            "query_vector": encoded_query.tolist()[0],
            "k":100,
            "num_candidates":1000
        }
    }
    res = es.search(index=index,body=es_query)
    return res['hits']['hits']

def colbert_search():
    return