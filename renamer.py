#!/usr/bin/env python

import json
import os
import requests
import sys
import time

import authentication as auth


tvdb_url = 'https://api-beta.thetvdb.com/'
headers = {'content-type': 'application/json'}
token = auth.AuthToken()
auth_header = {'Authorization': 'Bearer ' + token.getrefreshtoken()}


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
  endepisodename = json.loads(episodesjson.text)['data'][0]['episodeName']
  return endepisodename


def findnamefromfile(inputfile):
  '''Gets the series name, season and episode id from file name.
  Input must be in the form of Series - SXX - EXXX -.mp4.
  '''
  episodeinfo = [x.strip() for x in inputfile.split('-')]
  seriesname = episodeinfo[0]
  seasonepnumber = episodeinfo[1].strip('S')
  seasonnumber = seasonepnumber.split('E')[0]
  episodenumber = seasonepnumber.split('E')[1]
  return seriesname, seasonnumber, episodenumber


def main():
  for (dirpath, dirname, filenames) in os.walk(sys.argv[1]):
    for filename in filenames:
      if filename.startswith('.'):
        pass
      if filename.endswith('- .mp4'):
        originalpath = sys.argv[1] + '/'
        originalfile = os.path.basename(filename)
        seriesabridged = findnamefromfile(originalfile)
        originalname, ext = os.path.splitext(originalfile)
        episode =  episodename(seriesabridged[0], seriesabridged[1],
                               seriesabridged[2])
        print 'Renaming to - ', originalname + ' ' + episode + str(ext)
        os.rename(originalpath + filename, originalpath + originalname + ' '
                  + episode + str(ext))
      else:
        pass


if __name__ == '__main__':
  main()
