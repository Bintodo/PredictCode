import pytest
import unittest.mock as mock
from tests.helpers import MockOpen
import os.path
import numpy as np

import open_cp.sources.chicago as chicago

def test_load_default_filename():
    with mock.patch("builtins.open", MockOpen(None)) as open_mock:
        assert( chicago.default_burglary_data() == None )
        filename = open_mock.calls[0][0][0]
        assert( os.path.split(filename)[1] == "chicago.csv" )

string_data = "\n".join([
    ",".join([chicago._DESCRIPTION_FIELD, chicago._X_FIELD, chicago._Y_FIELD,
        "other", chicago._TIME_FIELD]),
    "THEFT, 789, 1012, ahgd, 01/01/2017 10:30:23 PM",
    "ASSAULT, 12, 34, dgs, sgjhg",
    "THEFT, 123, 456, as, 03/13/2016 02:53:30 AM"
    ])

def test_load_data():
    with mock.patch("builtins.open", MockOpen(string_data)) as open_mock:
        points = chicago.load("filename", {"THEFT"})
        assert( open_mock.calls[0][0] == ("filename",) )

        assert( len(points.timestamps) == 2 )
        assert( points.timestamps[0] == np.datetime64("2016-03-13T02:53:30") )
        assert( points.timestamps[1] == np.datetime64("2017-01-01T22:30:23") )
        np.testing.assert_allclose( points.coords[:,0], np.array([123, 456]) / 3.28084 )
        np.testing.assert_allclose( points.coords[:,1], np.array([789, 1012]) / 3.28084 )

def test_load_data_keep_in_feet():
    with mock.patch("builtins.open", MockOpen(string_data)) as open_mock:
        points = chicago.load("filename", {"THEFT"}, to_meters=False)
        np.testing.assert_allclose( points.coords[:,0], [123, 456] )
        np.testing.assert_allclose( points.coords[:,1], [789, 1012] )
