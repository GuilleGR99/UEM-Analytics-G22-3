#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#### requiere:

## pip install pysocks
##  pip install requests[socks]
import requests
from stem import Signal
from stem.control import Controller
import socks, socket
import time
def changeIp(controller):
    controller.signal(Signal.NEWNYM)
    time.sleep(controller.get_newnym_wait())
def get_tor_session():
    session = requests.session()
    # Tor uses the 9050 port as the default socks port
    session.proxies = {'http':  'socks5://127.0.0.1:9050',
                       'https': 'socks5://127.0.0.1:9050'}
    return session


def main():
    # Make a request through the Tor connection
    # IP visible through Tor
    session = get_tor_session()
    print("prueba tor 1: ",session.get("http://httpbin.org/ip").text)
    # Above sh
    # Following prints your normal public IP
    print("prueba tor my ip: ",requests.get("http://httpbin.org/ip").text)
    
    with Controller.from_port(port=9051) as controller:
        socks.setdefaultproxy(proxy_type=socks.PROXY_TYPE_SOCKS5, addr="127.0.0.1", port=9050)
        socket.socket = socks.socksocket
        controller.authenticate()
        print("prueba tor 4: ",requests.get("http://httpbin.org/ip").text)
        changeIp(controller)
        print("prueba tor 3: ",requests.get("http://httpbin.org/ip").text)
    
if __name__ == "__main__":
    main()


# In[2]:


#print("prueba tor my ip: ",requests.get("http://httpbin.org/ip").text)


# In[ ]:




