#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pymongo
from pymongo import MongoClient
from tensorflow.keras import layers
import tensorflow as tf
import numpy as np
import pandas as pd
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
                collection.insert_one(data[i])
            except Exception as exception:
                print(exception)
        print('Creación correcta') 
    except Exception as exception:
        print(exception)
    #print('Se han realizado', collection.count_documents({}) - cantidad_inicial , 'nuevas insercciones')  


# In[5]:


def delete_mongo(identificadores, collection):
    for i in identificadores:
        myquery = { "_id": i }
        collection.delete_one(myquery)


# In[6]:


def pandas_to_json(df):
    return json.loads(df.to_json(orient="records"))
    #return json.loads(df.apply(lambda x: decode_encode(x) if type(x) == type(["x"]) else x ).to_json(orient="records"))


# In[ ]:





# In[ ]:





# In[ ]:





# In[7]:


def evaluador(elem1,elem2):
    cosine_loss = tf.keras.losses.CosineSimilarity(axis=1)
    simil = cosine_loss([elem1], [elem2]).numpy()
    simil = simil*-1
    return simil


# In[8]:


def main():
    print("inicio")
    corte = 0
    w_abs = 1
    w_res = 2
    db_ini = "tockenizador"
    db_compare = "final_paper"
    db_fin = "final_distances"
    #data = pd.read_csv("total.csv", on_bad_lines='skip')
    db_from = acceder_una_coleccion(db_ini)
    db_compare = acceder_una_coleccion(db_compare)
    db_to = acceder_una_coleccion(db_fin)
    data =  pd.DataFrame(list(db_from.find(limit= 1)))
    data = data.dropna()
    data_to_compare =  pd.DataFrame(list(db_compare.find()))
    data_to_compare = data_to_compare.dropna()
    if len(data) == 0:
        print("tabla vacia")
        return()
    lista_procesados = data["_id"].tolist()
    data = data.drop(columns=['_id'])
    
    token_abtract = data["token_abtract"].map(tf.convert_to_tensor).tolist()[0]
    token_resumen = data["token_resumen"].map(tf.convert_to_tensor).tolist()[0]
    token_subjects = data["token_subjects"].map(tf.convert_to_tensor).tolist()[0]
    titulo_2 = data["titulo"].tolist()[0]
    
    data_to_compare["token_abtract"] = data_to_compare["token_abtract"].map(tf.convert_to_tensor)
    data_to_compare["token_resumen"] = data_to_compare["token_resumen"].map(tf.convert_to_tensor)
    data_to_compare["token_subjects"] = data_to_compare["token_subjects"].map(tf.convert_to_tensor)
    
    data_to_compare["comparation_abtract"] = data_to_compare["token_abtract"].map(lambda text : evaluador(text,token_abtract))
    data_to_compare["comparation_resumen"] = data_to_compare["token_resumen"].map(lambda text : evaluador(text,token_resumen))
    data_to_compare["comparation_subjects"] = data_to_compare["token_subjects"].map(lambda text : evaluador(text,token_subjects))
    data_to_compare["titulo_2"] =  titulo_2
    data_to_compare = data_to_compare[data_to_compare["comparation_abtract"]!=1]
    data_to_compare["distance"] = data_to_compare["comparation_abtract"]*w_abs + data_to_compare["comparation_resumen"]*w_res
    
    data_to_compare = data_to_compare[data_to_compare["distance"]>= corte]
    db_dis = data_to_compare[["titulo_2","titulo","distance"]]
    ############
    to_upload = pandas_to_json(db_dis)
    save_mongo(to_upload, db_to)
    delete_mongo(lista_procesados, db_from)
    
        

    
if __name__ == "__main__":
    main()


# In[ ]:



    


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




