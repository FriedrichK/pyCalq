from pycalq import __calq_api_version__

ERROR_TEMPLATE_SPECIAL_PROPERTIES = 'property %s is not a valid special property recognized by Calq as of API version %s. It will likely be ignored'
ERROR_TEMPLATE_REQUIRES = 'parameter %s cannot be used without including parameter %s as well'
ERROR_TEMPLATE_MAX_LENGTH = 'value for parameter %s exceeds the maximum length of %s'
ERROR_TEMPLATE_OPTIONS = 'value >>%s<< for parameter %s is not among the valid options: %s'
ERROR_TEMPLATE_INTEGER = 'value for parameter %s has to be an Integer'

VALID_SPECIAL_PROPERTIES = {
    'action': [
        'sale_value', 'sale_currency', 'device_agent', 'device_os', 'device_resolution',
        'device_mobile', 'country', 'region', 'city', 'gender', 'age', 'utm_campaign',
        'utm_source', 'utm_medium', 'utm_content', 'utm_term'
    ],
    'profile': [
        'actor', 'full_name', 'image_url', 'country', 'region', 'city', 'gender', 'age',
        'email', 'phone', 'sms'
    ]
}


class ParameterValidationException(Exception):
    pass


class EntryParameter:
    def __init__(self, requires=False, max_length=None, options=None, integer=False):
        self._requires = requires
        self._max_length = max_length
        self._options = options
        self._integer = integer

    def set_name(self, name):
        self._name = name

    def check_validity(self, data):
        processors = [self._check_requires, self._check_max_length, self._check_options, self._check_integer]
        for processor in processors:
            success, message = processor(data)
            if not success:
                return success, message
        return True, None

    def _check_requires(self, data):
        if not self._name in data or not self._requires:
            return True, None
        result = self._requires in data
        message = None if result else ERROR_TEMPLATE_REQUIRES % (self._name, self._requires)
        return result, message

    def _check_max_length(self, data):
        if not self._name in data or self._max_length is None:
            return True, None
        result = len(data[self._name]) <= self._max_length
        message = None if result else ERROR_TEMPLATE_MAX_LENGTH % (self._name, self._max_length)
        return result, message

    def _check_options(self, data):
        if not self._name in data or self._options is None:
            return True, None
        result = data[self._name] in self._options
        message = None if result else ERROR_TEMPLATE_OPTIONS % (data[self._name], self._name, ', '.join([unicode(item) for item in self._options]))
        return result, message

    def _check_integer(self, data):
        if not self._name in data or not self._integer:
            return True, None
        result = isinstance(data[self._name], int)
        message = None if result else ERROR_TEMPLATE_INTEGER % (self._name)
        return result, message


class _ParameterValidatorMetaClass(type):

    def __new__(meta, name, bases, dct):
        validators = []
        for key, value in dct.items():
            if isinstance(value, EntryParameter):
                value.set_name('$' + key)
                validators.append(value)
                del dct[key]
        dct['_validators'] = validators
        return super(_ParameterValidatorMetaClass, meta).__new__(meta, name, bases, dct)


class ParameterValidator:
    __metaclass__ = _ParameterValidatorMetaClass

    def validate(self, data):
        success, message = self._validate_special_properties(data)
        if not success:
            raise ParameterValidationException(message)

        for validator in self._validators:
            success, message = validator.check_validity(data)
            if not success:
                raise ParameterValidationException(message)
        return True, None

    def _validate_special_properties(self, data):
        for property_ in data:
            if not property_[0] == '$':
                continue
            if not property_[1:] in VALID_SPECIAL_PROPERTIES[self.name]:
                return False, ERROR_TEMPLATE_SPECIAL_PROPERTIES % (property_, __calq_api_version__)
        return True, None


class ActionParameterValidator(ParameterValidator):
    name = 'action'

    sale_value = EntryParameter()
    sale_currency = EntryParameter(max_length=3, requires='$sale_value')
    device_agent = EntryParameter()
    device_os = EntryParameter()
    device_resolution = EntryParameter()
    device_mobile = EntryParameter()
    country = EntryParameter()
    region = EntryParameter()
    city = EntryParameter()
    gender = EntryParameter(options=['male', 'female'])
    age = EntryParameter(integer=True)
    utm_campaign = EntryParameter()
    utm_source = EntryParameter()
    utm_medium = EntryParameter()
    utm_content = EntryParameter()
    utm_term = EntryParameter()


class ProfileParameterValidator(ParameterValidator):
    name = 'profile'

    actor = EntryParameter()
    full_name = EntryParameter()
    image_url = EntryParameter()
    country = EntryParameter()
    region = EntryParameter()
    city = EntryParameter()
    gender = EntryParameter(options=['male', 'female'])
    age = EntryParameter(integer=True)
    email = EntryParameter()
    phone = EntryParameter()
    sms = EntryParameter()
