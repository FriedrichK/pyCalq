# -*- coding: utf-8 -*-
from datetime import datetime
import json
import unittest

from mock import Mock, patch
from hamcrest import *

from pycalq import CALQ_API_ENDPOINT_TRACKING
from pycalq.tools import create_timestamp_string
from pycalq.validation import ActionParameterValidator, ParameterValidationException
from pycalq.tracking import track_action

TEST_DATETIME = datetime(2014, 8, 19, 13, 16, 30, 1)
TEST_DATETIME_STRING = '2014-08-19 13:16:30.000001'
TEST_ACTOR_NAME = 'test_actor'
IP_ADDRESS_MOCK = '127.1.2.7'
TEST_ACTION = 'Does Amazing Thing'
WRITE_KEY_MOCK = 'allworkandnoplaymakesjackadullboy'

TEST_PROPERTY_INVALID_GENDER = 'I prefer not to say'
TEST_PROPERTY_VALID_CURRENCY = 'usd'
TEST_PROPERTY_INVALID_CURRENCY = 'usdx'
TEST_PROPERTY_INVALID_AGE = 'twenty-nine'
TEST_PROPERTY_VALID_SALE_VALUE = 1


class ToolsTestCase(unittest.TestCase):

    def test_returns_timestamp_string_in_expected_format(self):
        actual = create_timestamp_string(TEST_DATETIME)

        self.assertEquals(actual, TEST_DATETIME_STRING)


class TrackingTestCase(unittest.TestCase):

    @patch('pycalq.tracking.PoolManager')
    def test_sends_tracking_request_as_expected_without_pool_manager(self, PoolManagerMock):
        pool_manager_mock = Mock()
        pool_manager_mock.urlopen = Mock()
        PoolManagerMock.return_value = pool_manager_mock

        properties = {'$country': 'NL', 'custom_property': True}
        track_action(TEST_ACTOR_NAME, TEST_ACTION, WRITE_KEY_MOCK, properties, IP_ADDRESS_MOCK, TEST_DATETIME)

        args, kwargs = pool_manager_mock.urlopen.call_args
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
    def test_logs_that_properties_are_invalid(self, PoolManagerMock):
        logger_mock = Mock()
        logger_mock.debug = Mock()

        properties = {'$gender': TEST_PROPERTY_INVALID_GENDER}
        track_action(TEST_ACTOR_NAME, TEST_ACTION, WRITE_KEY_MOCK, properties, IP_ADDRESS_MOCK, TEST_DATETIME, log=logger_mock)

        self.assertTrue(logger_mock.debug.called)


class ValidationTestCase(unittest.TestCase):

    def test_recognizes_data_as_valid(self):
        data = {
            '$sale_value': 1,
            '$sale_currency': 'eur',
            '$device_agent': 'android',
            '$device_os': 'android',
            '$device_resolution': '1024x768',
            '$device_mobile': True,
            '$country': 'DE',
            '$region': 'BE',
            '$city': 'Berlin',
            '$gender': 'male',
            '$age': 29,
            '$utm_campaign': 'campaign_name',
            '$utm_source': 'utm_source',
            '$utm_medium': 'radio',
            '$utm_content': 'nytimes',
            '$utm_term': 'some,keywords,convert,well'
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
