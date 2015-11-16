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
tvdbheaders = {'content-type': 'application/json'}
token = auth.TvdbAuthToken()
tvdbauth_header = {'Authorization': 'Bearer ' + token.getrefreshtoken()}


class WWE(object):
  """ WWE will query TMDB for Episode info.

      Takes input in the form of WWE.<Showname>.<Year>.<Month>.<Day>.<JUNK>
      and return season episode and date.
  """
  tmdbapistring = '?api_key=' + auth.MovieDBAuthToken.apikey

  def wwecontroller(self, inputfile):
    serieslist = inputfile.split('.')
    seriesname = serieslist[0] + ' ' + serieslist[1]
    date = serieslist[2] + '-' + serieslist[3] + '-' + serieslist[4]
    seriesid = self.wwesearchseries(seriesname)
    seasonnumber = str(self.findseasonnumber(seriesid, serieslist[2])).zfill(2)
    episodenumber = str(self.matchdateinseason( \
        seriesid, seasonnumber, date)).zfill(2)
    return seriesname, seasonnumber, episodenumber, date

  def wwesearchseries(self, seriesname):
    """Searchs TMDB for the WWE series name, returns ID value."""

    searchurl = auth.MovieDBAuthToken.moviedbURL
    search = requests.get(searchurl + '&query=' + seriesname,
                          headers=auth.MovieDBAuthToken.header)
    seriesid = json.loads(search.text)['results'][0]['id']
    return seriesid

  def findseasonnumber(self, seriesid, year):
    """Fetches JSON overview from TMDB, searches for year, returns season."""
    searchurl = 'http://api.themoviedb.org/3/tv/' + str(seriesid) \
                + self.tmdbapistring
    showlist = requests.get(searchurl, headers=auth.MovieDBAuthToken.header)
    showlist = json.loads(showlist.text)['seasons']
    for elem in showlist:
      if int(elem['air_date'].split('-')[0]) == int(year):
        return elem['season_number']

  def matchdateinseason(self, seriesid, season_number, date):
    """Using the season number, match the details of the episode."""
    searchurl = 'http://api.themoviedb.org/3/tv/' + str(seriesid) + '/season/' \
                + str(season_number) + self.tmdbapistring
    seasoninfo = requests.get(searchurl, headers=auth.MovieDBAuthToken.header)
    seasonjson = json.loads(seasoninfo.text)
    for elem in seasonjson['episodes']:
      if str(elem['air_date']) == date:
        return elem['episode_number']


def searchseries(seriesname):
  """Searches for a series based on name, returns ID."""
  searchurl = tvdb_url + 'search/series?name='
  search = requests.get(searchurl + seriesname, headers=tvdbauth_header)
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
  episodesjson = requests.get(episodesurl, headers=tvdbauth_header)
  if episodesjson.status_code == int(404):
    raise EpNotFoundError('Episode or Season incorrect')
  if episodesjson.status_code == int(401):
    raise TokenInvalidError('Token expired or non-existant')
  else:
    endepisodename = json.loads(episodesjson.text)['data'][0]['episodeName']
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
  wwe = WWE()
  for (dirpath, dirname, filenames) in os.walk(sys.argv[1]):
    for filename in filenames:
      if filename.startswith('.'):
        pass
      originalpath = sys.argv[1] + '/'
      originalfile = os.path.basename(filename)
      originalname, ext = os.path.splitext(originalfile)
      if originalname.startswith('WWE') is True:
        print 'WWE file found!'
        renamed = wwe.wwecontroller(originalname)
        finalname = str(renamed[0]) + ' - S' + str(renamed[1]) + 'E' + \
                    str(renamed[2]) + ' - ' + str(renamed[3])
        print 'Renaming to -', str(renamed[0]) + ' - S' + str(renamed[1]) + \
              'E' + str(renamed[2]) + ' - ' + str(renamed[3])
#        os.rename(originalpath + filename, originalpath + finalname + str(ext))
      elif filename.endswith('- .mp4'):
        seriesabridged = findnamefromfile(originalfile)
        episode = episodename(seriesabridged[0], seriesabridged[1],
                              seriesabridged[2])
        print 'Renaming to - ', originalname + ' ' + episode + str(ext)
        os.rename(originalpath + filename, originalpath + originalname + ' '
                  + episode + str(ext))
      else:
        pass


if __name__ == '__main__':
  main()
