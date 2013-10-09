""" ski_data (https://github.com/lbracken/ski_data)
    Copyright (c) 2013 Levi Bracken.  
    Licensed under the MIT license.
-------------------------------------------------------------------------------

    Defines the SkiArea class

"""

ski_area_formats = [
	"full",
	"short",
	"location",
	"autocomplete"]


ski_area_attributes = [
	"id",
	"name",
	"trails",
	"lifts",
	"vertical",
	"elevation",
	"base_elevation",
	"area",
	"snowfall",
	"city",
	"postal_code",
	"latitude",
	"longitude",
	"website",
	"wiki",
	"region",
	"country",
	"continent",
	"metric_values"]	


ski_area_orders = [
	"id",
	"name",
	"trails",
	"lifts",
	"vertical",
	"elevation",
	"base_elevation",
	"area",
	"snowfall",
	"city",
	"postal_code",
	"latitude",
	"longitude",
	"website",
	"wiki",
	"region",
	"country",
	"continent",
	"metric_values"]


class SkiArea(object):
	""" Represents a ski area 
	"""
	def __init__(self, id=0, name=''):
		self.id = id
		self.name = name


	def __str__(self):
		return "%d - %s" % (self.id, self.name)


	def format(self, format="full"):
		""" Returns the SkiArea in the given format.  Default is 'full'.
		"""

		formatted_result = {}

		if "short" == format:
			formatted_result["id"] = self.id
			formatted_result["name"] = self.name
			None	# Nothing else to do

		elif "autocomplete" == format:
			formatted_result["id"]    = self.id
			formatted_result["name"]  = self.name
			formatted_result["desc"]  = self.get_location_description()
			formatted_result["label"] = self.get_autocomplete_label()

		elif "location" == format:
			formatted_result["area"]      = self.area
			formatted_result["vertical"]  = self.vertical
			formatted_result["elevation"] = self.elevation
			formatted_result["snowfall"]  = self.snowfall		
			formatted_result["trails"]    = self.trails
			formatted_result["coordinates"] = self.get_coordinates()

		else:
			# Default, full format.
			for attribute in ski_area_attributes:
				formatted_result[attribute] = getattr(self, attribute)

		return formatted_result


	def get_location_description(self):
		return "%s, %s" % (self.region, self.country)


	def get_autocomplete_label(self):
		return "%s, %s, %s, %s" % (self.name, self.region, self.country, self.continent)


	def get_coordinates(self):
		return [self.longitude, self.latitude]