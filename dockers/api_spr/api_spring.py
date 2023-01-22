#!/usr/bin/env python
# coding: utf-8

# In[1]:


# Importamos bibliotecas
import requests
from lxml import html
import time
import random
import pandas as pd
import json
import pymongo
from pymongo import MongoClient
import sys


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


def pandas_to_json(df):
    return json.loads(df.to_json(orient="records"))
    #return json.loads(df.apply(lambda x: decode_encode(x) if type(x) == type(["x"]) else x ).to_json(orient="records"))


# In[6]:


def main():
    params = sys.argv[1:]
    if len(params) > 0:
        area = " ".join(params)
    else:
        area = "computer"

    num_de_paginas = 1000
    print("busqueda")
    print(area)
    token = "e92b055534e1400b7259e1827871f932"


    pagina ="http://api.springernature.com/metadata/json?q=%22"+area.replace(" ", "%20")+"%22&api_key="+token
    #pagina ="http://api.springernature.com/openaccess/jats?q=subject:"+area.replace(" ", "%20")+"&api_key="+token
    headers = requests.utils.default_headers()

    headers.update(
        {
            'User-Agent': 'Chrome/96.0.4664.93',
        }
    )

    req =  requests.get(pagina, headers=headers)
    text = req.text
    dictio = json.loads(text)
    print(dictio.get("result"))

    db1 = acceder_una_coleccion("papers")
    db2 = acceder_una_coleccion("papers_2")

    for i in range (num_de_paginas):
        req =  requests.get(pagina, headers=headers)
        print(str(i))
        if req.status_code == 429:
            print('wait' +req.headers.get('Retry-After'))
            time.sleep(int(req.headers.get('Retry-After'))+1)
            req =  requests.get(pagina, headers=headers)
        #Convertimos a diccionario
        text = req.text
        dictio = json.loads(text)
        # dict_keys(['apiMessage', 'query', 'apiKey', 'nextPage', 'result', 'records', 'facets'])
        #papers.extend(dictio.get("records"))
        data_raw = pd.DataFrame.from_dict(dictio.get("records"))
        if(len(data_raw)==0):
            continue
        data = data_raw[data_raw["language"]=="en"]
        data = data[["creators","publisher",'title','abstract','subjects']]
        data = data.dropna()
        if(len(data)==0):
            continue
        data["creators"] = data["creators"].map(lambda x: [ a.get("creator") for a in x])
        data.columns = ['autores', 'fuente',"titulo","abstract", 'clase_primaria']
        data["pag_espec"] = " "
        data["n_citaciones"] = " "
        data["citado"] = " "
        #####################
        to_upload = pandas_to_json(data)
        save_mongo(to_upload, db1)
        save_mongo(to_upload, db2)
        pagina = "http://api.springernature.com" + dictio.get("nextPage")
    print("FIN")


# In[7]:


if __name__ == "__main__":
    main()


# In[ ]:




