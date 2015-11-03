#!/usr/bin/env python

import renamer
import unittest


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
		'''seriesid should return good values from search'''
		for seriesid, seriesname in self.goodseriesid:
			result = renamer.searchseries(seriesname)
			self.assertEqual(seriesid, result)

	def test_findnamefromfile(self):
		'''Should return Series name, Season and episode numbers.'''
		for filename, fileids in self.goodids:
			result = renamer.findnamefromfile(filename)
			self.assertEqual(fileids, result)


	def test_episodename(self):
		'''episodename should return known values for episode from filename'''
		for fileids, episodename in self.goodfilenames:
			result = renamer.episodename(fileids[0], fileids[1], fileids[2])
			self.assertEqual(episodename, result)



if __name__ == '__main__':
	unittest.main()

