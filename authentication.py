#!/usr/bin/env python

import getpass
import json
import os
import time

import keyring
import requests

class OMDBapi(object):
  """Defines schema of www.omdbapi.com."""
  searchurl = 'https://www.omdbapi.com/?'


class MovieDBAuthToken(object):
  """Defines login schema and headers"""
  apikey = '27d2f43a458ceac2a5aebaef45338a48'
  header = {'Accept' : 'application/json'}
  moviedbURL = 'https://api.themoviedb.org/3/search/tv?api_key=' + apikey


class TvdbAuthToken(object):
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

    if lastrefresh > 0 and lastrefresh < lastrefresh + 3600:
      print 'REFRESH'
      with open('.tvdbtoken.token', 'r') as tokenfile:
        originaltoken = tokenfile.read().rstrip('\n')
        auth_header = {'Authorization': 'Bearer ' + originaltoken}
        print 'Obtaining REFRESH Token'
        token = requests.get(tvdb_url + 'refresh_token', headers=auth_header)
        finaltoken = json.loads(token.text)
        os.utime('.tvdbtoken.token', (time.time(), time.time()))

    if lastrefresh > lastrefresh + 3600:
      print 'NEW No file'
      with open('.tvdbtoken.token', 'r+') as tokenfile:
        originaltoken = tokenfile.read().rstrip('\n')
        print 'Obtaining NEW token'
        token = requests.post(tvdb_url + 'login',
                              data=json.dumps(self.login_schema()),
                              headers=headers)
        finaltoken = json.loads(token.text)
        tokenfile.write(finaltoken['token'])

    if os.path.isfile('.tvdbtoken.token') is False:
      print 'NEW FILE'
      with open('.tvdbtoken.token', 'w+') as tokenfile:
        originaltoken = tokenfile.read().rstrip('\n')
        print 'Obtaining NEW token and writing to file'
        token = requests.post(tvdb_url + 'login',
                              data=json.dumps(self.login_schema()),
                              headers=headers)
        finaltoken = json.loads(token.text)
        tokenfile.write(finaltoken['token'])

    return finaltoken['token']