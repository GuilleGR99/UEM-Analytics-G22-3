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
import pymongo
from pymongo import MongoClient
import json


# In[2]:


# *inicio de sesion en mongo y listado de colecciones.
# *Otros user_name [Miguel, Lucas, Julieta, Guillermo]
# def inicio_sesion(user_name, password):
def inicio_sesion():
    user_name = 'Guillermo'
    password = 'aplicacionesytendenciasdelanalisisdedatos2022'
    cluster = MongoClient(f'mongodb+srv://{user_name}:{password}@cluster0.rnxayot.mongodb.net/?retryWrites=true&w=majority')
    # *seleccion de la coleccion de datos
    db = cluster['papers']
    db.list_collection_names()
    return(db)


# In[3]:


#* Acceso a todas las colecciones. Devuelve una lista con las colecciones
# nombres colecciones: papers   final_distances  tockenizador  refinded_paper  final_paper   papers_2
def acceder_una_coleccion(nombre_col):
    db = inicio_sesion()
    collection = db[nombre_col]
    return(collection)


# In[4]:


#* Debe pasarsele un datos en formato json y una coleccion como acceder_coleccion[x] 
def save_mongo(data, collection):
    # *guarda data en mongo db, si la coleccion esta vacia inserta el primero, 
    # *si no esta vacio compara si alguno de los documentos en la coleccion tiene 
    # *el mismo titulo que el que se va a insertar, si no es asi se inserta.
    cantidad_inicial = collection.count_documents({})
    try:
        for i in range(len(data)):
            if collection.count_documents({}) == 0:
                collection.insert_one(data[i])
            try:
                collection.find({'titulo':data[i]['titulo']})[0]
            except:
                collection.insert_one(data[i])
        print('Creación correcta') 
    except Exception as exception:
        print(exception)
    #print('Se han realizado', collection.count_documents({}) - cantidad_inicial , 'nuevas insercciones')  


# In[ ]:



    
    
    
    


# In[5]:


def delete_mongo(identificadores, collection):
    for i in identificadores:
        myquery = { "_id": i }
        collection.delete_one(myquery)


# In[6]:


def pandas_to_json(df):
    return json.loads(df.apply(lambda x: decode_encode(x) if type(x) == type(["x"]) else x ).to_json(orient="records"))



# In[7]:


class cleaner():
    def __init__(self):
        nltk.download('stopwords')
        self.word_list = stopwords.words('english')
        self.stemmer = PorterStemmer() 
    def __call__(self, text):
        res = ""
        words = re.sub( "[()-/%""”“?''’]","" ,re.sub("\d+", "", text.lower().replace("\n","").replace(".","").replace(",","").replace("b'","") )).split(" ")
        palabras = [h for h in words  ] # if h not in self.word_list
        frase = ' '.join(palabras)
        return frase
    def flat_clean(self, text):
        res = ""
        words = re.sub( "[()-/%""”“?''’]","" ,re.sub("\d+", "", text.lower().replace("\n","").replace(".","").replace(",","").replace("b'","") )).split(" ")
        palabras = [self.stemmer.stem(h) for h in words if h not in self.word_list ]
        frase = ' '.join(palabras)
        return frase
        
   


# In[8]:


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


# In[9]:


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


# In[10]:


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


# In[11]:


def suma(lista):
    lista_tem = " ".join(lista)
    return(lista_tem )
def decode_encode(lista):
    lista_tem = [x.decode('utf-8','ignore').encode("utf-8") if type(x) == type("x") else x for x in lista   ]
    return(lista_tem )


# In[12]:


def main():
    print("inicio")
    db_ini = "papers_2"
    db_fin = "refinded_paper"
    #data = pd.read_csv("total.csv", on_bad_lines='skip')
    db_from = acceder_una_coleccion(db_ini)
    db_to = acceder_una_coleccion(db_fin)
    data =  pd.DataFrame(list(db_from.find(limit= 3)))
    data = data.dropna()
    if len(data) == 0:
        print("tabla vacia")
        return()
    limpiador = cleaner()
    print("cleaner cargado")
    extractor_keywords = keyword_extractor()
    print("keyword_extractor cargado")
    resumidor = summary()
    print("summary cargado")
    #ajustar columnas
    lista_procesados = data["_id"].tolist()
    data["abstract"] = list(map(suma, data["abstract"].tolist()))
    data["titulo"] = list(map(suma, data["titulo"].tolist()))
    data["n_citaciones"] = list(map(suma, data["n_citaciones"].tolist()))
    data = data.drop(columns=['_id'])
    ### ejecutar limpiezas
    data["abstract_limpio"] =  data["abstract"].apply(lambda x: limpiador(x))
    print("primera ejecucion terminada")
    data["resumen"] =  data["abstract_limpio"].apply(lambda x: resumidor(x)) 
    print("segunda ejecucion terminada")
    data["keywords"] =  data["abstract_limpio"].apply(lambda x: extractor_keywords(x))
    print("tercera ejecucion terminada")
    data["resumen_limpio"] =  data["resumen"].apply(lambda x: limpiador(x)) 
    print("cuarta ejecucion terminada")
    data["resumen_plano"] =  data["resumen"].apply(lambda x: limpiador.flat_clean(x)) 
    print("quinta ejecucion terminada")
    data["abstract_plano"] =  data["abstract"].apply(lambda x: limpiador.flat_clean(x)) 
    print("sexta ejecucion terminada")
    #####################
    to_upload = pandas_to_json(data)
    save_mongo(to_upload, db_to)
    delete_mongo(lista_procesados, db_from)
    print("FIN")
      
    
    
if __name__ == "__main__":
    main()


# In[ ]:




