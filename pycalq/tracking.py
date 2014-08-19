# -*- coding: utf-8 -*-

import sys
import json
import logging
LOG = logging.getLogger('pycalq-tracking')
LOG.addHandler(logging.NullHandler())

from urllib3 import PoolManager

from pycalq import CALQ_API_ENDPOINT_TRACKING, CALQ_API_ENDPOINT_PROFILE, CALQ_API_ENDPOINT_TRANSFER
from tools import create_timestamp_string
from validation import ParameterValidationException, ActionParameterValidator, ProfileParameterValidator


def track_action(
        actor, action_name, write_key, properties={}, ip_address=None, timestamp=None, pool_manager=None,
        endpoint=CALQ_API_ENDPOINT_TRACKING, log=LOG):
    data = {
        'actor': actor,
        'action_name': action_name,
        'write_key': write_key,
        'properties': properties
    }
    if not ip_address is None:
        data['ip_address'] = ip_address

    timestamp = create_timestamp_string(timestamp) if not timestamp is None else None
    if not timestamp is None:
        data['timestamp'] = timestamp

    try:
        ActionParameterValidator().validate(properties)
    except ParameterValidationException:
        exc = sys.exc_info()[1]
        log.debug(exc.message)

    return send_request(endpoint, data, pool_manager=pool_manager)


def submit_profile(actor, write_key, properties={}, pool_manager=None, endpoint=CALQ_API_ENDPOINT_PROFILE, log=LOG):
    data = {
        'actor': actor,
        'write_key': write_key,
        'properties': properties
    }

    try:
        ProfileParameterValidator().validate(properties)
    except ParameterValidationException:
        exc = sys.exc_info()[1]
        log.debug(exc.message)

    return send_request(endpoint, data, pool_manager)


def transfer_user(old_actor, new_actor, write_key, pool_manager=None, endpoint=CALQ_API_ENDPOINT_TRANSFER, log=LOG):
    data = {
        'old_actor': old_actor,
        'new_actor': new_actor,
        'write_key': write_key
    }

    return send_request(endpoint, data, pool_manager)


def send_request(endpoint, data, pool_manager=None):
    if pool_manager is None:
        pool_manager = PoolManager()
    return pool_manager.urlopen('POST', endpoint, headers={'Content-Type': 'application/json'}, body=json.dumps(data))
