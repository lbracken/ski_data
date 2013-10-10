""" ski_data (https://github.com/lbracken/ski_data)
    Copyright (c) 2013 Levi Bracken.  
    Licensed under the MIT license.
-------------------------------------------------------------------------------

    Provides Flask based web service for getting data about ski areas.  
    Calls into ski_area_datasource for all ski_area data.

"""

import json
from flask import *

from ski_area import *
from ski_area_datasource import *


app = Flask(__name__)
datasource = None


def init_db():
	global datasource
	datasource = SkiAreaDataSource()


@app.route('/', methods=['GET'])
def main_page():
	return render_template('main.html')


@app.route('/ski-area-size-visualization', methods=['GET'])
def size_page():
	return render_template('ski-area-size-visualization.html')


@app.route('/ski-area-map', methods=['GET'])
def map_page():
	return render_template('ski-area-map.html')		


@app.route('/get_ski_areas', methods=['GET', 'POST'])
def get_ski_areas():
	""" Returns a set of ski areas in JSON format based upon various request
		arguments.
	"""	
	try:
		# Read and validate request arguments
		ids       = get_ids_from_req(request)
		name      = get_name_from_req(request)
		format    = get_format_from_req(request)
		order     = get_order_from_req(request)
		ascending = get_ascending_from_req(request)
		usa_only  = get_usa_only_from_req(request)

	except:
		# If there was a problem reading the request arguments, then request
		# is bad.  Return status code '400 - Bad Request'
		abort(400)

	# Get the requested ski areas from the datasource.  If ids are provided,
	# use that, otherwise use a provided name.  Or just get them all...
	if ids:
		ski_areas = datasource.get_ski_areas_by_id(ids, order, ascending)
	elif name:
		ski_areas = datasource.get_ski_areas_by_name(name, order, ascending)
	else:
		ski_areas = datasource.get_all_ski_areas(order, ascending)

	# Quick hack to support showing map of ski areas in the US until the 
	# datasource can support a proper query by various facets, like country.
	if usa_only:
		ski_areas[:] = [ski_area for ski_area in ski_areas if not ski_area.country != "USA"]

	# Create response
	response_body = {		
		"results" : [],
		"results_count" : len(ski_areas),
		"format"        : format,
		"order"         : order,
		"ascending"     : ascending,
	}

	# Calculating min/max in the following way was about 20-25% slower than
	# a number of if blocks in a single loop. But it's neater and more 
	# pythonic...  (Based upon 10 runs with 10k and 100k loops)
	if ski_areas:
		response_body["vertical_max"]  = max(ski_area.vertical  for ski_area in ski_areas)
		response_body["vertical_min"]  = min(ski_area.vertical  for ski_area in ski_areas)
		response_body["area_max"]      = max(ski_area.area      for ski_area in ski_areas)
		response_body["area_min"]      = min(ski_area.area      for ski_area in ski_areas)
		response_body["elevation_max"] = max(ski_area.elevation for ski_area in ski_areas)
		response_body["elevation_min"] = min(ski_area.elevation for ski_area in ski_areas)
		response_body["snowfall_max"]  = max(ski_area.snowfall  for ski_area in ski_areas)
		response_body["snowfall_min"]  = 0, # No all ski areas have snowfall data, so use zero as min
		response_body["trails_max"]    = max(ski_area.trails    for ski_area in ski_areas)
		response_body["trails_min"]    = min(ski_area.trails    for ski_area in ski_areas)

	# Add the ski areas to the response
	for ski_area in ski_areas:
		response_body["results"].append(ski_area.format(format))

	# Create and return the response object
	resp = make_response(jsonify(response_body))
	return resp


def get_ids_from_req(request):
	""" Returns the sanitized list of ids provided in the request.
	"""
	ids = [] 
	for id in request.args.get('id', '').strip("[]").split(','):
		id = id.strip()
		if is_int(id):
			ids.append(int(id))

	return ids if ids else None


def get_name_from_req(request):
	""" Returns a name provided in the request.
	"""
	name = request.args.get('name', None)
	return str(name.strip().lower()) if name else None


def get_format_from_req(request):
	""" Returns the format provided in the request.  Default is 'full'.
	"""
	format = request.args.get('format', '')
	format = format.strip().lower()
	return format if format in ski_area_formats else 'full'


def get_order_from_req(request):
	""" Returns the order provided in the request.  Default is 'id'.
	"""
	order = request.args.get('order', '')
	order = order.strip().lower()
	return order if order in ski_area_orders else 'id'


def get_ascending_from_req(request):
	""" Returns True if sort order should be ascending. Default true.
	"""	
	acs = request.args.get('ascending', "true")
	return False if ("false" == acs.strip().lower()) else True


def get_usa_only_from_req(request):
	""" Returns True if only ski areas from the USA should be returned.
	    Default false.
	"""	
	usa = request.args.get('usa_only', "false")
	return True if ("true" == usa.strip().lower()) else False	


def is_int(i):
	""" Return true if the given value can be cast as an int
	"""
	try:
		int(i)
		return True		
	except ValueError:
		return False


if __name__ == '__main__':
	init_db()
	app.run(debug=True)