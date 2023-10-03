from transformers import AutoConfig, AutoTokenizer
import torch
from torch import nn, Tensor
from transformers import PreTrainedModel, AutoModel
from transformers.file_utils import ModelOutput
from typing import Dict, Optional

class EncoderModel(nn.Module):
    TRANSFORMER_CLS = AutoModel

    def __init__(self,
                 lm: PreTrainedModel
                 ):
        super().__init__()
        self.lm = lm
        self.cross_entropy = nn.CrossEntropyLoss(reduction='mean')
        self.tokenizer = AutoTokenizer.from_pretrained("xlm-roberta-large")

    def forward(self, query, passage):
        p_reps = self.encode_passage(passage)
        q_reps = self.encode_query(query)
        # for inference
        #print(p_reps,q_reps)
        return q_reps,p_reps

    def compute_similarity(self, q_reps, p_reps):
        return torch.matmul(q_reps, p_reps.transpose(0, 1))
    
    def encode_passage(self, psg):
        if psg is None:
            return None
        ids = psg["input_ids"]
        attention_mask = psg["attention_mask"]
        #psg_out = self.lm(psg, return_dict=True)
        psg_out = self.lm(ids,attention_mask=attention_mask, return_dict=True)
        p_hidden = psg_out.last_hidden_state
        p_reps = p_hidden[:, 0]
        return p_reps

    def encode_query(self, qry):
        if qry is None:
            return None
        ids = qry["input_ids"]
        attention_mask = qry["attention_mask"]
        #qry_out = self.lm(qry,return_dict=True)
        qry_out = self.lm(ids,attention_mask=attention_mask, return_dict=True)
        q_hidden = qry_out.last_hidden_state
        q_reps = q_hidden[:, 0]
        return q_reps
    
    @classmethod
    def load(cls, model_path):
        lm = cls.TRANSFORMER_CLS.from_pretrained(model_path)
        model = cls(lm=lm)
        return model