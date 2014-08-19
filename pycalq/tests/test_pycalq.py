# -*- coding: utf-8 -*-
from datetime import datetime
import json
import unittest

from mock import Mock, patch
from hamcrest import *

from pycalq import CALQ_API_ENDPOINT_TRACKING, CALQ_API_ENDPOINT_PROFILE, CALQ_API_ENDPOINT_TRANSFER
from pycalq.tools import create_timestamp_string
from pycalq.validation import ActionParameterValidator, ParameterValidationException
from pycalq.tracking import track_action, submit_profile, transfer_user

TEST_DATETIME = datetime(2014, 8, 19, 13, 16, 30, 1)
TEST_DATETIME_STRING = '2014-08-19 13:16:30.000001'
TEST_ACTOR_NAME = 'test_actor'
TEST_ACTOR_NAME2 = "test_actor_2"
IP_ADDRESS_MOCK = '127.1.2.7'
TEST_ACTION = 'Does Amazing Thing'
WRITE_KEY_MOCK = 'allworkandnoplaymakesjackadullboy'

TEST_PROPERTY_VALID_GENDER = 'male'
TEST_PROPERTY_INVALID_GENDER = 'I prefer not to say'
TEST_PROPERTY_VALID_CURRENCY = 'usd'
TEST_PROPERTY_INVALID_CURRENCY = 'usdx'
TEST_PROPERTY_VALID_AGE = 29
TEST_PROPERTY_INVALID_AGE = 'twenty-nine'
TEST_PROPERTY_VALID_SALE_VALUE = 1
TEST_PROPERTY_VALID_SALE_CURRENCY = 'eur'
TEST_PROPERTY_VALID_DEVICE_AGENT = 'android'
TEST_PROPERTY_VALID_DEVICE_OS = 'android'
TEST_PROPERTY_VALID_DEVICE_RESOLUTION = '1024x768'
TEST_PROPERTY_VALID_DEVICE_MOBILE = True
TEST_PROPERTY_VALID_COUNTRY = 'DE'
TEST_PROPERTY_VALID_REGION = 'BE'
TEST_PROPERTY_VALID_CITY = 'Berlin'
TEST_PROPERTY_VALID_UTM_CAMPAIGN = 'campaign_name'
TEST_PROPERTY_VALID_UTM_SOURCE = 'utm_source'
TEST_PROPERTY_VALID_UTM_MEDIUM = 'radio'
TEST_PROPERTY_VALID_UTM_SOURCE = 'nytimes'
TEST_PROPERTY_VALID_UTM_CONTENT = 'content'
TEST_PROPERTY_VALID_UTM_TERM = 'some,keywords,convert,well'


class ToolsTestCase(unittest.TestCase):

    def test_returns_timestamp_string_in_expected_format(self):
        actual = create_timestamp_string(TEST_DATETIME)

        self.assertEquals(actual, TEST_DATETIME_STRING)


class TrackingTestCase(unittest.TestCase):

    @patch('pycalq.tracking.PoolManager')
    def test_sends_tracking_request_as_expected(self, PoolManagerMock):
        PoolManagerMock, url_open_mock = self._build_pool_manager_mock(PoolManagerMock)

        properties = {'$country': 'NL', 'custom_property': True}
        track_action(TEST_ACTOR_NAME, TEST_ACTION, WRITE_KEY_MOCK, properties, IP_ADDRESS_MOCK, TEST_DATETIME)

        args, kwargs = url_open_mock.call_args
        self.assertEquals(args[0], 'POST')
        self.assertEquals(args[1], CALQ_API_ENDPOINT_TRACKING)
        self.assertEquals(kwargs['headers'], {'Content-Type': 'application/json'})
        expected = {
            'timestamp': TEST_DATETIME_STRING,
            'actor': TEST_ACTOR_NAME,
            'action_name': TEST_ACTION,
            'write_key': WRITE_KEY_MOCK,
            'ip_address': IP_ADDRESS_MOCK,
            'properties': properties
        }
        self.assertEquals(json.loads(kwargs['body']), expected)

    @patch('pycalq.tracking.PoolManager')
    def test_logs_that_action_request_properties_are_invalid(self, PoolManagerMock):
        logger_mock = Mock()
        logger_mock.debug = Mock()

        properties = {'$gender': TEST_PROPERTY_INVALID_GENDER}
        track_action(TEST_ACTOR_NAME, TEST_ACTION, WRITE_KEY_MOCK, properties, IP_ADDRESS_MOCK, TEST_DATETIME, log=logger_mock)

        self.assertTrue(logger_mock.debug.called)

    @patch('pycalq.tracking.PoolManager')
    def test_sends_profile_request_as_expected(self, PoolManagerMock):
        PoolManagerMock, url_open_mock = self._build_pool_manager_mock(PoolManagerMock)

        properties = {'$age': TEST_PROPERTY_VALID_AGE, 'custom_property': True}
        submit_profile(TEST_ACTOR_NAME, WRITE_KEY_MOCK, properties)

        args, kwargs = url_open_mock.call_args
        self.assertEquals(args[0], 'POST')
        self.assertEquals(args[1], CALQ_API_ENDPOINT_PROFILE)
        self.assertEquals(kwargs['headers'], {'Content-Type': 'application/json'})
        expected = {
            'actor': TEST_ACTOR_NAME,
            'write_key': WRITE_KEY_MOCK,
            'properties': properties
        }
        self.assertEquals(json.loads(kwargs['body']), expected)

    @patch('pycalq.tracking.PoolManager')
    def test_logs_that_profile_request_properties_are_invalid(self, PoolManagerMock):
        logger_mock = Mock()
        logger_mock.debug = Mock()

        properties = {'$age': TEST_PROPERTY_INVALID_AGE}
        submit_profile(TEST_ACTOR_NAME, WRITE_KEY_MOCK, properties, log=logger_mock)

        self.assertTrue(logger_mock.debug.called)

    @patch('pycalq.tracking.PoolManager')
    def test_sends_transfer_request_as_expected(self, PoolManagerMock):
        PoolManagerMock, url_open_mock = self._build_pool_manager_mock(PoolManagerMock)

        transfer_user(TEST_ACTOR_NAME, TEST_ACTOR_NAME2, WRITE_KEY_MOCK)

        args, kwargs = url_open_mock.call_args
        self.assertEquals(args[0], 'POST')
        self.assertEquals(args[1], CALQ_API_ENDPOINT_TRANSFER)
        self.assertEquals(kwargs['headers'], {'Content-Type': 'application/json'})
        expected = {
            'old_actor': TEST_ACTOR_NAME,
            'new_actor': TEST_ACTOR_NAME2,
            'write_key': WRITE_KEY_MOCK
        }
        self.assertEquals(json.loads(kwargs['body']), expected)

    def _build_pool_manager_mock(self, PoolManagerMock):
        pool_manager_mock = Mock()
        pool_manager_mock.urlopen = Mock()
        PoolManagerMock.return_value = pool_manager_mock
        return PoolManagerMock, pool_manager_mock.urlopen


class ValidationTestCase(unittest.TestCase):

    def test_recognizes_data_as_valid(self):
        data = {
            '$sale_value': TEST_PROPERTY_VALID_SALE_VALUE,
            '$sale_currency': TEST_PROPERTY_VALID_SALE_CURRENCY,
            '$device_agent': TEST_PROPERTY_VALID_DEVICE_AGENT,
            '$device_os': TEST_PROPERTY_VALID_DEVICE_OS,
            '$device_resolution': TEST_PROPERTY_VALID_DEVICE_RESOLUTION,
            '$device_mobile': TEST_PROPERTY_VALID_DEVICE_MOBILE,
            '$country': TEST_PROPERTY_VALID_COUNTRY,
            '$region': TEST_PROPERTY_VALID_REGION,
            '$city': TEST_PROPERTY_VALID_CITY,
            '$gender': TEST_PROPERTY_VALID_GENDER,
            '$age': TEST_PROPERTY_VALID_AGE,
            '$utm_campaign': TEST_PROPERTY_VALID_UTM_CAMPAIGN,
            '$utm_source': TEST_PROPERTY_VALID_UTM_SOURCE,
            '$utm_medium': TEST_PROPERTY_VALID_UTM_MEDIUM,
            '$utm_content': TEST_PROPERTY_VALID_UTM_CONTENT,
            '$utm_term': TEST_PROPERTY_VALID_UTM_TERM
        }
        actual = ActionParameterValidator().validate(data)
        self.assertEquals(actual, (True, None,))

    def test_flags_unrecognized_special_property(self):
        data = {'$unrecognizedproperty': 'is unrecognized'}
        self.assertRaises(ParameterValidationException, ActionParameterValidator().validate, data)

    def test_flags_missing_required_parameter(self):
        data = {'$sale_currency': TEST_PROPERTY_VALID_CURRENCY}
        self.assertRaises(ParameterValidationException, ActionParameterValidator().validate, data)

    def test_flags_max_length_violation(self):
        data = {'$sale_currency': TEST_PROPERTY_INVALID_CURRENCY, '$sale_value': TEST_PROPERTY_VALID_SALE_VALUE}
        self.assertRaises(ParameterValidationException, ActionParameterValidator().validate, data)

    def test_flags_option_violation(self):
        data = {'$gender': TEST_PROPERTY_INVALID_GENDER}
        self.assertRaises(ParameterValidationException, ActionParameterValidator().validate, data)

    def test_flags_integer_violation(self):
        data = {'$age': TEST_PROPERTY_INVALID_AGE}
        self.assertRaises(ParameterValidationException, ActionParameterValidator().validate, data)
