
import json

from keen.api import KeenApi, HTTPMethods
from keen import exceptions, utilities
from keen.utilities import KeenKeys, requires_key


class SavedQueriesInterface:

    def __init__(self, api):
        self.api = api
        self.saved_query_url = "{0}/{1}/projects/{2}/queries/saved".format(
            self.api.base_url, self.api.api_version, self.api.project_id
        )

    @requires_key(KeenKeys.MASTER)
    def all(self):
        """
        Gets all saved queries for a project from the Keen IO API.
        Master key must be set.
        """

        response = self._get_json(HTTPMethods.GET, self.saved_query_url, self._get_master_key())

        return response

    @requires_key(KeenKeys.MASTER)
    def get(self, query_name):
        """
        Gets a single saved query for a project from the Keen IO API given a
        query name.
        Master key must be set.
        """

        url = "{0}/{1}".format(self.saved_query_url, query_name)
        response = self._get_json(HTTPMethods.GET, url, self._get_master_key())

        return response

    @requires_key(KeenKeys.READ)
    def results(self, query_name):
        """
        Gets a single saved query with a 'result' object for a project from the
        Keen IO API given a query name.
        Read or Master key must be set.
        """

        url = "{0}/{1}/result".format(self.saved_query_url, query_name)
        response = self._get_json(HTTPMethods.GET, url, self._get_read_key())

        return response

    @requires_key(KeenKeys.MASTER)
    def create(self, query_name, saved_query):
        """
        Creates the saved query via a PUT request to Keen IO Saved Query endpoint.
        Master key must be set.
        """
        url = "{0}/{1}".format(self.saved_query_url, query_name)
        payload = saved_query

        # To support clients that may have already called dumps() to work around how this used to
        # work, make sure it's not a str. Hopefully it's some sort of mapping. When we actually
        # try to send the request, client code will get an InvalidJSONError if payload isn't
        # a json-formatted string.
        if not isinstance(payload, str):
            payload = json.dumps(saved_query)

        response = self._get_json(HTTPMethods.PUT, url, self._get_master_key(), data=payload)
        keen_api._error_handling(response)

        return response

    @requires_key(KeenKeys.MASTER)
    def update(self, query_name, saved_query):
        """
        Updates the saved query via a PUT request to Keen IO Saved Query
        endpoint.
        Master key must be set.
        """

        return self.create(query_name, saved_query)

    @requires_key(KeenKeys.MASTER)
    def delete(self, query_name):
        """
        Deletes a saved query from a project with a query name.
        Master key must be set.
        """

        url = "{0}/{1}".format(self.saved_query_url, query_name)
        response = self._get_json(HTTPMethods.DELETE, url, self._get_master_key())

        return True

    def _get_json(self, http_method, url, key, *args, **kwargs):
        response = self.api.fulfill(http_method, url, headers=utilities.headers(key), *args, **kwargs)
        self.api._error_handling(response)

        try:
            response = response.json()
        except ValueError:
            response = "No JSON available."

        return response

    def _get_read_key(self):
        return self.api.read_key

    def _get_master_key(self):
        return self.api.master_key
