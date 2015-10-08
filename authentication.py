import json
import requests
import time


tvdb_url = 'https://api-dev.thetvdb.com/'
headers = {'content-type': 'application/json'}


def login_schema():
    '''Defines the login Schema for Refresh token.'''
    ##TODO Fix this, its awful and has my password.
    apikey = None
    username = None
    password = None
    return {'apikey': apikey, 'username': username, 'userpass': password}


def getrefreshtoken():
    ''' Get a JWT token or refreshes if it exists and is less than an hour.'''
    lastrefresh = None
    if lastrefresh == None:
        token = requests.post(tvdb_url + 'login', 
                              data=json.dumps(login_schema()), headers=headers)
        lastrefresh = time.time()
    elif lastrefresh < lastrefresh + 3600:
        token = requests.get(tvdb_url + 'login', 
                             data=json.dumps(login_schema()), headers=headers)
        lastrefresh = time.time()
    finaltoken = json.loads(token.text)
    return finaltoken['token']

auth_header = {'Authorization': 'Bearer ' + getrefreshtoken()}

def searchseries(seriesname):
    '''Searches for a series based on name, returns ID.'''
    searchurl = tvdb_url + 'search/series?name='
    search = requests.get(searchurl + seriesname, headers=auth_header)
    return json.loads(search.text)['data'][1]['id']


def getepisodes(seriesid):
    '''Returns JSON episodes for series based on numeric ID.'''
    seriesid = searchseries(seriesid)
    episodesurl = tvdb_url + 'series/' + str(seriesid) + '/episodes'
    episodesjson = requests.get(episodesurl, headers=auth_header)
    print(json.loads(episodesjson.text)['data'][0])


if __name__ == '__main__':
    getepisodes("Red Dwarf")