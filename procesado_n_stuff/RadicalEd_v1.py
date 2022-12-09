#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests
from lxml import html
import time
import random
import pandas as pd


# In[ ]:


######################
#MACROS
######################

#macros, se podren pasar como argumentos en futuras versiones
#hasta = '2021-12-31'
#desde = '2021-01-01'
area = 'machine learning'
fuente = 'arxiv'
# numero de paginas a revisar (paginas de 10 elementos)
num_de_paginas = 20 
start=210 


# In[ ]:


def get_tor_session():
    session = requests.session()
    # Tor uses the 9050 port as the default socks port
    session.proxies = {'http':  'socks5://127.0.0.1:9050',
                       'https': 'socks5://127.0.0.1:9050'}
    return session


# In[ ]:


def main():
    #https://scholar.google.com/scholar?hl=es&as_sdt=0,5&q=machine+learning+source:arxiv&btnG=
    pagina = 'https://scholar.google.com/scholar?hl=es&as_sdt=0%2C5&q='+area.replace(" ", "+")+'+source%3A'+fuente+'&oq='
    headers = requests.utils.default_headers()
    session = get_tor_session()
    headers.update(
        {
            'User-Agent': "Mozilla/5.0 (X11; Linux x86_64; rv:12.0) Gecko/20100101 Firefox/12.0",
            'Accept':'text/html',
            "Referer" : "http://www.google.com/"
        }
    )
    
    req =  session.get(pagina, headers=headers)
    if req.status_code == 429:
        print('1wait 429',session.get("http://httpbin.org/ip").text )
        #time.sleep(int(req.headers.get('Retry-After'))+1)
        #req =  requests.get(pagina, headers=headers)
    print(req)
    
    #Convertimos a tree 
    arbol_html = html.fromstring(req.content)
    papers = []


    for i in range (num_de_paginas):
        print('Empiezo vuelta '+str(i)+' :'+time.strftime("%H:%M:%S", time.gmtime()))
        pagina = 'https://scholar.google.com/scholar?start='+str((10*(i)+start ))+'&q='+area.replace(" ", "+")+'+source%3A'+fuente+'&oq='
        req =  session.get(pagina, headers=headers)
        if req.status_code == 429:
            print('2wait 429',session.get("http://httpbin.org/ip").text )
            #time.sleep(int(req.headers.get('Retry-After'))+1)
            #req =  session.get(pagina, headers=headers)
        #Convertimos a tree 
        arbol_html = html.fromstring(req.content)
        temp_res = arbol_html.xpath('//h3 [@class ="gs_rt"]/a/@href')
        for i in range(len(temp_res)):
            pag = temp_res[i]
            time.sleep(random.randint(1,10)*0.5)
            paper_res =  session.get(pag, headers=headers)
            paper_dic = {}
            if paper_res.status_code == 429:
                print('3wait 429',session.get("http://httpbin.org/ip").text )
                #time.sleep(int(paper_res.headers.get('Retry-After'))+1)
                #paper_res =  requests.get(pag, headers=headers)
            paper_arbol_html = html.fromstring(paper_res.content)
            # especifico de la pagina
            paper_dic["fuente"] = "arxiv.org"
            paper_dic["titulo"] = paper_arbol_html.xpath('//h1 [@class ="title mathjax"]/text()')
            paper_dic["autores"] = paper_arbol_html.xpath('//div [@class ="authors"]/a/text()')
            paper_dic["abstract"] = paper_arbol_html.xpath('//blockquote [@class ="abstract mathjax"]/text()')
            paper_dic["clase_primaria"] = paper_arbol_html.xpath('//span [@class ="primary-subject"]/text()')
            paper_dic["otras_clases"] = paper_arbol_html.xpath('//td [@class ="tablecell subjects"]/text()')
            paper_dic["clase_primaria"] = paper_arbol_html.xpath('//span [@class ="primary-subject"]/text()')
            #generico
            paper_dic["n_citaciones"] = arbol_html.xpath('//a [@href ="'+pag+'"]/parent::*/parent::*/div [@class = "gs_fl"]/a [contains(text(),"Citado")]/text()')
            paper_dic["citado"] = arbol_html.xpath('//a [@href ="'+pag+'"]/parent::*/parent::*/div [@class = "gs_fl"]/a [contains(text(),"Citado")]/@href')
            papers.append(paper_dic)
            
        
        
    titulos = []
    abstractos = []
    clase_pri = []
    clase_otr = []
    for papel in papers:
        try:
            titulos.append(papel["titulo"][0])
            abstractos.append(papel["abstract"][1])
            clase_pri.append(papel["clase_primaria"][0])
        except:
            continue
        try:
            clase_otr.append(papel["otras_clases"][1])
        except:
            clase_otr.append("")
    
    
    
    data = {'titulo': titulos,
        'abstract': abstractos,
        'clase_pri': clase_pri,
        'clase_otr': clase_otr
        }

    df = pd.DataFrame(data)
    filepath = "data_test.csv"
    df.to_csv(filepath,index=False)  
    

if __name__ == "__main__":
    main()

