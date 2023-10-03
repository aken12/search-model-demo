from elasticsearch import Elasticsearch
from chat import query_translate

es = Elasticsearch(hosts=[{'host': 'localhost', 'port': 9200,'scheme': 'http'}])
#es = Elasticsearch(
    #"https://localhost:9200",
    #ssl_assert_fingerprint=CERT_FINGERPRINT,
    #basic_auth=("elastic",ELASTIC_PASSWORD)
#)

def search_documents(index, query_json,model):
    query = query_json.get('q','')
    q_ids = model.tokenizer.encode_plus(query, return_tensors='pt',max_length=32)
    q_encoded,_ = model(q_ids,None)
    query = {
    "field": "my_vector",
    "query_vector": q_encoded.tolist()[0],
    "k": 100,
    "num_candidates": 100,
    "similarity" : "l2_norm"
    }
    es_query = {
		        "knn": {
				    "field": "doc_vector",
				    "query_vector": q_encoded.tolist()[0],
				    "k": 10,
				    "num_candidates": 10
                }
            }
    #res = es.knn_search(index=index, knn=query)
    res = es.search(index=index,body=es_query)
    return res['hits']['hits']
    # #&queryTrans=${queryTrans}&semester=${semester}&semesterAbc=${semesterAbc}&timeSlot=${timeSlot}`)
    ##    semester = query_json.get('semester','')
    ##abc = query_json.get('semesterAbc','')
    ##ime = query_json.get('timeSlot','')
    ##date =query_json.get('date','')
    #                    body={"query": {'match': {'subject_name':value}}})