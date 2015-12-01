#!/usr/bin/env python

import unittest

import renamer

tvshow = renamer.TvShow()

class KnownValues(unittest.TestCase):

  goodseriesid = ((76703, 'Pokemon'),
                  (76924, 'Black Books'),
                  (76736, 'Blackadder'))

  goodids = (('Pokemon - S01E01 -.mp4', ('Pokemon', '01', '01')),
             ('Red Dwarf - S08E03 -.mp4', ('Red Dwarf', '08', '03')),
             ('Black Books - S03E02 -.mp4', ('Black Books', '03', '02')))

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

  def empty_episode(self):
    """episodename should do nothing if empty."""
    result = tvshow.episodename(fileids[0])
    self.assertEqual(None, result)


class BadInput(unittest.TestCase):

  def no_ep_in_season(self):
    """episodename should return valueerror when the episode doesn't exist."""
    with self.assertRaises(tvshow.EpNotFoundError):
      tvshow.episodename('Red Dwarf', 01, 10)

  def no_series_found(self):
    """searchseries should return valueerror when no series found."""
    with self.assertRaises(tvshow.SeriesNotFoundError):
      tvshow.searchseries('Rad Dwarf')

if __name__ == '__main__':
  unittest.main()