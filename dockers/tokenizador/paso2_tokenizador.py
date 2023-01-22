#!/usr/bin/env python
# coding: utf-8

# In[1]:


from tensorflow.keras import layers
import numpy as np
import json
from keras.preprocessing.text import Tokenizer
#import tensorflow_text as text
import tensorflow as tf
import pandas as pd

from tensorflow import keras
import pymongo
from pymongo import MongoClient


# In[2]:


class text_vectorizer():
    def __init__(self,text):
        vocabulary = set()
        text.str.lower().str.split().apply(vocabulary.update)
        vocabulary_size = len(vocabulary)
        self.text_vectorizer = layers.TextVectorization(
            max_tokens=vocabulary_size,standardize="lower_and_strip_punctuation" , ngrams=2, output_mode="tf_idf",pad_to_max_tokens=True
        ) # "tf_idf" "count"
        with tf.device("/CPU:0"):
            self.text_vectorizer.adapt(text)
    def __call__(self, text):
        return self.text_vectorizer(text)


# In[ ]:





# In[3]:


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


# In[4]:


#* Acceso a todas las colecciones. Devuelve una lista con las colecciones
# nombres colecciones: papers   final_distances  tockenizador  refinded_paper  final_paper   papers_2
def acceder_una_coleccion(nombre_col):
    db = inicio_sesion()
    collection = db[nombre_col]
    return(collection)


# In[5]:


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


# In[6]:


def delete_mongo(identificadores, collection):
    for i in identificadores:
        myquery = { "_id": i }
        collection.delete_one(myquery)


# In[7]:


def decode_encode(lista):
    lista_tem = lista.decode('utf-8','ignore').encode("utf-8") 
    return(lista_tem )


# In[8]:


def pandas_to_json(df):
    return json.loads(df.to_json(orient="records"))
    #return json.loads(df.apply(lambda x: decode_encode(x) if type(x) == type(["x"]) else x ).to_json(orient="records"))


# In[9]:


def suma(lista):
    lista_tem = " ".join(lista)
    return(lista_tem )


# In[ ]:





# In[10]:


def main():
    src_data = pd.read_csv("src/sample_to_tokens.csv",encoding='utf-8', engine='python')
    print("inicio")
    db_ini = "refinded_paper"
    db_fin = "final_paper"
    db_fin_copy = "tockenizador"
    #data = pd.read_csv("total.csv", on_bad_lines='skip')
    db_from = acceder_una_coleccion(db_ini)
    db_to = acceder_una_coleccion(db_fin)
    db_to_copy = acceder_una_coleccion(db_fin_copy)
    data =  pd.DataFrame(list(db_from.find(limit= 2)))
    data = data.dropna()
    if len(data) == 0:
        print("tabla vacia")
        return()
    lista_procesados = data["_id"].tolist()
    data = data.drop(columns=['_id'])
    
    abs_tok = text_vectorizer(src_data["abstract_plano"])
    sum_tok = text_vectorizer(src_data["resumen_plano"])
    sub_tok = text_vectorizer(src_data["subjects"].map(lambda text : suma(text)))
    
    data["token_abtract"] = data["abstract_plano"].map(lambda text : abs_tok(text).numpy()[1:])
    data["token_resumen"] = data["resumen_plano"].map(lambda text : sum_tok(text).numpy()[1:])
    data["token_subjects"] = data["keywords"].map(lambda text : sub_tok(suma(text)).numpy()[1:])
    #####################
    to_upload = pandas_to_json(data)
    save_mongo(to_upload, db_to)
    save_mongo(to_upload, db_to_copy)
    delete_mongo(lista_procesados, db_from)
    print("FIN")

if __name__ == "__main__":
    main()


# In[ ]:





# In[ ]:





# In[ ]:




