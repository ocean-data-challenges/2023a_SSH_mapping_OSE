import datetime
import logging
from datetime import timedelta

import numpy as np
import pandas 
import xarray as xr


def retrieve_list_of_files_from_url(path_catalog, path_data, prefix3='dt_',read_online=True):
    from urllib.request import Request, urlopen, urlretrieve
    from bs4 import BeautifulSoup
    def read_url(url):
        allfiles = list()
        url = url.replace(" ","%20") 
        req = Request(url)
        a = urlopen(req).read()
        soup = BeautifulSoup(a, 'html.parser')
        x = (soup.find_all('a'))
        for i in x:
            file_name = i.extract().get_text() 
            if prefix3 != None:
                if file_name[:3] == prefix3:
                    allfiles.append(file_name)  
            else:
                allfiles.append(file_name)

        return(allfiles)

    list_of_files=read_url(path_catalog)

    for i in range(np.shape(list_of_files)[0]):
        if read_online:
            list_of_files[i]=path_data+list_of_files[i]+"#mode=bytes"
        else:
            list_of_files[i]=path_data+list_of_files[i]
        
    return sorted(list_of_files)