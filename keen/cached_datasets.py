import json

from keen.api import HTTPMethods
from keen.utilities import KeenKeys, headers, requires_key


class CachedDatasetsInterface:

    def __init__(self, api):
        self.api = api
        self._cached_datasets_url = "{0}/{1}/projects/{2}/datasets".format(
            self.api.base_url, self.api.api_version, self.api.project_id
        )

    @requires_key(KeenKeys.READ)
    def all(self):
        """ Fetch all Cached Datasets for a Project. Read key must be set.
        """
        return self._get_json(HTTPMethods.GET,
                              self._cached_datasets_url,
                              self._get_master_key())

    def _get_json(self, http_method, url, key, *args, **kwargs):
        response = self.api.fulfill(
            http_method,
            url,
            headers=headers(key),
            *args,
            **kwargs)

        self.api._error_handling(response)

        try:
            response = response.json()
        except ValueError:
            response = "No JSON available."

        return response

    def _get_read_key(self):
        return self.api._get_read_key()

    def _get_master_key(self):
        return self.api._get_master_key()
