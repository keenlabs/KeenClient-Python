from keen.api import KeenApi
from keen import exceptions

class SavedQueriesInterface:

    def __init__(self, project_id, master_key, read_key):
        self.project_id = project_id
        self.master_key = master_key
        self.read_key = read_key

    def all(self):
        """
        Gets all saved queries for a project from the Keen IO API.
        Master key must be set.
        """
        keen_api = KeenApi(self.project_id, master_key=self.master_key)
        self._check_for_master_key()
        url = "{0}/{1}/projects/{2}/queries/saved".format(
            keen_api.base_url, keen_api.api_version, self.project_id
        )
        response = keen_api.fulfill("get", url, headers=self._headers())

        return response.json()

    def get(self, query_name):
        """
        Gets a single saved query for a project from the Keen IO API given a
        query name.
        Master key must be set.
        """
        keen_api = KeenApi(self.project_id, master_key=self.master_key)
        self._check_for_master_key()
        url = "{0}/{1}/projects/{2}/queries/saved/{3}".format(
            keen_api.base_url, keen_api.api_version, self.project_id, query_name
        )
        response = keen_api.fulfill("get", url, headers=self._headers())
        keen_api._error_handling(response)

        return response.json()

    def results(self, query_name):
        """
        Gets a single saved query with a 'result' object for a project from thei
        Keen IO API given a query name.
        Read or Master key must be set.
        """
        keen_api = KeenApi(self.project_id, master_key=self.master_key)
        self._check_for_master_or_read_key()
        url = "{0}/{1}/projects/{2}/queries/saved/{3}/result".format(
            keen_api.base_url, keen_api.api_version, self.project_id, query_name
        )
        key = self.master_key if self.master_key else self.read_key
        response = keen_api.fulfill("get", url, headers={"Authorization": key })
        keen_api._error_handling(response)

        return response.json()

    def create(self, query_name, saved_query):
        """
        Creates the saved query via a PUT request to Keen IO Saved Query endpoint. Master key must be set.
        """
        keen_api = KeenApi(self.project_id, master_key=self.master_key)
        self._check_for_master_key()
        url = "{0}/{1}/projects/{2}/queries/saved/{3}".format(
            keen_api.base_url, keen_api.api_version, self.project_id, query_name
        )
        response = keen_api.fulfill(
            "put", url, headers=self._headers(), data=saved_query
        )
        keen_api._error_handling(response)

        return response.json()

    def update(self, query_name, saved_query):
        """
        Updates the saved query via a PUT request to Keen IO Saved Query
        endpoint.
        Master key must be set.
        """
        return self.create(query_name, saved_query)

    def delete(self, query_name):
        """
        Deletes a saved query from a project with a query name.
        Master key must be set.
        """
        keen_api = KeenApi(self.project_id, master_key=self.master_key)
        self._check_for_master_key()
        url = "{0}/{1}/projects/{2}/queries/saved/{3}".format(
            keen_api.base_url, keen_api.api_version, self.project_id, query_name
        )
        response = keen_api.fulfill("delete", url, headers=self._headers())
        keen_api._error_handling(response)

        return True

    def _headers(self):
        return {"Authorization": self.master_key}

    def _check_for_master_key(self):
        if not self.master_key:
            raise exceptions.InvalidEnvironmentError(
                "The Keen IO API requires a master key to perform this operation on saved queries. "
                "Please set a 'master_key' when initializing the "
                "KeenApi object."
            )

    def _check_for_master_or_read_key(self):
        if not (self.read_key or self.master_key):
            raise exceptions.InvalidEnvironmentError(
                "The Keen IO API requires a read key or master key to perform this operation on saved queries. "
                "Please set a 'read_key' or 'master_key' when initializing the "
                "KeenApi object."
            )
