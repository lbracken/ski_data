""" ski_data (https://github.com/lbracken/ski_data)
    Copyright (c) 2013 Levi Bracken.  
    Licensed under the MIT license.
-------------------------------------------------------------------------------

    Serves as a source for ski area data.  Currently (temporarily?) implemented
    as an in-memory data source given the small data set size and the desire to
    stand something up quickly.

"""

import os
import sys
from operator import attrgetter

from ski_area import *

class SkiAreaDataSource(object):
	""" Represents a ski area datasource 
	"""
	def __init__(self, filename="./data/skiAreaData.tsv"):
		self.ski_areas = read_ski_data_file(filename)


	def __str__(self):
		return "SkiAreaDataSource -- Size: %d" % len(self.ski_areas)


	def get_ski_areas_by_id(self, ids, order, ascending):
		""" Returns the set of ski areas with the given set of ids
		"""
		result_set = []
		for id in ids:
			if id in self.ski_areas:
				result_set.append(self.ski_areas[id])

		return sort_ski_areas(result_set, order, ascending)


	def get_ski_areas_by_name(self, name, order, ascending):
		""" Returns the set of ski areas whose name contains the provided name.
			Ex: 'My Ski Area' would be returned if the provided name was 'My'.		
			Matches are case insensitive.  Current implementation requires a scan
			of the full set of ski areas.
		"""
		result_set = []
		for ski_area in self.ski_areas.values():
			if name.lower() in ski_area.name.lower():
				result_set.append(ski_area)

		return sort_ski_areas(result_set, order, ascending)


	def get_all_ski_areas(self, order, ascending):
		""" Returns the full set of ski areas in the data source
		"""
		return sort_ski_areas(self.ski_areas.values(), order, ascending)	


def sort_ski_areas(ski_areas, order, ascending):
	""" Returns a sorted list of the provided ski_areas, sorted as requested.
	"""
	return sorted(ski_areas, key=attrgetter(order), reverse = not ascending)


def read_ski_data_file(filename):
	""" Returned a dictionary of ski_areas (indexed by id) as read from the
		given filename.
	"""
	ski_areas = {}

	try:
		fin = open(filename)
		for line in fin:

			line = line.strip()

			# Ignore empty and comment lines...			
			if (not line or line[0] == '#'):
				continue

			# Parse each line, validating it's the correct size...
			parsed_line = line.split('\t')
			if(len(parsed_line) != 19):
				print 'Error parsing line: %s' % line
				continue

			# Populate a SkiArea object with the parsed line...
			ski_area = SkiArea(
				get_as_int(parsed_line[0]),
				get_as_str(parsed_line[1]))

			ski_area.trails         = get_as_int(parsed_line[2])
			ski_area.lifts          = get_as_int(parsed_line[3])
			ski_area.vertical       = get_as_int(parsed_line[4])
			ski_area.elevation      = get_as_int(parsed_line[5])
			ski_area.base_elevation = get_as_int(parsed_line[6])
			ski_area.area           = get_as_float(parsed_line[7])
			ski_area.snowfall       = get_as_int(parsed_line[8])
			ski_area.city           = get_as_str(parsed_line[9])
			ski_area.postal_code    = get_as_str(parsed_line[10])
			ski_area.latitude       = get_as_float(parsed_line[11])
			ski_area.longitude      = get_as_float(parsed_line[12])
			ski_area.website        = get_as_str(parsed_line[13])
			ski_area.wiki           = get_as_str(parsed_line[14])
			ski_area.region         = get_as_str(parsed_line[15])
			ski_area.country        = get_as_str(parsed_line[16])
			ski_area.continent      = get_as_str(parsed_line[17])
			ski_area.metric_values  = get_as_bool(parsed_line[18])

			ski_areas[ski_area.id] = ski_area

		fin.close()

	except:
		print 'Unable to read the file %s' % filename

	print "[SkiAreaDataSource] %d ski areas loaded from file '%s'" % (len(ski_areas), filename)
	return ski_areas


# -----------------------------------------------------------------------------
# Functions to help cast values.  Not robust in type checking, just quick
# casting with support for empty values.


def get_as_int(s):
	s = s.strip()
	return int(s) if s else 0


def get_as_str(s):
	return s.strip()


def get_as_float(s):
	s = s.strip()
	return float(s) if s else 0.0


def get_as_bool(s):
	s = s.strip()
	return True if ('true' == s.lower()) else False