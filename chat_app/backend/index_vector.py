from elasticsearch import Elasticsearch, helpers
import pickle
import csv
from tqdm import tqdm
import os
import torch

from encoder import E5ReteriveModel


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

index_name = 'syllabus-index'

if es.indices.exists(index=index_name):
    es.indices.delete(index=index_name)
    print("削除完了")

index_name = 'syllabus-vector-index'

def index_vector(es, index_name, doc_id, body):
    es.index(index=index_name, id=doc_id, body=body)

mappings = {
    "_source": {
    "excludes": ["doc_vector"]
    },
    "properties": {
        "doc_vector_large": {
            "type": "dense_vector",
            "dims": 1024,
            "index": True,
            "similarity": "dot_product"
        },
        "doc_vector": {
            "type": "dense_vector",
            "dims": 384,
            "index": True,
            "similarity": "dot_product"
        },
        "subject_number": {
            "type": "text"
        },
        "subject_name": {
            "type": "text"
        },
        "semester": {
            "type": "text"
        },
        "time_slot": {
            "type": "text"
        },
        "classroom": {
            "type": "text"
        },
        "course_overview": {
            "type": "text"
        },
        "id": {
            "type": "text"
        }
    }
}

# インデックス作成
if es.indices.exists(index=index_name):
    es.indices.delete(index=index_name)
    print(f"{index_name} 削除完了")

es.indices.create(index=index_name, body={"mappings": mappings})

csv_path = "/home/ec2-user/search-model-demo/chat_app/data/kdb-20240126.csv"
lines = [line for line in csv.reader(open(csv_path))]

# with open(f"/home/ec2-user/search-model-demo/chat_app/backend/my_encode_dir/e5_index.pkl", "rb") as f:
    # loaded_vectors = pickle.load(f)
model = E5ReteriveModel.load(model_path="intfloat/multilingual-e5-small")
model.lm.eval()
model_large = E5ReteriveModel.load(model_path="intfloat/multilingual-e5-large")
model_large.lm.eval()
for i in tqdm(range(len(lines)),total=len(lines)):
    with torch.no_grad():
        doc =  "passage: " + lines[i][1] + lines[i][9]
        encoded_doc = model.generate_e5_embs(doc,max_length=128)
        encoded_doc_large = model_large.generate_e5_embs(doc,max_length=128)
        body = {
            "id":i-1,
            "subject_number": lines[i][0],
            "subject_name": lines[i][1],
            "semester": lines[i][5],
            "time_slotre": lines[i][6],
            "classroom": lines[i][7],
            "course_overview":lines[i][9],
            "doc_vector": encoded_doc[0].tolist(),
            "doc_vector_large": encoded_doc_large[0].tolist(),            
        }           
        index_vector(es,index_name,i,body) 