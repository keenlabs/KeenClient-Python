# stdlib
import json
import ssl

# requests
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager

# keen
from keen import exceptions, utilities
from keen.utilities import KeenKeys, requires_key

# json
from requests.compat import json


__author__ = 'dkador'


class HTTPMethods(object):

    """ HTTP methods that can be used with Keen's API. """

    GET = 'get'
    POST = 'post'
    DELETE = 'delete'
    PUT = 'put'


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
        version is used
        :param get_timeout: optional, the timeout on GET requests
        :param post_timeout: optional, the timeout on POST requests
        :param master_key: a Keen IO Master API Key, needed for deletes
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

    def fulfill(self, method, *args, **kwargs):

        """ Fulfill an HTTP request to Keen's API. """

        return getattr(self.session, method)(*args, **kwargs)

    @requires_key(KeenKeys.WRITE)
    def post_event(self, event):
        """
        Posts a single event to the Keen IO API. The write key must be set first.

        :param event: an Event to upload
        """

        url = "{0}/{1}/projects/{2}/events/{3}".format(self.base_url, self.api_version,
                                                       self.project_id,
                                                       event.event_collection)
        headers = utilities.headers(self.write_key)
        payload = event.to_json()
        response = self.fulfill(HTTPMethods.POST, url, data=payload, headers=headers, timeout=self.post_timeout)
        self._error_handling(response)

    @requires_key(KeenKeys.WRITE)
    def post_events(self, events):

        """
        Posts a single event to the Keen IO API. The write key must be set first.

        :param events: an Event to upload
        """

        url = "{0}/{1}/projects/{2}/events".format(self.base_url, self.api_version,
                                                   self.project_id)
        headers = utilities.headers(self.write_key)
        payload = json.dumps(events)
        response = self.fulfill(HTTPMethods.POST, url, data=payload, headers=headers, timeout=self.post_timeout)
        self._error_handling(response)
        return self._get_response_json(response)

    def _order_by_is_valid_or_none(self, params):
        """
        Validates that a given order_by has proper syntax.

        :return: Returns True if either no order_by is present, or if the order_by is well-formed.
        """
        if not "order_by" in params or not params["order_by"]:
            return True

        def _order_by_dict_is_not_well_formed(d):
            if not isinstance(d, dict):
                # Bad type.
                return True
            if "property_name" in d and d["property_name"]:
                if "direction" in d and not (d["direction"] == "ASC" or d["direction"] == "DESC"):
                    # Bad direction provided.
                    return True
                for k in d:
                    if k != "property_name" and k != "direction":
                        # Unexpected key.
                        return True
                # Everything looks good!
                return False
            # Missing required key.
            return True

        # order_by is converted to a list before this point if it wasn't one before.
        order_by_list = json.loads(params["order_by"])
        if filter(_order_by_dict_is_not_well_formed, order_by_list):
            # At least one order_by dict is broken.
            return False
        if not "group_by" in params or not params["group_by"]:
            # We must have group_by to have order_by make sense.
            return False
        return True

    @requires_key(KeenKeys.READ)
    def query(self, analysis_type, params, all_keys=False):
        """
        Performs a query using the Keen IO analysis API.  A read key must be set first.

        """
        if not self._order_by_is_valid_or_none(params):
            raise ValueError("order_by given is invalid or is missing required group_by.")

        url = "{0}/{1}/projects/{2}/queries/{3}".format(self.base_url, self.api_version,
                                                        self.project_id, analysis_type)

        headers = utilities.headers(self.read_key)
        payload = params
        response = self.fulfill(HTTPMethods.GET, url, params=payload, headers=headers, timeout=self.get_timeout)
        self._error_handling(response)

        response = response.json()

        if not all_keys:
            response = response["result"]

        return response

    @requires_key(KeenKeys.MASTER)
    def delete_events(self, event_collection, params):
        """
        Deletes events via the Keen IO API. A master key must be set first.

        :param event_collection: string, the event collection from which event are being deleted

        """

        url = "{0}/{1}/projects/{2}/events/{3}".format(self.base_url,
                                                       self.api_version,
                                                       self.project_id,
                                                       event_collection)
        headers = utilities.headers(self.master_key)
        response = self.fulfill(HTTPMethods.DELETE, url, params=params, headers=headers, timeout=self.post_timeout)

        self._error_handling(response)
        return True

    @requires_key(KeenKeys.READ)
    def get_collection(self, event_collection):
        """
        Extracts info about a collection using the Keen IO API. A master key must be set first.

        :param event_collection: the name of the collection to retrieve info for
        """

        url = "{0}/{1}/projects/{2}/events/{3}".format(self.base_url, self.api_version,
                                                       self.project_id, event_collection)
        headers = utilities.headers(self.read_key)
        response = self.fulfill(HTTPMethods.GET, url, headers=headers, timeout=self.get_timeout)
        self._error_handling(response)

        return response.json()

    @requires_key(KeenKeys.READ)
    def get_all_collections(self):
        """
        Extracts schema for all collections using the Keen IO API. A master key must be set first.

        """

        url = "{0}/{1}/projects/{2}/events".format(self.base_url, self.api_version, self.project_id)
        headers = utilities.headers(self.read_key)
        response = self.fulfill(HTTPMethods.GET, url, headers=headers, timeout=self.get_timeout)
        self._error_handling(response)

        return response.json()

    def _error_handling(self, res):
        """
        Helper function to do the error handling

        :params res: the response from a request
        """

        # making the error handling generic so if an status_code starting with 2 doesn't exist, we raise the error
        if res.status_code // 100 != 2:
            error = self._get_response_json(res)
            raise exceptions.KeenApiError(error)

    def _get_response_json(self, res):
        """
        Helper function to extract the JSON body out of a response OR throw an exception.

        :param res: the response from a request
        :return: the JSON body OR throws an exception
        """

        try:
            error = res.json()
        except ValueError:
            error = {
                "message": "The API did not respond with JSON, but: {0}".format(res.text[:1000]),
                "error_code": "{0}".format(res.status_code)
            }
        return error

    def _create_session(self):

        """ Build a session that uses KeenAdapter for SSL """

        s = requests.Session()
        s.mount('https://', KeenAdapter())
        return s

    def _get_read_key(self):
        return self.read_key

    def _get_write_key(self):
        return self.write_key

    def _get_master_key(self):
        return self.master_key