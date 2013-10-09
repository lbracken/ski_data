""" ski_data (https://github.com/lbracken/ski_data)
    Copyright (c) 2013 Levi Bracken.  
    Licensed under the MIT license.
-------------------------------------------------------------------------------

    Tests the ski_data web service

"""

import os
import json
import unittest
from flask import *

import ski_data
from ski_area import *


class SkiDataTestCase(unittest.TestCase):


    def setUp(self):
        """Before each test, ..."""
        ski_data.app.config['TESTING'] = True
        self.app = ski_data.app.test_client()


    def tearDown(self):
        """After each test, ..."""
        None


    def test_get_ski_areas(self):

        # TODO: Assert format, both long and short...

        # Basic request with no arguments
        rv = self.app.get('/get_ski_areas')
        response = json.loads(rv.data)

        assert "full" == response["format"]
        assert "id"   == response["order"]
        assert True   == response["ascending"]
        assert 312    == response["results_count"]

        # Verify first result
        assert 1000              == response["results"][0]["id"]
        assert "Mohawk Mountain" == response["results"][0]["name"]

        # Verify last result
        assert 2349             == response["results"][311]["id"]
        assert "Mont Tremblant" == response["results"][311]["name"]


        # Request with provided ids, two of which are invalid
        rv = self.app.get('/get_ski_areas?id=2135,9999,1000,1163,-5')
        response = json.loads(rv.data)

        assert "full" == response["format"]
        assert "id"   == response["order"]
        assert True   == response["ascending"]
        assert 3      == response["results_count"]

        # Verify results (should be sorted by id)
        assert 1000                 == response["results"][0]["id"]
        assert "Mohawk Mountain"    == response["results"][0]["name"]
        assert 1163                 == response["results"][1]["id"]
        assert "Stowe"              == response["results"][1]["name"]
        assert 2135                 == response["results"][2]["id"]
        assert "Whistler Blackcomb" == response["results"][2]["name"]               


        # Request with provided ids, sorted by name, desc
        rv = self.app.get('/get_ski_areas?id=2135,1000,1163&order=name&ascending=false')
        response = json.loads(rv.data)

        assert "full" == response["format"]
        assert "name" == response["order"]
        assert False  == response["ascending"]
        assert 3      == response["results_count"]

        # Verify results (should be sorted by name descending)
        assert 2135                 == response["results"][0]["id"]
        assert "Whistler Blackcomb" == response["results"][0]["name"]        
        assert 1163                 == response["results"][1]["id"]
        assert "Stowe"              == response["results"][1]["name"]  
        assert 1000                 == response["results"][2]["id"]
        assert "Mohawk Mountain"    == response["results"][2]["name"]


        # Request with provided name, sorted by vertical, in short format
        rv = self.app.get('/get_ski_areas?name=hood&order=vertical&ascending=true&format=short')
        response = json.loads(rv.data)

        assert "short"    == response["format"]
        assert "vertical" == response["order"]
        assert True       == response["ascending"]
        assert 3          == response["results_count"]

        # Verify results
        assert 2005                  == response["results"][0]["id"]
        assert "Hoodoo"              == response["results"][0]["name"]        
        assert 2002                  == response["results"][1]["id"]
        assert "Mount Hood Ski Bowl" == response["results"][1]["name"]  
        assert 2001                  == response["results"][2]["id"]
        assert "Mount Hood Meadows"  == response["results"][2]["name"] 
        
        # Verify that a request with id uses that over name
        rv = self.app.get('/get_ski_areas?name=ski&id=1000')
        response = json.loads(rv.data)

        assert "full" == response["format"]
        assert "id"   == response["order"]
        assert True   == response["ascending"]
        assert 1      == response["results_count"]

        # Verify results
        assert 1000              == response["results"][0]["id"]
        assert "Mohawk Mountain" == response["results"][0]["name"]


        # Verify that a requst for US only data, include only US ski areas
        rv = self.app.get('/get_ski_areas?usa_only=true')
        response = json.loads(rv.data)

        assert "full" == response["format"]
        assert "id"   == response["order"]
        assert True   == response["ascending"]
        assert 302    == response["results_count"]

        # Verify results
        for ski_area in response["results"]:
            assert ski_area["country"] == "USA"


    # Test reading request parameters...

    def test_get_ids_from_req(self):

    	# No value for id
    	with ski_data.app.test_request_context('/'):
    		assert None == ski_data.get_ids_from_req(ski_data.request)

    	# Single, valid, value for id
    	with ski_data.app.test_request_context('/?id=1'):
    		assert [1] == ski_data.get_ids_from_req(ski_data.request)    		

    	# Single, invalid, value for id
    	with ski_data.app.test_request_context('/?id=a'):
    		assert None == ski_data.get_ids_from_req(ski_data.request) 

    	# Single, invalid, value for id
    	with ski_data.app.test_request_context('/?id=1.2'):
    		assert None == ski_data.get_ids_from_req(ski_data.request)   

    	# Multiple, valid, values for id
    	with ski_data.app.test_request_context('/?id=1,2,3,4,5'):
    		assert [1,2,3,4,5] == ski_data.get_ids_from_req(ski_data.request)

    	# Multiple, invalid, values for id
    	with ski_data.app.test_request_context('/?id=a,False,2.2'):
    		assert None == ski_data.get_ids_from_req(ski_data.request)

    	# Multiple, valid and invalid, values for id
    	with ski_data.app.test_request_context('/?id=1,a,,2,2.2,c,3,x'):
    		assert [1,2,3] == ski_data.get_ids_from_req(ski_data.request)    


    def test_get_name_from_req(self):

    	# No value for name
    	with ski_data.app.test_request_context('/'):
    		assert None == ski_data.get_name_from_req(ski_data.request)

    	# Valid value for name
    	with ski_data.app.test_request_context('/?name= FOO'):
    		assert "foo" == ski_data.get_name_from_req(ski_data.request)    		

    	# Valid value for name
    	with ski_data.app.test_request_context('/?name=1'):
    		assert "1" == ski_data.get_name_from_req(ski_data.request)  

    	# Valid value for name
    	with ski_data.app.test_request_context('/?name=Foo,Bar'):
    		assert "foo,bar" == ski_data.get_name_from_req(ski_data.request)


    def test_get_format_from_req(self):

    	# No value for format
    	with ski_data.app.test_request_context('/'):
    		assert "full" == ski_data.get_format_from_req(ski_data.request)

    	# Valid value for format
    	with ski_data.app.test_request_context('/?format=short'):
    		assert "short" == ski_data.get_format_from_req(ski_data.request)  

        # Valid value for format
        with ski_data.app.test_request_context('/?format=AUTOCOMPLETE'):
            assert "autocomplete" == ski_data.get_format_from_req(ski_data.request)  

        # Valid value for format
        with ski_data.app.test_request_context('/?format=full'):
            assert "full" == ski_data.get_format_from_req(ski_data.request)  

        # Valid value for format
        with ski_data.app.test_request_context('/?format=foo'):
            assert "full" == ski_data.get_format_from_req(ski_data.request)                           


    def test_get_order_from_req(self):

       	# No value for order
    	with ski_data.app.test_request_context('/'):
    		assert "id" == ski_data.get_order_from_req(ski_data.request)

       	# Valid value for order
    	with ski_data.app.test_request_context('/?order=id'):
    		assert "id" == ski_data.get_order_from_req(ski_data.request)

       	# Valid value for order
    	with ski_data.app.test_request_context('/?order=ELEVATION'):
    		assert "elevation" == ski_data.get_order_from_req(ski_data.request)      	

    	# Invalid value for order
    	with ski_data.app.test_request_context('/?order=foo'):
    		assert "id" == ski_data.get_order_from_req(ski_data.request)     

    	# Invalid value for order
    	with ski_data.app.test_request_context('/?order=1'):
    		assert "id" == ski_data.get_order_from_req(ski_data.request)


    def test_get_ascending_from_req(self):

       	# No value for ascending
    	with ski_data.app.test_request_context('/'):
    		assert True == ski_data.get_ascending_from_req(ski_data.request)

       	# Valid value for order
    	with ski_data.app.test_request_context('/?ascending=FALSE'):
    		assert False == ski_data.get_ascending_from_req(ski_data.request)

       	# Valid value for order
    	with ski_data.app.test_request_context('/?ascending=false'):
    		assert False == ski_data.get_ascending_from_req(ski_data.request)   

       	# Valid value for order
    	with ski_data.app.test_request_context('/?ascending=true'):
    		assert True == ski_data.get_ascending_from_req(ski_data.request)      		  	

       	# Inalid value for order
    	with ski_data.app.test_request_context('/?ascending=1'):
    		assert True == ski_data.get_ascending_from_req(ski_data.request)

    	# Invalid value for order
    	with ski_data.app.test_request_context('/?ascending=z'):
    		assert True == ski_data.get_ascending_from_req(ski_data.request)


    def test_get_usa_only_from_req(self):

        # No value for usa only
        with ski_data.app.test_request_context('/'):
            assert False == ski_data.get_usa_only_from_req(ski_data.request)

        # Valid value for usa only
        with ski_data.app.test_request_context('/?usa_only=FALSE'):
            assert False == ski_data.get_usa_only_from_req(ski_data.request)

        # Valid value for usa only
        with ski_data.app.test_request_context('/?usa_only=false'):
            assert False == ski_data.get_usa_only_from_req(ski_data.request)   

        # Valid value for usa only
        with ski_data.app.test_request_context('/?usa_only=tRue'):
            assert True == ski_data.get_usa_only_from_req(ski_data.request)                

        # Inalid value for usa only
        with ski_data.app.test_request_context('/?usa_only=1'):
            assert False == ski_data.get_usa_only_from_req(ski_data.request)

        # Invalid value for usa only
        with ski_data.app.test_request_context('/?usa_only=z'):
            assert False == ski_data.get_usa_only_from_req(ski_data.request)


    def test_is_int(self):
    	assert True == ski_data.is_int(0)
    	assert True == ski_data.is_int(1000)
    	assert True == ski_data.is_int("1")
    	assert False == ski_data.is_int("foo")
    	assert False == ski_data.is_int("")


if __name__ == '__main__':
    # Initialize the connection to the ski_area_datasource
    ski_data.init_db()

    unittest.main()
