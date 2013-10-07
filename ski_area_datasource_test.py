""" ski_data (https://github.com/lbracken/ski_data)
    Copyright (c) 2013 Levi Bracken.  
    Licensed under the MIT license.
-------------------------------------------------------------------------------

    Tests the ski_area_datasource service

"""

import os
import unittest
from ski_area_datasource import *


datasource = SkiAreaDataSource()

class SkiAreaDataSourceTestCase(unittest.TestCase):
    

    def setUp(self):
        """Before each test, ..."""
        None

    def tearDown(self):
        """After each test, ..."""
        None


    def test_get_ski_areas_by_id(self):

        # Test with all invalid idatasource
        ski_areas = datasource.get_ski_areas_by_id([0, 9999], "id", True)
        assert 0 == len(ski_areas)

        # Test with three valid and two invalid idatasource
        ski_areas = datasource.get_ski_areas_by_id([0, 1000, 1025, 1200, 9999], "id", True)
        assert 3 == len(ski_areas)

        assert "Mohawk Mountain" == ski_areas[0].name
        assert "Baker Mountain" == ski_areas[1].name
        assert "Wisp" == ski_areas[2].name


    def test_get_ski_areas_by_name(self):

        # Test with an invalid name
        ski_areas = datasource.get_ski_areas_by_name("zzz", "name", False)
        assert 0 == len(ski_areas)

        # Test with a valid name that will return three matches
        ski_areas = datasource.get_ski_areas_by_name("hood", "name", False)
        assert 3 == len(ski_areas) 

        assert "Mount Hood Ski Bowl" == ski_areas[0].name
        assert "Mount Hood Meadows" == ski_areas[1].name
        assert "Hoodoo" == ski_areas[2].name


    def test_get_all_ski_areas(self):

        ski_areas = datasource.get_all_ski_areas("id", True)
        assert 312 == len(ski_areas) 
        assert 1000 == ski_areas[0].id
        assert 2349 == ski_areas[311].id


    def test_get_as_int(self):
        assert 1   == get_as_int("1")
        assert 100 == get_as_int(" 100 ")


    def test_get_as_str(self):
        assert "1"   == get_as_str("1")
        assert "foo" == get_as_str(" foo ")


    def test_get_as_float(self):
        assert 1.0 == get_as_float("1")
        assert 2.2 == get_as_float("2.2")               


    def test_get_as_bool(self):
        assert True  == get_as_bool("true")
        assert True  == get_as_bool(" TruE ")
        assert False == get_as_bool("false")
        assert False == get_as_bool("foo")
        assert False == get_as_bool("")


if __name__ == '__main__':
    unittest.main()