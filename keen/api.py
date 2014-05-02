# stdlib
import json, sys

try:
    import _ssl as ssl
except ImportError:
    import ssl

try:
    import __builtin__
except ImportError:
    pass  # Py3 doesn't have `__builtin__`

# requests
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager

# keen exceptions
from keen import exceptions


__author__ = 'dkador'


class HTTPMethods(object):

    ''' HTTP methods that can be used with Keen's API. '''

    GET = 'get'
    POST = 'post'


class KeenAdapter(HTTPAdapter):

    ''' Adapt :py:mod:`requests` to Keen IO. '''

    def init_poolmanager(self, connections, maxsize, block=False):

        ''' Initialize pool manager with forced TLSv1 support. '''

        self.poolmanager = PoolManager(num_pools=connections,
                                       maxsize=maxsize,
                                       block=block,
                                       ssl_version=ssl.PROTOCOL_TLSv1)


class KeenApi(object):
    """
    Responsible for communicating with the Keen API. Used by multiple
    persistence strategies or async processing.
    """

    # the default base URL of the Keen API
    base_url = "https://api.keen.io"
    # the default version of the Keen API
    api_version = "3.0"

    # default number of retries to be attempted
    default_retries = 0

    # `requests`: adapter and session
    __adapter__ = None
    __session__ = None

    # self says it belongs to KeenApi/andOr is the object passed into KeenApi
    # __init__ create keenapi object whenever KeenApi class is invoked
    def __init__(self, project_id,
                 write_key=None, read_key=None,
                 base_url=None, api_version=None, default_retries=0):
        """
        Initializes a KeenApi object

        :param project_id: the Keen project ID
        :param write_key: a Keen IO Scoped Key for Writes
        :param read_key: a Keen IO Scoped Key for Reads
        :param base_url: optional, set this to override where API requests
        are sent
        :param api_version: string, optional, set this to override what API
        version is used
        """
        # super? recreates the object with values passed into KeenApi
        super(KeenApi, self).__init__()

        # copy over keys and settings
        self.project_id = project_id
        self.write_key = write_key
        self.read_key = read_key
        self.default_retries = default_retries

        # copy in base URL and API version
        if base_url: self.base_url = base_url
        if api_version: self.api_version = api_version

    # py3-compatible range operation
    @staticmethod
    def range(*args, **kwargs):

        '''  '''

        if int(sys.version[0]) >= 3:
            return range(*args, **kwargs)
        return __builtin__.xrange(*args, **kwargs)

    @property
    def _apisession(self):

        ''' Lazy-load a session from :py:mod:`requests`. '''

        # lazy-init session
        if not self.__session__:
            self.__session__ = requests.Session()
            self.__session__.mount('https://', self._apiadapter)
        return self.__session__

    @property
    def _apiadapter(self):

        ''' Lazy-load an adapter from :py:mod:`requests`. '''

        # lazy-init adapter
        if not self.__adapter__: self.__adapter__ = KeenAdapter()
        return self.__adapter__

    def post_event(self, event, retries=None, strict=False):
        """
        Posts a single event to the Keen IO API. The write key must be set first.

        :param event: an Event to upload
        """
        if not self.write_key:
            raise exceptions.InvalidEnvironmentError(
                "The Keen IO API requires a write key to send events. "
                "Please set a 'write_key' when initializing the "
                "KeenApi object.")

        # send the request
        return self.fulfill(*(
                HTTPMethods.POST,  # HTTP method to use
                "{0}/{1}/projects/{2}/events/{3}".format(  # build URL to use
                    self.base_url,
                    self.api_version,
                    self.project_id,
                    event.event_collection
                )
            ), **{
                'data': event.to_json(),  # payload
                'headers': {  # auth headers
                    "Content-Type": "application/json",
                    "Authorization": self.write_key
                },
                'retries': retries or self.default_retries,  # retry count
                'expected': 201,  # expected return code
                '_strict': strict  # whether to raise exceptions immediately
            }
        )

    def post_events(self, events, retries=None, strict=False):

        """
        Posts a single event to the Keen IO API. The write key must be set first.

        :param events: an Event to upload
        """
        if not self.write_key:
            raise exceptions.InvalidEnvironmentError(
                "The Keen IO API requires a write key to send events. "
                "Please set a 'write_key' when initializing the "
                "KeenApi object.")

        # send the request
        return self.fulfill(*(
                HTTPMethods.POST,  # HTTP method to use
                "{0}/{1}/projects/{2}/events".format(  # build URL to use
                    self.base_url,
                    self.api_version,
                    self.project_id
                )
            ), **{
                'data': json.dumps(events),  # payload
                'headers': {  # auth headers
                    "Content-Type": "application/json",
                    "Authorization": self.write_key
                },
                'retries': retries or self.default_retries,  # retry count
                'expected': 200,  # expected return code
                '_strict': strict  # whether to raise exceptions immediately
            }
        )

    def query(self, analysis_type, params, retries=None, strict=False):
        """
        Performs a query using the Keen IO analysis API.  A read key must be set first.

        """
        if not self.read_key:
            raise exceptions.InvalidEnvironmentError(
                "The Keen IO API requires a read key to perform queries. "
                "Please set a 'read_key' when initializing the "
                "KeenApi object.")

        return self.fulfill(*(
                HTTPMethods.GET,  # HTTP method to use
                "{0}/{1}/projects/{2}/queries/{3}".format(  # build URL to use
                    self.base_url,
                    self.api_version,
                    self.project_id,
                    analysis_type
                )
            ), **{
                'params': params,  # payload
                'headers': {  # auth headers
                    "Authorization": self.read_key
                },
                'retries': retries or self.default_retries,  # retry count
                'expected': (200, 304),  # expected return code
                'return_key': 'result',  # result location in response
                'default_value': {},  # default value if no `return_key`
                '_strict': strict  # whether to raise exceptions immediately
            }
        )

    def fulfill(self, method, url, retries=None, expected=200, return_key=None, default_value={}, _retry_count=0, _strict=False, *args, **kwargs):

        ''' Fulfill an HTTP request to Keen's API. '''

        # allow multiple success codes
        if not isinstance(expected, tuple):
            expected = (expected,)

        for attempt in self.range(1, (retries or 1) + 1):

            # defaults
            result, response = None, None

            try:
                # fire off request using lazy-loaded session
                result = getattr(self._apisession, method)(url, *args, **kwargs)
                response = result.json()

            except Exception as e:
                if _strict or attempt >= (retries or self.default_retries):
                    raise exceptions.KeenApiError({'message': str(e), 'error_code': str(e.__class__.__name__)})  # oops, apierror!

            else:
                # check for unexpected responses
                if expected and result.status_code not in expected:
                    raise exceptions.KeenApiError(response)  # raise immediately, it worked and failed

                break  # things worked, stop trying

        if return_key: return response.get(return_key, default_value)  # potentially, return a specific key with an optional default
        return response  # otherwise return :)
