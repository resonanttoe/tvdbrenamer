import authentication
import renamer
import unittest


class KnownValues(unittest.TestCase):

	goodseriesid = ('Pokemon', '76703')

	def testseriesid(self):
		'''seriesid should return good values from search'''
		for filename, seriesid in self.goodseriesid:
			print filename
			result = renamer.searchseries(filename)
			self.assertEqual(seriesid, result)


if __name__ == '__main__':
	unittest.main()

#goodfilenames = (('Pokemon - S01E01 -.mp4', 'Pokemon! I Choose You!'),
#								 ('Red Dwarf - S08E03 -.mp4', 'Back in the Red (3)'),
#								 ('Black Books - S03E02 -.mp4', 'Elephants and Hens'))