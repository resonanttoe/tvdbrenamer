import json
import os
import requests
import sys
import time


tvdb_url = 'https://api-beta.thetvdb.com/'
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
    seriesid = json.loads(search.text)['data'][0]['id']
    return seriesid

def episodename(seriesname, season, episode):
    '''Returns String of Episode name.

    Args:
    Seriesname - Searches using searchseries() for SeriesID number
    Season - AiredSeason number
    Episode - AiredEpisode Number

    Output:
    String of the episode name.
    '''
    seriesid = searchseries(seriesname)
    episodesurl = tvdb_url + 'series/' + str(seriesid) + '/episodes/query?' + \
                  'airedSeason=' + season + '&airedEpisode=' + episode
    episodesjson = requests.get(episodesurl, headers=auth_header)
    episodename = json.loads(episodesjson.text)['data'][0]['episodeName']
    return episodename


def findnamefromfile(inputfile):
    '''Gets the series name, season and episode id from file name.

    Input must be in the form of Series - Season XX - Episode XXX -.mp4.'''
    episodeinfo = [x.strip() for x in inputfile.split('-')]
    seriesname = episodeinfo[0]
    seasonnumber = episodeinfo[1].strip('Season ')
    episodenumber = episodeinfo[2].strip('Episode ')
    return seriesname, seasonnumber, episodenumber


def main():
    for (dirpath, dirname, filenames) in os.walk(sys.argv[1]):
        for filename in filenames:
            originalpath = sys.argv[1] + '/'
            originalfile = os.path.basename(filename)
            seriesabridged = findnamefromfile(originalfile)
            originalname, ext = os.path.splitext(originalfile)
            episode =  episodename(seriesabridged[0], seriesabridged[1], seriesabridged[2])
            os.rename(originalpath + filename, originalpath + originalname + ' ' + episode + str(ext))


if __name__ == '__main__':
    main()