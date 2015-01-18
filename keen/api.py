# stdlib
import json
import ssl

# requests
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager

# keen exceptions
from keen import exceptions


__author__ = 'dkador'


class HTTPMethods(object):

    """ HTTP methods that can be used with Keen's API. """

    GET = 'get'
    POST = 'post'


class KeenAdapter(HTTPAdapter):

    """ Adapt :py:mod:`requests` to Keen IO. """

    def init_poolmanager(self, connections, maxsize, block=False):

        """ Initialize pool manager with forced TLSv1 support. """

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

    # self says it belongs to KeenApi/andOr is the object passed into KeenApi
    # __init__ create keenapi object whenever KeenApi class is invoked
    def __init__(self, project_id, write_key=None, read_key=None,
                 base_url=None, api_version=None, get_timeout=None, post_timeout=None,
                 master_key=None):
        """
        Initializes a KeenApi object

        :param project_id: the Keen project ID
        :param write_key: a Keen IO Scoped Key for Writes
        :param read_key: a Keen IO Scoped Key for Reads
        :param base_url: optional, set this to override where API requests
        are sent
        :param api_version: string, optional, set this to override what API
        :param master_key: a Keen IO Master API Key
        version is used
        """
        # super? recreates the object with values passed into KeenApi
        super(KeenApi, self).__init__()
        self.project_id = project_id
        self.write_key = write_key
        self.read_key = read_key
        self.master_key = master_key
        if base_url:
            self.base_url = base_url
        if api_version:
            self.api_version = api_version
        self.get_timeout = get_timeout
        self.post_timeout = post_timeout
        self.session = self._create_session()

    def _create_session(self):

        """ Build a session that uses KeenAdapter for SSL """

        s = requests.Session()
        s.mount('https://', KeenAdapter())
        return s

    def fulfill(self, method, *args, **kwargs):

        """ Fulfill an HTTP request to Keen's API. """

        return getattr(self.session, method)(*args, **kwargs)

    def post_event(self, event):
        """
        Posts a single event to the Keen IO API. The write key must be set first.

        :param event: an Event to upload
        """
        if not self.write_key:
            raise exceptions.InvalidEnvironmentError(
                "The Keen IO API requires a write key to send events. "
                "Please set a 'write_key' when initializing the "
                "KeenApi object."
            )

        url = "{0}/{1}/projects/{2}/events/{3}".format(self.base_url, self.api_version,
                                                       self.project_id,
                                                       event.event_collection)
        headers = {"Content-Type": "application/json", "Authorization": self.write_key}
        payload = event.to_json()
        response = self.fulfill(HTTPMethods.POST, url, data=payload, headers=headers, timeout=self.post_timeout)
        if response.status_code != 201:
            error = response.json()
            raise exceptions.KeenApiError(error)

    def post_events(self, events):

        """
        Posts a single event to the Keen IO API. The write key must be set first.

        :param events: an Event to upload
        """
        if not self.write_key:
            raise exceptions.InvalidEnvironmentError(
                "The Keen IO API requires a write key to send events. "
                "Please set a 'write_key' when initializing the "
                "KeenApi object."
            )

        url = "{0}/{1}/projects/{2}/events".format(self.base_url, self.api_version,
                                                   self.project_id)
        headers = {"Content-Type": "application/json", "Authorization": self.write_key}
        payload = json.dumps(events)
        response = self.fulfill(HTTPMethods.POST, url, data=payload, headers=headers, timeout=self.post_timeout)
        if response.status_code != 200:
            error = response.json()
            raise exceptions.KeenApiError(error)

    def query(self, analysis_type, params):
        """
        Performs a query using the Keen IO analysis API.  A read key must be set first.

        """
        if not self.read_key:
            raise exceptions.InvalidEnvironmentError(
                "The Keen IO API requires a read key to perform queries. "
                "Please set a 'read_key' when initializing the "
                "KeenApi object."
            )

        url = "{0}/{1}/projects/{2}/queries/{3}".format(self.base_url, self.api_version,
                                                        self.project_id, analysis_type)

        headers = {"Authorization": self.read_key}
        payload = params
        response = self.fulfill(HTTPMethods.GET, url, params=payload, headers=headers, timeout=self.get_timeout)
        if response.status_code != 200:
            error = response.json()
            raise exceptions.KeenApiError(error)

        return response.json()["result"]
