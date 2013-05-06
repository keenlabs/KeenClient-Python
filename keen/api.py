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

    def __init__(self, project_token, base_url=None,
                 api_version=None):
        """ Initializes a KeenApi object

        :param project_token: the Keen project token
        :param base_url: optional, set this to override where API requests
        are sent
        :param api_version: string, optional, set this to override what API
        version is used
        """
        self.project_token = project_token
        if base_url:
            self.base_url = base_url
        if api_version:
            self.api_version = api_version

    def post_event(self, event):
        """ Posts a single event to the Keen API.

        :param event: an Event to upload
        """
        url = "{}/{}/projects/{}/events/{}".format(self.base_url, self.api_version,
                                            self.project_token,
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