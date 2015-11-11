#!/usr/bin/env python

import getpass
import json
import os
import time

import keyring
import requests


class AuthToken:
  """Defines login schema and retrieves login/refresh token."""

  def login_schema(self):
    """Defines the login Schema for Refresh token."""
    apikey = '4C2681B7D3922F1A'
    username = raw_input('TVDB.com Username:')
    if keyring.get_password('tvdbrenamer', username) is not None:
      password = keyring.get_password('tvdbrenamer', username)
    else:
      password = getpass.getpass('TVDB.com Password:')
      keyring.set_password('tvdbrenamer', username, password)
    return {'apikey': apikey, 'username': username, 'userpass': str(password)}


  def getrefreshtoken(self):
    """Get a JWT token or refreshes if it exists and is less than an hour."""
    tvdb_url = 'https://api-beta.thetvdb.com/'
    headers = {'content-type': 'application/json'}
    lastrefresh = 0
    if os.path.isfile('.tvdbtoken.token') is True:
      lastrefresh = os.path.getmtime('.tvdbtoken.token')
    print lastrefresh
    with open('.tvdbtoken.token', 'ab+') as tokenfile:
      originaltoken = tokenfile.read().rstrip('\n')
      print originaltoken
      if lastrefresh is 0:
        print 'Obtaining NEW token'
        token = requests.post(tvdb_url + 'login',
                              data=json.dumps(self.login_schema()),
                              headers=headers)
      elif lastrefresh <= lastrefresh + 3600:
        auth_header = {'Authorization': 'Bearer ' + originaltoken}
        print auth_header
        print 'Obtaining REFRESH Token'
        token = requests.get(tvdb_url + 'refresh_token', headers=auth_header)
      finaltoken = json.loads(token.text)
      print finaltoken
      tokenfile.write(finaltoken['token'])
    if 'Error' in finaltoken:
      raise ValueError('Username or Password not found/incorrect')
    else: 
      return finaltoken['token']
