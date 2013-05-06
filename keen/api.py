from google.appengine.api import urlfetch
from keen import exceptions
try:
    import ujson as json
except:
    from django.utils import simplejson as json
__author__ = 'dkador'


class KeenApi(object):
    """
    Responsible for communicating with the Keen API. Used by multiple
    persistence strategies or async processing.
    """

    # the default base URL of the Keen API
    base_url = "https://api.keen.io"
    # the default version of the Keen API
    api_version = "3.0"

    def __init__(self, project_id,
                 write_key=None, read_key=None,
                 base_url=None, api_version=None):
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
        super(KeenApi, self).__init__()
        self.project_id = project_id
        self.write_key = write_key
        self.read_key = read_key
        if base_url:
            self.base_url = base_url
        if api_version:
            self.api_version = api_version

    def post_event(self, event):
        """
        Posts a single event to the Keen IO API. The write key must be set first.

        :param event: an Event to upload
        """
        if not self.write_key:
            raise Exception("The Keen IO API requires a write key to send events. "
                            "Please set a 'write_key' when initializing the "
                            "KeenApi object.")

        url = "{0}/{1}/projects/{2}/events/{3}".format(self.base_url, self.api_version,
                                                       self.project_id,
                                                       event.collection_name)
        headers = {"Content-Type": "application/json"}
        payload = event.to_json()
        fetch = urlfetch.fetch(url=url,
                                payload=payload,
                                method=urlfetch.POST,
                                headers=headers)
        response = json.loads(fetch.content)
        if fetch.status_code != 201:
            raise exceptions.KeenApiError(response)