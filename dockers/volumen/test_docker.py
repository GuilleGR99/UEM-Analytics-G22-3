#!/usr/bin/env python
# coding: utf-8

# In[1]:


from transformers import (
    TokenClassificationPipeline,
    SummarizationPipeline,
    AutoModelForTokenClassification,
    AutoTokenizer,BigBirdPegasusForConditionalGeneration
)
from transformers.pipelines import AggregationStrategy
import numpy as np
import pandas as pd
import nltk
from nltk.corpus import stopwords
import re
from nltk.stem import PorterStemmer


# In[2]:


class cleaner():
    def __init__(self):
        nltk.download('stopwords')
        self.word_list = stopwords.words('english')
        self.stemmer = PorterStemmer() 
    def __call__(self, text):
        res = ""
        words = re.sub( "[()-/%""”“?''’]","" ,re.sub("\d+", "", text.lower().replace(".","").replace(",","").replace("b'","") )).split(" ")
        palabras = [h for h in words  ] # if h not in self.word_list
        frase = ' '.join(palabras)
        return frase
    def flat_clean(self, text):
        res = ""
        words = re.sub( "[()-/%""”“?''’]","" ,re.sub("\d+", "", text.lower().replace(".","").replace(",","").replace("b'","") )).split(" ")
        palabras = [self.stemmer.stem(h) for h in words if h not in self.word_list ]
        frase = ' '.join(palabras)
        return frase
        
   


# In[3]:


class KeyphraseExtractionPipeline(TokenClassificationPipeline):
    def __init__(self, model, *args, **kwargs):
        super().__init__(
            model=AutoModelForTokenClassification.from_pretrained(model),
            tokenizer=AutoTokenizer.from_pretrained(model),
            *args,
            **kwargs
        )

    def postprocess(self, model_outputs):
        results = super().postprocess(
            model_outputs=model_outputs,
            aggregation_strategy=AggregationStrategy.SIMPLE,
        )
        return np.unique([result.get("word").strip() for result in results])


# In[4]:


class summary(SummarizationPipeline):
    def __init__(self, *args, **kwargs):
        super().__init__(
            model = BigBirdPegasusForConditionalGeneration.from_pretrained("google/bigbird-pegasus-large-arxiv", attention_type="original_full", max_length=50),
            tokenizer = AutoTokenizer.from_pretrained("google/bigbird-pegasus-large-arxiv"),
            *args,
            **kwargs
        )
    def postprocess(self, model_outputs):
        results = super().postprocess(
            model_outputs=model_outputs,
        )
        res = "none data"
        if len(results) > 0 :
            res = results[0].get("summary_text") 
        return res


# In[5]:


class keyword_extractor(TokenClassificationPipeline):
    def __init__(self, *args, **kwargs):
        super().__init__(
            model=AutoModelForTokenClassification.from_pretrained("ml6team/keyphrase-extraction-distilbert-inspec"),
            tokenizer=AutoTokenizer.from_pretrained("ml6team/keyphrase-extraction-distilbert-inspec"),
            *args,
            **kwargs
        )

    def postprocess(self, model_outputs):
        results = super().postprocess(
            model_outputs=model_outputs,
            aggregation_strategy=AggregationStrategy.SIMPLE,
        )
        return np.unique([result.get("word").strip() for result in results])


# In[6]:


def main():
    print("inicio")
    data = pd.read_csv("total.csv", on_bad_lines='skip')
    data = data.dropna()
    data = data.sample(100)
     
    limpiador = cleaner()
    print("cleaner cargado")
    extractor_keywords = keyword_extractor()
    print("keyword_extractor cargado")
    resumidor = summary()
    print("summary cargado")
    data["abstract_limpio"] =  data["abstract"].apply(lambda x: limpiador(x))
    print("primera ejecucion terminada")
    data["reumen"] =  data["abstract_limpio"].apply(lambda x: resumidor(x)) 
    print("segunda ejecucion terminada")
    data["keywords"] =  data["abstract_limpio"].apply(lambda x: extractor_keywords(x))
    print("tercera ejecucion terminada")
    data["reumen_limpio"] =  data["reumen"].apply(lambda x: limpiador(x)) 
    print("cuarta ejecucion terminada")
    data.to_csv("total_procesed.csv",index=False)  
    
    
if __name__ == "__main__":
    main()


# In[ ]:





# In[ ]:





# In[ ]:




