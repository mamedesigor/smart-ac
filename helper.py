#!/usr/bin/env python3

import requests

url = 'https://www.arcondicionado.cf/request'
url2 = 'http://127.0.0.1:3031/request'

data = {'temp1':101, 'temp2':666}

requests.post(url2, json = data)
