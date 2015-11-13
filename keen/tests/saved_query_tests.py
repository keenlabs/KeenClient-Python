from keen.tests.base_test_case import BaseTestCase
from keen.client import KeenClient
from keen import exceptions

import responses

class SavedQueryTests(BaseTestCase):

    def setUp(self):
        super(SavedQueryTests, self).setUp()
        self.exp_project_id = "xxxx1234"
        exp_master_key = "abcd3456"
        self.client = KeenClient(
            project_id=self.exp_project_id,
            master_key=exp_master_key
        )

    def test_get_all_saved_queries_keys(self):
        client = KeenClient(project_id="123123")
        self.assertRaises(
            exceptions.InvalidEnvironmentError, client.saved_queries.all
        )

    @responses.activate
    def test_get_all_saved_queries(self):
        saved_queries_response = [
            { "query_name": "first-saved-query", "query": {} },
            { "query_name": "second-saved-query", "query": {} }
        ]
        url = "{0}/{1}/projects/{2}/queries/saved".format(
            self.client.api.base_url,
            self.client.api.api_version,
            self.exp_project_id
        )
        responses.add(
            responses.GET, url, status=200, json=saved_queries_response
        )

        all_saved_queries = self.client.saved_queries.all()

        self.assertEquals(all_saved_queries, saved_queries_response)

    def test_get_one_saved_query_keys(self):
        client = KeenClient(project_id="123123")
        self.assertRaises(
            exceptions.InvalidEnvironmentError,
            lambda: client.saved_queries.get("saved-query-name")
        )

    @responses.activate
    def test_get_one_saved_query(self):
        saved_queries_response = {
            "query_name": "saved-query-name"
        }
        url = "{0}/{1}/projects/{2}/queries/saved/saved-query-name".format(
            self.client.api.base_url,
            self.client.api.api_version,
            self.exp_project_id
        )
        responses.add(
            responses.GET, url, status=200, json=saved_queries_response
        )

        saved_query = self.client.saved_queries.get("saved-query-name")

        self.assertEquals(saved_query, saved_queries_response)

    def test_create_saved_query_master_key(self):
        client = KeenClient(project_id="123123")
        self.assertRaises(
            exceptions.InvalidEnvironmentError,
            lambda: client.saved_queries.create("saved-query-name", {})
        )

    @responses.activate
    def test_create_saved_query(self):
        saved_queries_response = {
            "query_name": "saved-query-name"
        }
        url = "{0}/{1}/projects/{2}/queries/saved/saved-query-name".format(
            self.client.api.base_url,
            self.client.api.api_version,
            self.exp_project_id
        )
        responses.add(
            responses.PUT, url, status=201, json=saved_queries_response
        )

        saved_query = self.client.saved_queries.create("saved-query-name", saved_queries_response)

        self.assertEquals(saved_query, saved_queries_response)

    @responses.activate
    def test_update_saved_query(self):
        saved_queries_response = {
            "query_name": "saved-query-name"
        }
        url = "{0}/{1}/projects/{2}/queries/saved/saved-query-name".format(
            self.client.api.base_url,
            self.client.api.api_version,
            self.exp_project_id
        )
        responses.add(
            responses.PUT, url, status=200, json=saved_queries_response
        )

        saved_query = self.client.saved_queries.update("saved-query-name", saved_queries_response)

        self.assertEquals(saved_query, saved_queries_response)

    def test_delete_saved_query_master_key(self):
        client = KeenClient(project_id="123123", read_key="123123")
        self.assertRaises(
            exceptions.InvalidEnvironmentError,
            lambda: client.saved_queries.delete("saved-query-name")
        )

    @responses.activate
    def test_delete_saved_query(self):
        url = "{0}/{1}/projects/{2}/queries/saved/saved-query-name".format(
            self.client.api.base_url,
            self.client.api.api_version,
            self.exp_project_id
        )
        responses.add(
            responses.DELETE, url, status=204, json=""
        )

        response = self.client.saved_queries.delete("saved-query-name")

        self.assertEquals(response, True)

    @responses.activate
    def test_saved_query_results(self):
        saved_queries_response = {
            "query_name": "saved-query-name",
            "results": {}
        }
        url = "{0}/{1}/projects/{2}/queries/saved/saved-query-name/result".format(
            self.client.api.base_url,
            self.client.api.api_version,
            self.exp_project_id
        )
        responses.add(
            responses.GET, url, status=209, json=saved_queries_response
        )

        response = self.client.saved_queries.results("saved-query-name")

        self.assertEquals(response, saved_queries_response)
