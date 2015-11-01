#!/usr/bin/env python

import json
import requests
import time

class AuthToken:

    def login_schema(self):
        '''Defines the login Schema for Refresh token.'''
        ##TODO Fix this, its awful and has my password.
        apikey = '4C2681B7D3922F1A'
        username = 'resonance'
        password = 'NgZPnL749Ut^L)NfU9)oAN.3H'
        return {'apikey': apikey, 'username': username, 'userpass': password}


    def getrefreshtoken(self):
        ''' Get a JWT token or refreshes if it exists and is less than an hour.'''
        tvdb_url = 'https://api-beta.thetvdb.com/'
        headers = {'content-type': 'application/json'}
        lastrefresh = None
        if lastrefresh == None:
            token = requests.post(tvdb_url + 'login', 
                                  data=json.dumps(self.login_schema()), headers=headers)
            lastrefresh = time.time()
        elif lastrefresh < lastrefresh + 3600:
            token = requests.get(tvdb_url + 'login', 
                                 data=json.dumps(self.login_schema()), headers=headers)
            lastrefresh = time.time()
        finaltoken = json.loads(token.text)
        return finaltoken['token']