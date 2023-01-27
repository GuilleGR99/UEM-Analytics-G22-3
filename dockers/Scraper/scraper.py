# %%

# *Importamos librerias
import requests
from lxml import html
import time
import random
import json
import pymongo
from pymongo import MongoClient

# %%

# *macros, se podren pasar como argumentos en futuras versiones
#hasta = '2021-12-31'
#desde = '2021-01-01'
# area = 'advantage actor critic'
# fuente = 'arxiv'
# numero de paginas a revisar (paginas de 10 elementos)
num_de_paginas = 1


# %%

# !La clase primaria de springer no es correcto, tiene un html generico para que se ejecute sin dar fallo   
# !Cuando google te banea, el bucle for que itera las pagina especificas falla

info_fuentes = []

info_fuente_arvix = {
    'area':'advantage actor critic',
    'fuente':'arxiv',
    'titulo':'//h1 [@class ="title mathjax"]/text()',
    'autores':'//div [@class ="authors"]/a/text()',
    'abstract':'//blockquote [@class ="abstract mathjax"]/text()',
    'clase_primaria':'//span [@class ="primary-subject"]/text()',
    # 'otras_clases':'//td [@class ="tablecell subjects"]/text()',
}
info_fuente_arvix['pagina'] = 'https://scholar.google.com/scholar?q='+info_fuente_arvix.get("area").replace(" ", "+")+'+source%3A'+info_fuente_arvix.get("fuente")+'&oq='
info_fuentes.append(info_fuente_arvix)

info_fuente_springer = {
    'area':'advantage actor critic',
    'fuente':'springer',
    'titulo':'//h1 [@class ="c-article-title"]/text()',
    'autores':'//li [@class ="c-article-author-list__item"]/a/text()',
    'abstract':'//div [@class ="c-article-section__content"][@id="Abs1-content"]/p/text()',
    'clase_primaria':'//li [@class ="c-article-subject-list__subject"]/span/text()',
    # 'otras_clases':'',
}
info_fuente_springer['pagina'] = 'https://scholar.google.com/scholar?q='+info_fuente_springer.get("area").replace(" ", "+")+'+source%3A'+info_fuente_springer.get("fuente")+'&oq='
info_fuentes.append(info_fuente_springer)

info_fuente_SSRN = {
    'area':'advantage actor critic',
    'fuente':'SSRN',
    'titulo':'//h1/text()',
    'autores':'//div [@class ="authors authors-full-width"]/h2/a/text()',
    'abstract':'//div [@class ="abstract-text"]/p/text()',
    'clase_primaria':'//vacio',
    # 'otras_clases':'',
}
info_fuente_SSRN['pagina'] = 'https://scholar.google.com/scholar?q='+info_fuente_SSRN.get("area").replace(" ", "+")+'+source%3A'+info_fuente_SSRN.get("fuente")+'&oq='
info_fuentes.append(info_fuente_SSRN)

info_fuente_cambridge = {
    'area':'machine learning',
    'fuente':'cambridge',
    'titulo':'//h1 [@data-v-0950e612=""]/text()',
    'autores':'//div [@class="row contributor-type"]/div/a [@class="app-link app-link__text app-link--accent"]/span/text()',
    'abstract':'//div [@class="abstract-content"]/div/div/p/text()',
    'clase_primaria':'//div [@class="row keywords__pills"]/a/span/text()',
    # 'otras_clases':'',
}
info_fuente_cambridge['pagina'] = 'https://scholar.google.com/scholar?q='+info_fuente_cambridge.get("area").replace(" ", "+")+'+source%3A'+info_fuente_cambridge.get("fuente")+'&oq='
info_fuentes.append(info_fuente_cambridge)

# %%
papers = []

for k in range(len(info_fuentes)):
    headers = requests.utils.default_headers()

    headers.update(
        {
            'User-Agent': 'Chrome/96.0.4664.93',
        }
    )

    req =  requests.get(info_fuentes[k].get('pagina'), headers=headers)
    if req.status_code == 429:
        # print('wait' +req.headers.get('Retry-After'))
        time.sleep(int(req.headers.get('Retry-After'))+1)
        req =  requests.get(info_fuentes[k].get('pagina'), headers=headers)
    # print(req)

    #Convertimos a tree 
    arbol_html = html.fromstring(req.content)

    # start=10 

    for i in range (num_de_paginas):
        # print('Empiezo vuelta '+str(i)+' :'+time.strftime("%H:%M:%S", time.gmtime()))
        req =  requests.get(info_fuentes[k].get('pagina'), headers=headers)
        # print('scrapig google', info_fuentes[k].get('pagina'))

        # repetir despues del tiempo de espera
        if req.status_code == 429:
            # print('wait' +req.headers.get('Retry-After'))
            time.sleep(int(req.headers.get('Retry-After'))+1)
            req =  requests.get(info_fuentes[k].get('pagina'), headers=headers)

        # Convertimos a tree 
        arbol_html = html.fromstring(req.content)
        temp_res = arbol_html.xpath('//h3 [@class ="gs_rt"]/a/@href')

        for j in range(len(temp_res)):
            paper_dic = {}
            # print('scraping a', temp_res[j])
            pag = temp_res[j]
            time.sleep(random.randint(1,2)*0.5)
            paper_res =  requests.get(pag, headers=headers)
            
            if paper_res.status_code == 429:
                # print('wait' +paper_res.headers.get('Retry-After'))
                time.sleep(int(paper_res.headers.get('Retry-After'))+1)
                paper_res =  requests.get(pag, headers=headers)
            paper_arbol_html = html.fromstring(paper_res.content)

            # especifico de la pagina
            paper_dic['fuente'] = info_fuentes[k]['fuente']
            paper_dic['titulo'] = paper_arbol_html.xpath(info_fuentes[k]['titulo'])
            paper_dic['autores'] = paper_arbol_html.xpath(info_fuentes[k]['autores'])
            paper_dic['abstract'] = paper_arbol_html.xpath(info_fuentes[k]['abstract'])
            paper_dic['clase_primaria'] = paper_arbol_html.xpath(info_fuentes[k]['clase_primaria'])
            # paper_dic['otras_clases'] = paper_arbol_html.xpath(info_fuentes[k]['otras_clases'])
            #metadata
            paper_dic['pag_espec'] = pag
            paper_dic['pag_espec'] = info_fuentes[k].get('pagina')
            #generico
            paper_dic["n_citaciones"] = arbol_html.xpath('//a [@href ="'+pag+'"]/parent::*/parent::*/div [@class = "gs_fl"]/a [contains(text(),"Citado")]/text()')
            paper_dic["citado"] = arbol_html.xpath('//a [@href ="'+pag+'"]/parent::*/parent::*/div [@class = "gs_fl"]/a [contains(text(),"Citado")]/@href')
            papers.append(paper_dic)
        info_fuentes[k]['pagina'] = 'https://scholar.google.com/scholar?start='+str(10*(i+1))+'&q='+info_fuentes[k].get("area").replace(" ", "+")+'+source%3A'+info_fuentes[k].get("fuente").split('.')[0]+'&oq='

# %%
# *si los datos clave de un documento no existen este es borrado, el bucle for no actualiza el tamaño de los papers 
# *segun se borran con lo cual acaba indicando que hay mas de los que son realmente y da error al borrar
# *se resta a item los borrados para obtener la cantidad verdadera
borrados = 0
for item in range(len(papers)):
    if not papers[item-borrados].get('titulo'):
        papers.pop(item-borrados)
        borrados+=1
    elif not papers[item-borrados].get('abstract'):
        papers.pop(item-borrados)
        borrados+=1
# print(f'Se han borrado {borrados} elemento invalidos')

# *comprobacion de papers
# print('cantidad de papers:', len(papers))

# *guarda la info es .json
# with open('papers.json', 'w') as file:
#     json.dump(papers, indent=7, fp=file)

# %%

# *inicio de sesion en mongo
# *Introduce tu nombre como input o ponlo como variable [Miguel, Lucas, Julieta, Guillermo]
nombre = 'Guillermo'
# password = input('introduce pass')
password = 'aplicacionesytendenciasdelanalisisdedatos2022'
cluster = MongoClient(f'mongodb+srv://{nombre}:{password}@cluster0.rnxayot.mongodb.net/?retryWrites=true&w=majority')
# *seleccion de la coleccion de datos
db = cluster['papers']
collection = db['papers']

# %%

# *elimina todo el contenido de la coleccion
# collection.delete_many({})
# *cuenta los documentos de la coleccion
# collection.count_documents({})

# %%
# *la ejecució normal no cargaria el documento .json
# papers = json.load(open('papers.json'))

# %%

# *guarda papers en mongo db, si la coleccion esta vacia inserta el primero, 
# *si no esta vacio compara si alguno de los documentos en la coleccion tiene 
# *el mismo titulo que el que se va a insertar, si no es asi se inserta.
cantidad_inicial = collection.count_documents({})
try:
    for i in range(len(papers)):
        if collection.count_documents({}) == 0:
            collection.insert_one(papers[i])
        try:
            collection.find({'titulo':papers[i]['titulo']})[0]
        except:
            collection.insert_one(papers[i])
    print('Creación correcta') 
except Exception as exception:
    print(exception)
print('Se han realizado', collection.count_documents({}) - cantidad_inicial , 'nuevas insercciones')    

# %%


# %%


# %%


# %%


# %%


# %%


# %%


# %%


# %%


# %%


# %%



