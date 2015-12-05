#!/usr/bin/env python

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


class TvShow(object):
  """TvShow class queries TVDB.com for Show info.
  Input:
    <Tvshow> - SxxExx -.mp4
  """

  def editcontroller(self, filename):
    """Controller for files that match Title - SxxExx -.mp4 file name."""
    originalpath = sys.argv[1] + '/'
    originalfile = os.path.basename(filename)
    originalname, ext = os.path.splitext(originalfile)
    seriesabridged = self.findnamefromfile(originalfile)
    episode = self.episodename(seriesabridged[0], seriesabridged[1],
                               seriesabridged[2])
    if episode is None:
      print 'Error found'
    else:
      print 'Renaming to - ', originalname + ' ' + episode + str(ext)
      os.rename(originalpath + filename, originalpath + originalname
                + episode + str(ext))

  def dotcontroller(self, filename):
    """Controller for files that match Title.SxxExx.Junk.mp4 file name."""
    pass

  def searchseries(self, seriesname):
    """Searches for a series based on name, returns ID."""
    searchurl = TVDBAuth.tvdb_url + 'search/series?name='
    search = requests.get(searchurl + seriesname,
                          headers=TVDBAuth.tvdbauth_header)
    if search.status_code == int(404):
      print 'Series Name "%s" incorrect' % seriesname
      return None
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
      print 'No Episode found for %s' % seriesname, season, episode
      return None
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
  for (dirpath, dirname, filenames) in os.walk(sys.argv[1]):
    for filename in filenames:
      if filename.startswith('.'):
        pass
      tvshows = TvShow()
      if filename.endswith('- .mp4'):
        tvshows.editcontroller(filename)
      elif filename.endswith('.mp4') and filename.split('.mp4')[0] is not '':
        tvshows.dotcontroller(filename)

if __name__ == '__main__':
  main()
