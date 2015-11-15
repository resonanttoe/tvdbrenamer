#!/usr/bin/env python

import json
import os
import sys
import time

import authentication as auth
import requests


class EpNotFoundError(ValueError):
  pass


class TokenInvalidError(ValueError):
  pass


class SeriesNotFoundError(ValueError):
  pass

tvdb_url = 'https://api-beta.thetvdb.com/'
headers = {'content-type': 'application/json'}
token = auth.AuthToken()
auth_header = {'Authorization': 'Bearer ' + token.getrefreshtoken()}


def searchseries(seriesname):
  """Searches for a series based on name, returns ID."""
  searchurl = tvdb_url + 'search/series?name='
  search = requests.get(searchurl + seriesname, headers=auth_header)
  if search.status_code == int(404):
    raise SeriesNotFoundError('Series Name "%s" incorrect' % seriesname)
  if search.status_code == int(401):
    raise TokenInvalidError('Token expired or non-existant')
  else:
    seriesid = json.loads(search.text)['data'][0]['id']
  return seriesid


def episodename(seriesname, season, episode):
  """Returns String of Episode name.

  Args:
    seriesname: Searches using searchseries() for SeriesID number
    season:  AiredSeason number
    episode:  AiredEpisode Number
  Returns:
    endepisodename: String of the episode name.

  Raises:
    EpNotFoundError: if status code is 404
    TokenInvalidError: if status code is 401
  """
  seriesid = searchseries(seriesname)
  episodesurl = tvdb_url + 'series/' + str(seriesid) + '/episodes/query?' + \
                'airedSeason=' + season + '&airedEpisode=' + episode
  episodesjson = requests.get(episodesurl, headers=auth_header)
  if episodesjson.status_code == int(404):
    raise EpNotFoundError('Episode or Season incorrect')
  if episodesjson.status_code == int(401):
    raise TokenInvalidError('Token expired or non-existant')
  else:
    endepisodename = json.loads(episodesjson.text)['data'][0]['episodeName']
  if '/' in episodename:
    episodename = episodename.replace('/', '-')  
  return endepisodename


def findnamefromfile(inputfile):
  """Gets the series name, season and episode id from file name.

  Args:
    inputfile: Input must be in the form of Series - SXX - EXXX -.mp4.
  Returns:
    Tuple of TV show name, Season number and episode number.
  """
  episodeinfo = [x.strip() for x in inputfile.split(' - ')]
  seriesname = episodeinfo[0]
  seasoneplist = episodeinfo[1].split('-')[0]
  seasonepnumber = seasoneplist.strip('S')
  seasonnumber = seasonepnumber.split('E')[0]
  episodenumber = seasonepnumber.split('E')[1].rstrip()
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
        episode = episodename(seriesabridged[0], seriesabridged[1],
                              seriesabridged[2])
        print 'Renaming to - ', originalname + ' ' + episode + str(ext)
        os.rename(originalpath + filename, originalpath + originalname + ' '
                  + episode + str(ext))
      else:
        pass


if __name__ == '__main__':
  main()
