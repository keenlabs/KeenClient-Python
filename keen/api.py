import requests
from keen import exceptions

__author__ = 'dkador'

class KeenApi(object):
    base_url = "https://api.keen.io"
    api_version = "2.0"

    def __init__(self, project_id, auth_token, base_url=None,
                 api_version=None):
        super(KeenApi, self).__init__()
        self.project_id = project_id
        self.auth_token = auth_token
        if base_url:
            self.base_url = base_url
        if api_version:
            self.api_version = api_version

    def post_event(self, event):
        url = "{}/{}/projects/{}/{}".format(self.base_url, self.api_version,
                                            self.project_id,
                                            event.collection_name)
        headers = {"Authorization": self.auth_token,
                   "Content-Type": "application/json"}
        payload = event.to_json()
        response = requests.post(url, data=payload, headers=headers)
        if response.status_code != 201:
            error = response.json
            raise exceptions.KeenApiError(error)