# -*- coding: utf-8 -*-
"""
Created on Mon Sep  5 21:13:34 2016

@author: Marty
"""

from __future__ import absolute_import, print_function, division, unicode_literals
import unittest
from unittest import mock
import pandas as pd

from hydrofunctions import station, typing
from .fixtures import (
        fakeResponse
        )


class TestingNWIS(station.NWIS):
    """
    This subclass of NWIS is for testing the NWIS methods.
    """
    def __init__(self, dataframe):
        self._dataframe = dataframe


class TestStation(unittest.TestCase):

    def test_station_is_obj(self):
        actual = station.Station()
        self.assertIsInstance(actual, station.Station)

    def test_station_site_defaults_to_None(self):
        actual = station.Station()
        self.assertIsNone(actual.site)

    def test_station_id_sets(self):
        expected = "01234567"
        actual = station.Station(expected)
        another = station.Station("23456789")
        self.assertEqual(actual.site, expected)
        self.assertEqual(another.site, "23456789")

    def test_station_dict_returns_dict(self):
        actual = station.Station('first')
        self.assertIsInstance(actual.station_dict, dict)

    def test_multiple_instances_only_one_list(self):
        first = station.Station('first')
        second = station.Station('second')
        self.assertEqual(first.station_dict, second.station_dict)

    def test_station_dict_keeps_keys(self):
        first = station.Station('first')
        second = station.Station('second')
        actual = first.station_dict
        self.assertIn('first', actual)
        self.assertIn('second', actual)
        self.assertEqual(len(actual), 2, "The dict length is not equal to the \
                                            number of instances")

    def test_station_dict_returns_instance(self):
        first = station.Station('first')
        second = station.Station('second')
        expected = first
        # Look at the station_dict; does it contain a ref to 'first'?
        actual = second.station_dict['first']
        self.assertEqual(actual, expected)

    def test_station_subclasses_maintain_same_station_dict(self):
        class Foo(station.Station):
            pass

        foo_inst = Foo('foo')
        station_inst = station.Station('station')
        self.assertIn('station', foo_inst.station_dict)
        self.assertIn('foo', station_inst.station_dict)
        actual = station_inst.station_dict['foo']
        self.assertIsInstance(actual, Foo)


class TestNWIS(unittest.TestCase):

    @mock.patch("hydrofunctions.hydrofunctions.get_nwis")
    @mock.patch("hydrofunctions.hydrofunctions.get_nwis_property")
    def test_NWIS_init_check_defaults(self, mock_get_nwis_property, mock_get_nwis):
        default_site = None
        default_service = 'dv'
        default_start = None
        default_end = None
        default_parameterCd = 'all'
        default_period = None
        default_stateCd = None
        default_countyCd = None
        default_bBox = None

        mock_get_nwis_property.return_value = 'expected'
        mock_get_nwis.return_value = fakeResponse()

        station.NWIS()

        mock_get_nwis.assert_called_once_with(default_site,
                                              default_service,
                                              default_start,
                                              default_end,
                                              parameterCd=default_parameterCd,
                                              period=default_period,
                                              stateCd=default_stateCd,
                                              countyCd=default_countyCd,
                                              bBox=default_bBox)
        self.assertTrue(mock_get_nwis_property)

    @mock.patch("hydrofunctions.hydrofunctions.get_nwis")
    @mock.patch("hydrofunctions.hydrofunctions.get_nwis_property")
    def test_NWIS_init_calls_get_nwis_and_get_prop(self, mock_get_nwis_property, mock_get_nwis):
        site = 'expected site'
        service = 'expected service'
        start = 'expected start'
        end = 'expected end'
        parameterCd = 'expected pCode'
        mock_get_nwis_property.return_value = 'expected'
        mock_get_nwis.return_value = fakeResponse()

        station.NWIS(site, service, start, end, parameterCd=parameterCd)
        mock_get_nwis.assert_called_once_with(site, service, start, end,
                                              parameterCd=parameterCd,
                                              period=None, stateCd=None,
                                              countyCd=None, bBox=None)
        self.assertTrue(mock_get_nwis_property)

    @mock.patch("hydrofunctions.hydrofunctions.get_nwis")
    @mock.patch("hydrofunctions.hydrofunctions.get_nwis_property")
    @mock.patch("hydrofunctions.hydrofunctions.extract_nwis_df")
    def test_NWIS_init_sets_url_ok_json(self, mock_extract_nwis_df, mock_get_nwis_property, mock_get_nwis):
        expected_url = 'expected url'
        expected_ok = True
        expected_json = 'expected json'

        mock_get_nwis.return_value = fakeResponse(code=200,
                                                  url=expected_url,
                                                  json=expected_json)

        actual = station.NWIS()
        self.assertEqual(actual.url, expected_url, "NWIS.__init__() did not set self.url properly.")
        self.assertEqual(actual.ok, expected_ok, "NWIS.__init__() did not set self.ok properly.")
        self.assertEqual(actual.json, expected_json, "NWIS.__init__() did not set self.json properly.")

    @mock.patch("hydrofunctions.hydrofunctions.get_nwis")
    @mock.patch("hydrofunctions.hydrofunctions.get_nwis_property")
    @mock.patch("hydrofunctions.hydrofunctions.extract_nwis_df")
    def test_NWIS_init_calls_extract_nwis_df(self, mock_extract_nwis_df, mock_get_nwis_property, mock_get_nwis):
        expected_json = 'expected json'
        mock_get_nwis.return_value = fakeResponse(json=expected_json)
        actual = station.NWIS()
        mock_extract_nwis_df.assert_called_once_with(expected_json)

    def test_NWIS_df_returns_all_columns(self):
        expected_cols = ['USGS:01541200:00060:00000_qualifiers',
                         'USGS:01541200:00060:00000',
                         'USGS:01541200:00065:00000_qualifiers',
                         'USGS:01541200:00065:00000',
                         'USGS:01541303:00060:00000_qualifiers',
                         'USGS:01541303:00060:00000',
                         'USGS:01541303:00065:00000_qualifiers',
                         'USGS:01541303:00065:00000']
        data = [['test', 5, 'test', 5, 'test', 5, 'test', 5],
                ['test', 5, 'test', 5, 'test', 5, 'test', 5]]
        test_df = pd.DataFrame(data=data, columns=expected_cols)
        test_nwis = TestingNWIS(test_df)
        actual_df = test_nwis.df()
        actual_cols = actual_df.columns.tolist()
        self.assertListEqual(actual_cols, expected_cols, "NWIS.df() should return all of the columns.")

    def test_NWIS_df_all_returns_all_columns(self):
        cols = ['USGS:01541200:00060:00000_qualifiers',
                         'USGS:01541200:00060:00000',
                         'USGS:01541200:00065:00000_qualifiers',
                         'USGS:01541200:00065:00000',
                         'USGS:01541303:00060:00000_qualifiers',
                         'USGS:01541303:00060:00000',
                         'USGS:01541303:00065:00000_qualifiers',
                         'USGS:01541303:00065:00000']
        expected_cols = cols
        data = [['test', 5, 'test', 5, 'test', 5, 'test', 5],
                ['test', 5, 'test', 5, 'test', 5, 'test', 5]]
        test_df = pd.DataFrame(data=data, columns=cols)
        test_nwis = TestingNWIS(test_df)
        actual_df = test_nwis.df('all')
        actual_cols = actual_df.columns.tolist()
        self.assertListEqual(actual_cols, expected_cols, "NWIS.df() should return all of the columns.")

    def test_NWIS_df_discharge_returns_discharge_data_columns(self):
        cols = ['USGS:01541200:00060:00000_qualifiers',
                         'USGS:01541200:00060:00000',
                         'USGS:01541200:00065:00000_qualifiers',
                         'USGS:01541200:00065:00000',
                         'USGS:01541303:00060:00000_qualifiers',
                         'USGS:01541303:00060:00000',
                         'USGS:01541303:00065:00000_qualifiers',
                         'USGS:01541303:00065:00000']

        expected_cols = ['USGS:01541200:00060:00000',
                         'USGS:01541303:00060:00000']

        data = [['test', 5, 'test', 5, 'test', 5, 'test', 5],
                ['test', 5, 'test', 5, 'test', 5, 'test', 5]]
        test_df = pd.DataFrame(data=data, columns=cols)
        test_nwis = TestingNWIS(test_df)
        actual_df = test_nwis.df('discharge')
        actual_cols = actual_df.columns.tolist()
        self.assertListEqual(actual_cols, expected_cols, "NWIS.df() should return all of the columns.")

    def test_NWIS_df_q_returns_discharge_data_columns(self):
        cols = ['USGS:01541200:00060:00000_qualifiers',
                         'USGS:01541200:00060:00000',
                         'USGS:01541200:00065:00000_qualifiers',
                         'USGS:01541200:00065:00000',
                         'USGS:01541303:00060:00000_qualifiers',
                         'USGS:01541303:00060:00000',
                         'USGS:01541303:00065:00000_qualifiers',
                         'USGS:01541303:00065:00000']

        expected_cols = ['USGS:01541200:00060:00000',
                         'USGS:01541303:00060:00000']

        data = [['test', 5, 'test', 5, 'test', 5, 'test', 5],
                ['test', 5, 'test', 5, 'test', 5, 'test', 5]]
        test_df = pd.DataFrame(data=data, columns=cols)
        test_nwis = TestingNWIS(test_df)
        actual_df = test_nwis.df('q')
        actual_cols = actual_df.columns.tolist()
        self.assertListEqual(actual_cols, expected_cols, "NWIS.df() should return all of the columns.")

    def test_NWIS_df_stage_returns_stage_data_columns(self):
        cols = ['USGS:01541200:00060:00000_qualifiers',
                         'USGS:01541200:00060:00000',
                         'USGS:01541200:00065:00000_qualifiers',
                         'USGS:01541200:00065:00000',
                         'USGS:01541303:00060:00000_qualifiers',
                         'USGS:01541303:00060:00000',
                         'USGS:01541303:00065:00000_qualifiers',
                         'USGS:01541303:00065:00000']

        expected_cols = ['USGS:01541200:00065:00000',
                         'USGS:01541303:00065:00000']

        data = [['test', 5, 'test', 5, 'test', 5, 'test', 5],
                ['test', 5, 'test', 5, 'test', 5, 'test', 5]]
        test_df = pd.DataFrame(data=data, columns=cols)
        test_nwis = TestingNWIS(test_df)
        actual_df = test_nwis.df('stage')
        actual_cols = actual_df.columns.tolist()
        self.assertListEqual(actual_cols, expected_cols, "NWIS.df() should return all of the columns.")

    def test_NWIS_df_flags_returns_qualifiers_columns(self):
        cols = ['USGS:01541200:00060:00000_qualifiers',
                         'USGS:01541200:00060:00000',
                         'USGS:01541200:00065:00000_qualifiers',
                         'USGS:01541200:00065:00000',
                         'USGS:01541303:00060:00000_qualifiers',
                         'USGS:01541303:00060:00000',
                         'USGS:01541303:00065:00000_qualifiers',
                         'USGS:01541303:00065:00000']

        expected_cols = ['USGS:01541200:00060:00000_qualifiers',
                         'USGS:01541200:00065:00000_qualifiers',
                         'USGS:01541303:00060:00000_qualifiers',
                         'USGS:01541303:00065:00000_qualifiers']

        data = [['test', 5, 'test', 5, 'test', 5, 'test', 5],
                ['test', 5, 'test', 5, 'test', 5, 'test', 5]]
        test_df = pd.DataFrame(data=data, columns=cols)
        test_nwis = TestingNWIS(test_df)
        actual_df = test_nwis.df('flags')
        actual_cols = actual_df.columns.tolist()
        self.assertListEqual(actual_cols, expected_cols, "NWIS.df() should return all of the columns.")

    def test_NWIS_df_flags_q_returns_discharge_qualifiers_columns(self):
        cols = ['USGS:01541200:00060:00000_qualifiers',
                'USGS:01541200:00060:00000',
                'USGS:01541200:00065:00000_qualifiers',
                'USGS:01541200:00065:00000',
                'USGS:01541303:00060:00000_qualifiers',
                'USGS:01541303:00060:00000',
                'USGS:01541303:00065:00000_qualifiers',
                'USGS:01541303:00065:00000']

        expected_cols = ['USGS:01541200:00060:00000_qualifiers',
                         'USGS:01541303:00060:00000_qualifiers']

        data = [['test', 5, 'test', 5, 'test', 5, 'test', 5],
                ['test', 5, 'test', 5, 'test', 5, 'test', 5]]
        test_df = pd.DataFrame(data=data, columns=cols)
        test_nwis = TestingNWIS(test_df)
        actual_df = test_nwis.df('flags', 'q')
        actual_cols = actual_df.columns.tolist()
        self.assertListEqual(actual_cols, expected_cols, "NWIS.df() should return all of the columns.")

    def test_NWIS_df_stage_flags_returns_stage_qualifiers_columns(self):
        cols = ['USGS:01541200:00060:00000_qualifiers',
                'USGS:01541200:00060:00000',
                'USGS:01541200:00065:00000_qualifiers',
                'USGS:01541200:00065:00000',
                'USGS:01541303:00060:00000_qualifiers',
                'USGS:01541303:00060:00000',
                'USGS:01541303:00065:00000_qualifiers',
                'USGS:01541303:00065:00000']

        expected_cols = ['USGS:01541200:00065:00000_qualifiers',
                         'USGS:01541303:00065:00000_qualifiers']

        data = [['test', 5, 'test', 5, 'test', 5, 'test', 5],
                ['test', 5, 'test', 5, 'test', 5, 'test', 5]]
        test_df = pd.DataFrame(data=data, columns=cols)
        test_nwis = TestingNWIS(test_df)
        actual_df = test_nwis.df('stage', 'flags')
        actual_cols = actual_df.columns.tolist()
        self.assertListEqual(actual_cols, expected_cols, "NWIS.df() should return all of the columns.")

"""
    @mock.patch("hydrofunctions.typing.check_parameter_string")
    def test_NWIS_init_calls_check_parameter_string(self, mock_cps):

    def test_NWIS_start_defaults_to_None(self):
        actual = station.NWIS('01541200')
        self.assertIsNone(actual.start_date)

    def test_NWIS_end_defaults_to_None(self):
        actual = station.NWIS('01541200')
        self.assertIsNone(actual.end_date)

    def test_NWIS_setters_work(self):
        site = "01582500"
        service = "dv"
        start = "2011-01-01"
        end = "2011-01-02"
        actual = station.NWIS(site, service, start, end)
        self.assertIsInstance(actual, station.NWIS)
        self.assertEqual(actual.site, site)
        self.assertEqual(actual.service, service)
        self.assertEqual(actual.start_date, start)
        self.assertEqual(actual.end_date, end)
        # self.assertIs(type(actual.fetch), function)

    def test_NWIS_setters_parameterCd(self):
        site = "01582500"
        service = "dv"
        start = "2011-01-01"
        end = "2011-01-02"
        parameterCd = "00065"
        actual = station.NWIS(site, service, start, end,
                              parameterCd=parameterCd)
        self.assertIsInstance(actual, station.NWIS)
        self.assertEqual(actual.site, site)
        self.assertEqual(actual.service, service)
        self.assertEqual(actual.start_date, start)
        self.assertEqual(actual.parameterCd, parameterCd)

    @mock.patch("hydrofunctions.hydrofunctions.get_nwis")
    @mock.patch("hydrofunctions.hydrofunctions.get_nwis_property")
    def test_NWIS_get_data_calls_get_nwis_correctly(self, mock_get_prop, mock_get_nwis):
        site = "01582500"
        service = "dv"
        start = "2011-01-01"
        end = "2011-01-02"
        parameterCd = "00060"

        actual = station.NWIS(site, service, start, end, parameterCd=parameterCd)
        try_it_out = actual.get_data()
        # try_it_out should be a response object, I think
        mock_get_nwis.assert_called_once_with(site, service, start, end,
                                              parameterCd=parameterCd,
                                              period=None, stateCd=None,
                                              countyCd=None, bBox=None)

    @mock.patch("hydrofunctions.hydrofunctions.get_nwis")
    @mock.patch("hydrofunctions.hydrofunctions.get_nwis_property")
    def test_NWIS_get_data_calls_get_nwis_mult_sites(self, mock_get_prop, mock_get_nwis):
        site = ["01638500", "01646502"]
        siteEx = "01638500,01646502"
        service = "dv"
        start = "2011-01-01"
        end = "2011-01-02"
        parameterCd = None
        actual = station.NWIS(site, service, start, end)
        try_it_out = actual.get_data()
        # try_it_out should be an instance of NWIS.
        mock_get_nwis.assert_called_once_with(siteEx, service, start, end,
                                              parameterCd='all',
                                              period=None, stateCd=None,
                                              countyCd=None, bBox=None)

    @mock.patch('requests.get')
    @mock.patch("hydrofunctions.hydrofunctions.get_nwis_property")
    def test_NWIS_get_data_accepts_countyCd_array(self, mock_get_prop, mock_get):
        start = "2017-01-01"
        end = "2017-12-31"
        cnty = ['51059', '51061']
        cnty = typing.check_parameter_string(cnty, 'county')
        service2 = 'dv'

        expected_url = 'https://waterservices.usgs.gov/nwis/dv/?'
        expected_headers = {'max-age': '120', 'Accept-encoding': 'gzip'}
        expected_params = {'format': 'json,1.1', 'sites': None,
                           'stateCd': None, 'countyCd': cnty, 'bBox': None,
                           'parameterCd': None, 'period': None,
                           'startDT': start, 'endDT': end}

        expected = fakeResponse(200)

        mock_get.return_value = expected
        actual = station.NWIS(None, service2, start, countyCd=cnty,
                              end_date=end).get_data()
        mock_get.assert_called_once_with(expected_url, params=expected_params,
                                         headers=expected_headers)

    @mock.patch('requests.get')
    @mock.patch("hydrofunctions.hydrofunctions.get_nwis_property")
    def test_NWIS_get_data_accepts_parameterCd_array(self, mock_get_prop, mock_get):
        site = '01541200'
        start = "2017-01-01"
        end = "2017-12-31"
        service = 'iv'
        parameterCd = ['00060','00065']
        expected_parameterCd = '00060,00065'

        expected_url = 'https://waterservices.usgs.gov/nwis/iv/?'
        expected_headers = {'max-age': '120', 'Accept-encoding': 'gzip'}
        expected_params = {'format': 'json,1.1', 'sites': site,
                           'stateCd': None, 'countyCd': None, 'bBox': None,
                           'parameterCd': expected_parameterCd, 'period': None,
                           'startDT': start, 'endDT': end}

        expected = fakeResponse(200)

        mock_get.return_value = expected
        actual = station.NWIS(site, service, start, end_date=end,
                              parameterCd=parameterCd).get_data()
        mock_get.assert_called_once_with(expected_url, params=expected_params,
                                         headers=expected_headers)

    @mock.patch('requests.get')
    @mock.patch("hydrofunctions.hydrofunctions.get_nwis_property")
    def test_NWIS_get_data_converts_parameterCd_all_to_None(self, mock_get_prop, mock_get):
        site = '01541200'
        service = 'iv'
        parameterCd = 'all'
        expected_parameterCd = None
        expected_url = 'https://waterservices.usgs.gov/nwis/' + service + '/?'
        expected_headers = {'max-age': '120', 'Accept-encoding': 'gzip'}
        expected_params = {'format': 'json,1.1', 'sites': site,
                           'stateCd': None, 'countyCd': None, 'bBox': None,
                           'parameterCd': expected_parameterCd, 'period': None,
                           'startDT': None, 'endDT': None}
        expected = fakeResponse(200)
        mock_get.return_value = expected
        actual = station.NWIS(site, service, parameterCd = parameterCd).get_data()
        mock_get.assert_called_once_with(expected_url, params=expected_params,
                                         headers=expected_headers)

    # Now test .df() and .json()
    @unittest.skip("Test this differently")
    def test_NWIS_df_returns_df(self):
        site = "01582500"
        service = "dv"
        start = "2011-01-01"
        end = "2011-01-02"
        actual = station.NWIS(site, service, start, end)
        # You don't need to test the following like this.
        # Just test that actual.df() returns nothing if you call before get_data()
        # And actual.df() returns a df if you call after .get_data()
        actualdf = actual.get_data().df()  # returns a dataframe
        self.assertIs(type(actualdf), pd.core.frame.DataFrame,
                      msg="Did not return a df")

    def test_NWIS_raises_ValueError_too_many_location_arguments(self):
        with self.assertRaises(ValueError):
            station.NWIS('01541000', stateCd='MD')

    def test_NWIS_raises_ValueError_start_and_period_arguments(self):
        with self.assertRaises(ValueError):
            station.NWIS('01541000', start_date='2013-02-02', period='P9D')
    """





if __name__ == '__main__':
    unittest.main(verbosity=2)
