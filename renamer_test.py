#!/usr/bin/env python

import mock
import unittest

import renamer

tvshow = renamer.TvShow()

class KnownValues(unittest.TestCase):

  goodseriesid = ((76703, 'Pokemon'),
                  (76924, 'Black Books'),
                  (76736, 'Blackadder'))

  goodids = (('Pokemon - S01E01 -.mp4', ('Pokemon', '01', '01')),
             ('Red Dwarf - S08E03 -.mp4', ('Red Dwarf', '08', '03')),
             ('Black Books - S03E02 -.mp4', ('Black Books', '03', '02')),
             ('Hawaii Five-0 - S02E10 -.mp4', ('Hawaii Five-0', '02', '10')))

  goodfilenames = ((('Pokemon', '01', '01'), u'Pok\xe9mon! I Choose You!'),
                   (('Red Dwarf', '08', '03'), 'Back in the Red (3)'),
                   (('Black Books', '03', '02'), 'Elephants and Hens'))

  def test_seriesid(self):
    """seriesid should return good values from search."""
    for seriesid, seriesname in self.goodseriesid:
      result = tvshow.searchseries(seriesname)
      self.assertEqual(seriesid, result)

  def test_findnamefromfile(self):
    """Should return Series name, Season and episode numbers."""
    for filename, fileids in self.goodids:
      result = tvshow.findnamefromfile(filename)
      self.assertEqual(fileids, result)

  def test_episodename(self):
    """episodename should return known values for episode from filename."""
    for fileids, episodename in self.goodfilenames:
      result = tvshow.episodename(fileids[0], fileids[1], fileids[2])
      self.assertEqual(episodename, result)


class BadInput(unittest.TestCase):

  badids = (('Pokemon', '01', '99'),
             ('Red Dwarf', '40', '01',),
             ('Blackadder', '1', '12'))

  badnames = (('Rad Dwarf'),
              ('Pokereman'),
              ('Blackudder'))

  noepisodeinseason = (('The Simpsons', '15', '36'),
                       ('Stargate SG-1', '20', '32'),
                       ('Star Trek - Voyager', '01', '400'))

  
  def test_no_ep_in_season(self):
    """episodename should return None when the episode doesn't exist."""
    for show, season, episode in self.badids:
      result = tvshow.episodename(show, season, episode)
      self.assertIsNone(result)
    
  def test_no_series_found(self):
    """searchseries should return None when no series found."""
    for filename in self.badnames:
      result = tvshow.searchseries(filename)
      self.assertIsNone(result)

  def test_empty_episode(self):
    """episodename should do nothing if empty."""
    for show, season, episode in self.noepisodeinseason:
      result = tvshow.episodename(show, season, episode)
      self.assertEqual(None, result)


class testauthtokens(unittest.TestCase):

  mock = mock.Mock()

  def test_invalid_token(self):
    """Tests the return value of 401 for missing token."""
    
    mock.tvshow.episodename.return_value = 401
    result = tvshow.episodename('Red Dwarf')
    self.assertRaises(ValueError, result)


if __name__ == '__main__':
  unittest.main()