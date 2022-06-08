#!/usr/bin/env python3

import requests

url = 'https://www.arcondicionado.cf/request'

data = {'temp1':101}

requests.post(url, json = data)
