#!/usr/bin/env python

import datetime
import json
import os
import sys

import authentication as auth
import requests


class EpNotFoundError(ValueError):
  pass


class TokenInvalidError(ValueError):
  pass


class SeriesNotFoundError(ValueError):
  pass


class TVDBAuth(object):
  tvdb_url = 'https://api-beta.thetvdb.com/'
  tvdbheaders = {'content-type': 'application/json'}
  token = auth.TvdbAuthToken()
  tvdbauth_header = {'Authorization': 'Bearer ' + token.getrefreshtoken()}


class WWE(object):
  """WWE will query TMDB for Episode info.

      Takes input in the form of WWE.<Showname>.<Year>.<Month>.<Day>.<JUNK>
      and return season episode and date.
  """
  tmdbapistring = '?api_key=' + auth.MovieDBAuthToken.apikey

  def wwecontroller(self, inputfile):
    """Controller function for WWE Filenames."""
    if len(inputfile.split(' - ')) == 3:
      serieslist = inputfile.split(' - ')
      indate = serieslist[2]
      seriesname = serieslist[0]
    else:
      serieslist = inputfile.split('.')
      indate = serieslist[4] + '-' + serieslist[3] + '-' + serieslist[2]
      seriesname = serieslist[0] + ' ' + serieslist[1]
    reversedate = '-'.join(indate.split('-')[::-1])
    seriesid = self.wwesearchseries(seriesname)
    seasonnumber = str(self.findseasonnumber( \
        seriesid, reversedate.split('-')[0])).zfill(2)
    episodenumber = str(self.matchdateinseason( \
        seriesid, seasonnumber, reversedate)[0]).zfill(2)
    outdate = str(self.matchdateinseason( \
        seriesid, seasonnumber, reversedate)[1])
    return seriesname, seasonnumber, episodenumber, outdate

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

  def matchdateinseason(self, seriesid, season_number, indate):
    """Using the season number, match the details of the episode."""
    searchurl = 'http://api.themoviedb.org/3/tv/' + str(seriesid) + '/season/' \
                + str(season_number) + self.tmdbapistring
    seasoninfo = requests.get(searchurl, headers=auth.MovieDBAuthToken.header)
    seasonjson = json.loads(seasoninfo.text)
    indate = datetime.datetime.strptime(indate, '%Y-%m-%d')
    mindatecush = indate - datetime.timedelta(days=2)
    maxdatecush = indate + datetime.timedelta(days=2)
    for elem in seasonjson['episodes']:
      if mindatecush <= datetime.datetime.strptime(elem['air_date'], '%Y-%m-%d') <= maxdatecush:
        return elem['episode_number'], elem['air_date']


class TvShow(object):
  """TvShow class queries TVDB.com for Show info.

  Input:
    <Tvshow> - SxxExx -.mp4
  """

  def searchseries(self, seriesname):
    """Searches for a series based on name, returns ID."""
    searchurl = TVDBAuth.tvdb_url + 'search/series?name='
    search = requests.get(searchurl + seriesname,
                          headers=TVDBAuth.tvdbauth_header)
    if search.status_code == int(404):
      raise SeriesNotFoundError('Series Name "%s" incorrect' % seriesname)
    if search.status_code == int(401):
      raise TokenInvalidError('Token expired or non-existant')
    else:
      seriesid = json.loads(search.text)['data'][0]['id']
    return seriesid

  def episodename(self, seriesname, season, episode):
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
    seriesid = self.searchseries(seriesname)
    episodesurl = TVDBAuth.tvdb_url + 'series/' + str(seriesid) + \
                  '/episodes/query?' + 'airedSeason=' + season + \
                  '&airedEpisode=' + episode
    episodesjson = requests.get(episodesurl,
                                headers=TVDBAuth.tvdbauth_header)
    if episodesjson.status_code == int(404):
      raise EpNotFoundError('Episode or Season incorrect')
    if episodesjson.status_code == int(401):
      raise TokenInvalidError('Token expired or non-existant')
    else:
      endepisodename = json.loads(episodesjson.text)['data'][0]['episodeName']
    return endepisodename

  def findnamefromfile(self, inputfile):
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
        print 'Renaming to -', finalname
    #    os.rename(originalpath + filename, originalpath + finalname + str(ext))
      elif filename.endswith('- .mp4'):
        seriesabridged = TvShow.findnamefromfile(originalfile)
        episode = TvShow.episodename(seriesabridged[0], seriesabridged[1],
                              seriesabridged[2])
        print 'Renaming to - ', originalname + ' ' + episode + str(ext)
        os.rename(originalpath + filename, originalpath + originalname + ' '
                  + episode + str(ext))
      else:
        pass


if __name__ == '__main__':
  main()
