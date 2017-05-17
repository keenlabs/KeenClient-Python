import copy
import json
import re
from requests.exceptions import HTTPError
import responses

from keen.tests.base_test_case import BaseTestCase
from keen.client import KeenClient
from keen import exceptions


class SavedQueryTests(BaseTestCase):

    def setUp(self):
        super(SavedQueryTests, self).setUp()
        self.exp_project_id = "xxxx1234"
        exp_master_key = "abcd3456"
        self.client = KeenClient(
            project_id=self.exp_project_id,
            read_key="efgh7890",
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

        self.assertEqual(saved_query, saved_queries_response)

    @responses.activate
    def test_update_saved_query(self):
        unacceptable_attr = "run_information"
        metadata_attr_name = "metadata"

        original_query = {
            "query_name": "saved-query-name",
            "refresh_rate": 14400,
            "query": {
                "analysis_type": "average",
                "event_collection": "TheCollection",
                "target_property": "TheProperty",
                "timeframe": "this_2_weeks"
            },
            metadata_attr_name: { "foo": "bar" },
            unacceptable_attr: { "foo": "bar" }
        }

        url = "{0}/{1}/projects/{2}/queries/saved/saved-query-name".format(
            self.client.api.base_url,
            self.client.api.api_version,
            self.exp_project_id
        )

        responses.add(
            responses.GET, url, status=200, json=original_query
        )

        updated_query = { "query": {} } # copy.deepcopy(original_query)
        new_analysis_type = "sum"
        updated_query["query"]["analysis_type"] = new_analysis_type

        def request_callback(request):
            payload = json.loads(request.body)

            # Ensure update() round-trips some necessary things like "metadata"
            self.assertEqual(payload[metadata_attr_name], original_query[metadata_attr_name])

            # Ensure update() doesn't pass unacceptable attributes
            self.assertNotIn(unacceptable_attr, payload)

            # Ensure update() merges deep updates
            self.assertEqual(payload["query"]["analysis_type"], new_analysis_type)
            payload["query"]["analysis_type"] = "average"
            payload[unacceptable_attr] = original_query[unacceptable_attr]
            self.assertEqual(payload, original_query)

            headers = {}
            return (200, headers, json.dumps(updated_query))

        responses.add_callback(
            responses.PUT,
            url,
            callback=request_callback,
            content_type='application/json',
        )

        saved_query = self.client.saved_queries.update("saved-query-name", updated_query)

        self.assertEqual(saved_query, updated_query)

    @responses.activate
    def test_update_full_saved_query(self):
        saved_queries_response = {
            "query_name": "saved-query-name",
            "refresh_rate": 14400,
            "query": {
                "analysis_type": "average",
                "event_collection": "TheCollection",
                "target_property": "TheProperty",
                "timeframe": "this_2_weeks"
            }
        }

        url = "{0}/{1}/projects/{2}/queries/saved/saved-query-name".format(
            self.client.api.base_url,
            self.client.api.api_version,
            self.exp_project_id
        )

        # Unlike update(), update_full() should not be fetching the existing definition.
        exception = HTTPError("No GET expected when performing a full update.")
        responses.add(responses.GET, re.compile(".*"), body=exception)

        def request_callback(request):
            payload = json.loads(request.body)

            # Ensure update_full() passes along the unaltered complete Saved/Cached Query def.
            self.assertEqual(payload, saved_queries_response)
            headers = {}
            return (200, headers, json.dumps(saved_queries_response))

        responses.add_callback(
            responses.PUT,
            url,
            callback=request_callback,
            content_type='application/json',
        )

        saved_query = self.client.saved_queries.update_full("saved-query-name", saved_queries_response)

        self.assertEqual(saved_query, saved_queries_response)

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
