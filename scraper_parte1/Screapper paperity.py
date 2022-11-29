#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests
from lxml import html
import time
import random
import pandas as pd


# In[4]:


#macros, se podren pasar como argumentos en futuras versiones
#hasta = '2021-12-31'
#desde = '2021-01-01'
area = 'advantage actor critic'
fuente = 'paperity'
# numero de paginas a revisar (paginas de 10 elementos)
num_de_paginas = 4 


# In[5]:


pagina = 'https://scholar.google.com/scholar?q='+area.replace(" ", "+")+'+source%3A'+fuente+'&oq='
headers = requests.utils.default_headers()

headers.update(
    {
        'User-Agent': 'Chrome/96.0.4664.93',
    }
)

req =  requests.get(pagina, headers=headers)
if req.status_code == 429:
    print('wait' +req.headers.get('Retry-After'))
    time.sleep(int(req.headers.get('Retry-After'))+1)
    req =  requests.get(pagina, headers=headers)
print(req)

#Convertimos a tree 
arbol_html = html.fromstring(req.content)


# In[9]:


papers = []


for i in range (num_de_paginas):
    print('Empiezo vuelta '+str(i)+' :'+time.strftime("%H:%M:%S", time.gmtime()))
    req =  requests.get(pagina, headers=headers)
    if req.status_code == 429:
        print('wait' +req.headers.get('Retry-After'))
        time.sleep(int(req.headers.get('Retry-After'))+1)
        req =  requests.get(pagina, headers=headers)
    #Convertimos a tree 
    arbol_html = html.fromstring(req.content)
    temp_res = arbol_html.xpath('//h3 [@class ="gs_rt"]/a/@href')
    for i in range(len(temp_res)):
        pag = temp_res[i]
        time.sleep(random.randint(1,2)*0.5)
        paper_res =  requests.get(pag, headers=headers)
        paper_dic = {}
        if paper_res.status_code == 429:
            print('wait' +paper_res.headers.get('Retry-After'))
            time.sleep(int(paper_res.headers.get('Retry-After'))+1)
            paper_res =  requests.get(pag, headers=headers)
        paper_arbol_html = html.fromstring(paper_res.content)
        # especifico de la pagina
        paper_dic["fuente"] = "paperity"
        paper_dic["titulo"] = paper_arbol_html.xpath('//h1/text()')
        paper_dic["autores"] = paper_arbol_html.xpath('//div [@class ="authors authors-full-width"]/h2/a/text()')
        paper_dic["abstract"] = paper_arbol_html.xpath('//div [@class ="abstract-text"]/p/text()')
        #generico
        paper_dic["n_citaciones"] = arbol_html.xpath('//a [@href ="'+pag+'"]/parent::*/parent::*/div [@class = "gs_fl"]/a [contains(text(),"Citado")]/text()')
        paper_dic["citado"] = arbol_html.xpath('//a [@href ="'+pag+'"]/parent::*/parent::*/div [@class = "gs_fl"]/a [contains(text(),"Citado")]/@href')
        papers.append(paper_dic)
        pagina = 'https://scholar.google.com/scholar?start='+str(10*(i+1))+'&q='+area.replace(" ", "+")+'+source%3A'+fuente+'&oq='


# In[11]:


for i in papers:
    print(i['titulo'])


# In[ ]:




