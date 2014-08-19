# -*- coding: utf-8 -*-

import json
import logging
LOG = logging.getLogger('pycalq-tracking')
LOG.addHandler(logging.NullHandler())

from urllib3 import PoolManager

from pycalq import CALQ_API_ENDPOINT_TRACKING
from tools import create_timestamp_string
from validation import ParameterValidationException, ActionParameterValidator


def track_action(actor, action_name, write_key, properties={}, ip_address=None, timestamp=None, pool_manager=None, log=LOG):
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
    except ParameterValidationException, e:
        log.debug(e.message)

    return send_request(CALQ_API_ENDPOINT_TRACKING, data, pool_manager=pool_manager)


def send_request(endpoint, data, pool_manager=None):
    if pool_manager is None:
        pool_manager = PoolManager()
    return pool_manager.urlopen('POST', endpoint, headers={'Content-Type': 'application/json'}, body=json.dumps(data))
