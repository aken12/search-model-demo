import torch
import torch.nn.functional as F
from torch import nn, Tensor

from transformers import AutoConfig, AutoTokenizer
from transformers import PreTrainedModel, AutoModel
from transformers.file_utils import ModelOutput

from typing import Dict, Optional

import logging

logging.basicConfig(filename='app.log', level=logging.DEBUG)

class EncoderModel(nn.Module):
    TRANSFORMER_CLS = AutoModel

    def __init__(self,
                 lm: PreTrainedModel,
                 model_path: str
                 ):
        super().__init__()
        self.lm = lm
        self.cross_entropy = nn.CrossEntropyLoss(reduction='mean')
        self.tokenizer = AutoTokenizer.from_pretrained(model_path=model_path)

    def forward(self, query, passage):
        p_reps = self.encode_passage(passage)
        q_reps = self.encode_query(query)
        return q_reps,p_reps

    def compute_similarity(self, q_reps, p_reps):
        return torch.matmul(q_reps, p_reps.transpose(0, 1))
    
    def encode_passage(self, psg):
        if psg is None:
            return None
        ids = psg["input_ids"]
        attention_mask = psg["attention_mask"]
        psg_out = self.lm(ids,attention_mask=attention_mask, return_dict=True)
        p_hidden = psg_out.last_hidden_state
        p_reps = p_hidden[:, 0]
        return p_reps

    def encode_query(self, qry):
        if qry is None:
            return None
        ids = qry["input_ids"]
        attention_mask = qry["attention_mask"]
        qry_out = self.lm(ids,attention_mask=attention_mask, return_dict=True)
        q_hidden = qry_out.last_hidden_state
        q_reps = q_hidden[:, 0]
        return q_reps
    
    @classmethod
    def load(cls, model_path):
        lm = cls.TRANSFORMER_CLS.from_pretrained(model_path)
        model = cls(lm=lm)
        return model

class E5ReteriveModel():
    TRANSFORMER_CLS = AutoModel

    def __init__(self,
                 lm: PreTrainedModel,
                 model_path: str
                 ):
        super().__init__()
        self.lm = lm
        self.lm.eval()
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.sep_token = self.tokenizer.sep_token

    def average_pool(self,
                    last_hidden_states,attention_mask):
        last_hidden = last_hidden_states.masked_fill(~attention_mask[..., None].bool(), 0.0)
        return last_hidden.sum(dim=1) / attention_mask.sum(dim=1)[..., None]
    
    def generate_e5_embs(self,input_texts,max_length=32):
        text_dict = self.tokenizer.encode_plus(input_texts, return_tensors='pt', max_length=max_length)
        #breakpoint() 
        outputs = self.lm(**text_dict)
        # text_dictの出力　{'input_ids': tensor([[     0,      6,   6242,  19323, 129823,  10793,  19323,      2]]), 'attention_mask': tensor([[1, 1, 1, 1, 1, 1, 1, 1]])}
        embeddings = self.average_pool(outputs.last_hidden_state, text_dict['attention_mask'])
        embeddings = F.normalize(embeddings, p=2, dim=1)
        return embeddings
    
    @classmethod
    def load(cls, model_path):
        lm = cls.TRANSFORMER_CLS.from_pretrained(model_path)
        model = cls(lm=lm,model_path=model_path)
        print(model)
        return model