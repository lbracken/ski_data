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


@app.route('/get_ski_areas', methods=['GET'])
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

		# TODO: Remove or only log as debug...
		print "--------------------< Request >--"
		print "  id         : %s" % ids
		print "  name       : %s" % name
		print "  format     : %s" % format
		print "  order      : %s" % order
		print "  acscending : %s" % ascending

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

	# Create response
	response_body = {		
		"results" : [],
		"results_count" : len(ski_areas),
		"format"        : format,
		"order"         : order,
		"ascending"     : ascending
	}

	for ski_area in ski_areas:
		response_body["results"].append(ski_area.format(format))

	# Create and return the response object
	resp = make_response(jsonify(response_body))
	return resp


def get_ids_from_req(request):
	""" Returns the sanitized list of ids provided in the request.
	"""
	ids = [] 
	for id in request.args.get('id', '').split(','):
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