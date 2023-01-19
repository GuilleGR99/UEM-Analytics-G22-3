#!/usr/bin/env python
# coding: utf-8

# In[1]:

# *Importamos librerias
import json
import csv
import pymongo
from pymongo import MongoClient
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
# *inicio de sesion en mongo
# *Introduce tu nombre como input o ponlo como variable [Miguel, Lucas, Julieta, Guillermo]
nombre = 'Guillermo'
# password = input('introduce pass')
password = 'aplicacionesytendenciasdelanalisisdedatos2022'
try:
    cluster = MongoClient(f'mongodb+srv://{nombre}:{password}@cluster0.rnxayot.mongodb.net/?retryWrites=true&w=majority')
    # *seleccion de la coleccion de datos
    db = cluster['papers']
    papers_collection = db['papers']
    refined_papapers_collection = db['refined_papes']
except Exception as exception:
    print(f'ocurrio un error'+'\n'+{exception})


#  In[2]:
#! Al recurpera los datos de mongodb _id es una lista, se convierte a dict para pasar a json
#* Transformer trabaja en csv, en una primera versión no realizo cambios en el formato. Paso de json a csv
#! Cargo json local porque desde la uni no puedo acceder a mongodb
try:
    papers_mongodb = list(papers_collection.find())
    for paper_lenght in range(len(papers_mongodb)):
        papers_mongodb[paper_lenght]['_id'] = {'ObjectId' : str(papers_mongodb[paper_lenght]['_id'])}        
except Exception as exception:
    print('Ocurrio un error'+'\n'
    + str(exception) +'\n'
    + 'cargado papers de disco local')
    papers_mongodb = pd.read_json('papers_mongodb.json')
    papers_mongodb.to_csv(index=False)


#  In[2]:


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

#* Limpieza, resumen y extracción de palabras clave
def main():
    print("inicio")
    papers_mongodb = pd.read_json('papers_mongodb.json')
    papers_mongodb.to_csv('total_test.csv')
    data = pd.read_csv("total_test.csv", on_bad_lines='skip')
    data = data.dropna()
    # data = data.sample(100)
     
    limpiador = cleaner()
    print("cleaner cargado")
    extractor_keywords = keyword_extractor()
    print("keyword_extractor cargado")
    #! Error: Unable to load weights from pytorch checkpoint file
    try:
        resumidor = summary()
        print("summary cargado")
    except Exception as exception: 
        print(exception)
    data["abstract_limpio"] =  data["abstract"].apply(lambda x: limpiador(x))
    print("primera ejecucion terminada")
    try:
        data["resumen"] =  data["abstract_limpio"].apply(lambda x: resumidor(x))
        print("segunda ejecucion terminada")
    except Exception as exception: 
        pass
    data["keywords"] =  data["abstract_limpio"].apply(lambda x: extractor_keywords(x))
    print("tercera ejecucion terminada")
    #?  Resumen se forma limpiando y resumiendo el abstract, porque aqui se vuelve a limpiar? 
    try:
        data["reumen_limpio"] =  data["resumen"].apply(lambda x: limpiador(x)) 
        print("cuarta ejecucion terminada")
    except:
        pass
    data.to_csv("total_procesed.csv",index=False)  
    
    
if __name__ == "__main__":
    main()


# In[ ]:





# In[ ]:





# In[ ]:




