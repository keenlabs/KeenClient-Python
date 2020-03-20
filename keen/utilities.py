
from functools import wraps

# keen
from keen import exceptions


VERSION = "0.6.0"

def version():
    """
    Retrieves the current version of the SDK
    """
    return VERSION


def headers(api_key):
    """
    Helper function to easily get the correct headers for an endpoint

    :params api_key: The appropriate API key for the request being made
    """

    return {
        "Content-Type": "application/json",
        "Authorization": api_key,
        "Keen-Sdk": "python-{0}".format(version())
    }


class KeenKeys(object):
    """ Keen API key types. """

    READ = 'read'
    WRITE = 'write'
    MASTER = 'master'


class switch(object):
    """ Python switch recipe. """

    def __init__(self, value):
        self.value = value
        self.fall = False

    def __iter__(self):
        yield self.match
        raise StopIteration
    
    def match(self, *args):
        """Whether or not to enter a given case statement"""

        self.fall = self.fall or not args
        self.fall = self.fall or (self.value in args)

        return self.fall


def _throw_key_missing(key, relying_on_master):
    message = ("The Keen IO API requires a {0} key to perform queries. "
              "Please set a '{0}_key' when initializing the "
              "KeenApi object.")

    if relying_on_master:
        message += ' The "master_key" is set, but one should prefer the key with least privilege.'

    raise exceptions.InvalidEnvironmentError(message.format(key))


def requires_key(key_type):
    def requires_key_decorator(func):

        @wraps(func)
        def method_wrapper(self, *args, **kwargs):
            for case in switch(key_type):
                if case(KeenKeys.READ):
                    if not self._get_read_key():
                        _throw_key_missing(KeenKeys.READ, bool(self._get_master_key()))
                    break

                if case(KeenKeys.WRITE):
                    if not self._get_write_key():
                        _throw_key_missing(KeenKeys.WRITE, bool(self._get_master_key()))
                    break

                if case(KeenKeys.MASTER):
                    if not self._get_master_key():
                        _throw_key_missing(KeenKeys.MASTER, False)
                    break

            return func(self, *args, **kwargs)

        return method_wrapper
    return requires_key_decorator
