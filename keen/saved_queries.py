
import json
import six

try:
    from collections.abc import Mapping # Python >=3.3
except ImportError:
    from collections import Mapping

from keen.api import HTTPMethods
from keen import utilities
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

        return response

    @requires_key(KeenKeys.MASTER)
    def update_full(self, query_name, saved_query_full_definition):
        """
        Updates the saved query via a PUT request to Keen IO Saved Query
        endpoint. The entire query definition must be provided--anything
        excluded will be considered an explicit removal of that property.

        Master key must be set.
        """

        return self.create(query_name, saved_query_full_definition)

    @requires_key(KeenKeys.MASTER)
    def update(self, query_name, saved_query_attributes):
        """
        Given a dict of attributes to be updated, update only those attributes
        in the Saved Query at the resource given by 'query_name'. This will
        perform two HTTP requests--one to fetch the query definition, and one
        to set the new attributes. This method will intend to preserve any
        other properties on the query.

        Master key must be set.
        """

        query_name_attr_name = "query_name"
        refresh_rate_attr_name = "refresh_rate"
        query_attr_name = "query"
        metadata_attr_name = "metadata"

        old_saved_query = self.get(query_name)

        # Create a new query def to send back. We cannot send values for attributes like 'urls',
        # 'last_modified_date', 'run_information', etc.
        new_saved_query = {
            query_name_attr_name: old_saved_query[query_name_attr_name], # expected
            refresh_rate_attr_name: old_saved_query[refresh_rate_attr_name], # expected
            query_attr_name: {}
        }

        # If metadata was set, preserve it. The Explorer UI currently stores information here.
        old_metadata = (old_saved_query[metadata_attr_name]
                       if metadata_attr_name in old_saved_query
                       else None)

        if old_metadata:
            new_saved_query[metadata_attr_name] = old_metadata

        # Preserve any non-empty properties of the existing query. We get back values like None
        # for 'group_by', 'interval' or 'timezone', but those aren't accepted values when updating.
        old_query = old_saved_query[query_attr_name] # expected

        # Shallow copy since we want the entire object heirarchy to start with.
        for (key, value) in six.iteritems(old_query):
            if value:
                new_saved_query[query_attr_name][key] = value

        # Now, recursively overwrite any attributes passed in.
        SavedQueriesInterface._deep_update(new_saved_query, saved_query_attributes)

        return self.create(query_name, new_saved_query)

    @requires_key(KeenKeys.MASTER)
    def delete(self, query_name):
        """
        Deletes a saved query from a project with a query name.
        Master key must be set.
        """

        url = "{0}/{1}".format(self.saved_query_url, query_name)
        self._get_json(HTTPMethods.DELETE, url, self._get_master_key())

        return True

    @staticmethod
    def _deep_update(mapping, updates):
        for (key, value) in six.iteritems(updates):
            if isinstance(mapping, Mapping):
                if isinstance(value, Mapping):
                    next_level_value = SavedQueriesInterface._deep_update(mapping.get(key, {}),
                                                                          value)
                    mapping[key] = next_level_value
                else:
                    mapping[key] = value
            else:
                # Turn the original key into a mapping if it wasn't already
                mapping = { key: value }

        return mapping

    def _get_json(self, http_method, url, key, *args, **kwargs):
        response = self.api.fulfill(
            http_method,
            url,
            headers=utilities.headers(key),
            *args,
            **kwargs)

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
