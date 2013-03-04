import requests
from keen import exceptions

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

    def __init__(self, project_token, api_key, base_url=None,
                 api_version=None):
        """ Initializes a KeenApi object

        :param project_token: the Keen project token
        :param api_key: the Keen api key
        :param base_url: optional, set this to override where API requests
        are sent
        :param api_version: string, optional, set this to override what API
        version is used
        """
        super(KeenApi, self).__init__()
        self.project_token = project_token
        if base_url:
            self.base_url = base_url
        if api_key:
            self.api_key = api_key
        if api_version:
            self.api_version = api_version

    def post_event(self, event):
        """ Posts a single event to the Keen API.

        :param event: an Event to upload
        """
        url = "{}/{}/projects/{}/events/{}?api_key={}".format(self.base_url, self.api_version,
                                            self.project_token,
                                            event.collection_name,
                                            self.api_key)
        headers = {"Content-Type": "application/json"}
        payload = event.to_json()
        response = requests.post(url, data=payload, headers=headers)
        if response.status_code != 201:
            error = response.json
            raise exceptions.KeenApiError(error)
