import json

import responses

from keen import exceptions
from keen.client import KeenClient
from keen.tests.base_test_case import BaseTestCase


class CachedDatasetsTestCase(BaseTestCase):

    def setUp(self):
        super(CachedDatasetsTestCase, self).setUp()
        self.organization_id = "1234xxxx5678"
        self.project_id = "xxxx1234"
        self.read_key = "abcd5678read"
        self.master_key = "abcd5678master"
        self.client = KeenClient(
            project_id=self.project_id,
            read_key=self.read_key,
            master_key=self.master_key
        )

        self.datasets = [
            {
                "project_id": self.project_id,
                "organization_id": self.organization_id,
                "dataset_name": "DATASET_NAME_1",
                "display_name": "a first dataset wee",
                "query": {
                    "project_id": self.project_id,
                    "analysis_type": "count",
                    "event_collection": "best collection",
                    "filters": [
                                {
                                    "property_name": "request.foo",
                                    "operator": "lt",
                                    "property_value": 300,
                                }
                    ],
                    "timeframe": "this_500_hours",
                    "timezone": "US/Pacific",
                    "interval": "hourly",
                    "group_by": ["exception.name"],
                },
                "index_by": ["project.id"],
                "last_scheduled_date": "2016-11-04T18:03:38.430Z",
                "latest_subtimeframe_available": "2016-11-04T19:00:00.000Z",
                "milliseconds_behind": 3600000,
            },
            {
                "project_id": self.project_id,
                "organization_id": self.organization_id,
                "dataset_name": "DATASET_NAME_10",
                "display_name": "tenth dataset wee",
                "query": {
                    "project_id": self.project_id,
                    "analysis_type": "count",
                    "event_collection": "tenth best collection",
                    "filters": [],
                    "timeframe": "this_500_days",
                    "timezone": "UTC",
                    "interval": "daily",
                    "group_by": ["analysis_type"],
                },
                "index_by": ["project.organization.id"],
                "last_scheduled_date": "2016-11-04T19:28:36.639Z",
                "latest_subtimeframe_available": "2016-11-05T00:00:00.000Z",
                "milliseconds_behind": 3600000,
            },
        ]

    def test_get_all_raises_with_no_keys(self):
        client = KeenClient(project_id=self.project_id)

        with self.assertRaises(exceptions.InvalidEnvironmentError):
            client.cached_datasets.all()

    @responses.activate
    def test_get_all(self):
        keen_response = {
            "datasets": self.datasets,
            "next_page_url": (
                "https://api.keen.io/3.0/projects/{0}/datasets?"
                "limit=LIMIT&after_name={1}"
            ).format(self.project_id, self.datasets[-1]['dataset_name'])
        }

        url = "{0}/{1}/projects/{2}/datasets".format(
            self.client.api.base_url,
            self.client.api.api_version,
            self.project_id
        )

        responses.add(
            responses.GET, url, status=200, json=keen_response
        )

        all_cached_datasets = self.client.cached_datasets.all()

        self.assertEquals(all_cached_datasets, keen_response)

    def test_get_one_raises_with_no_keys(self):
        client = KeenClient(project_id=self.project_id)

        with self.assertRaises(exceptions.InvalidEnvironmentError):
            client.cached_datasets.get()

    @responses.activate
    def test_get_one(self):
        keen_response = self.datasets[0]

        url = "{0}/{1}/projects/{2}/datasets/{3}".format(
            self.client.api.base_url,
            self.client.api.api_version,
            self.project_id,
            self.datasets[0]['dataset_name']
        )

    def test_create_raises_with_no_keys(self):
        client = KeenClient(project_id=self.project_id)

        with self.assertRaises(exceptions.InvalidEnvironmentError):
            client.cached_datasets.create(
                "NEW_DATASET", {}, "product.id", "My new dataset"
            )

    def test_create_raises_with_read_key(self):
        client = KeenClient(project_id=self.project_id, read_key=self.read_key)

        with self.assertRaises(exceptions.InvalidEnvironmentError):
            client.cached_datasets.create(
                "NEW_DATASET", {}, "product.id", "My new dataset"
            )

    @responses.activate
    def test_create(self):
        dataset_name = "NEW_DATASET"
        display_name = "My new dataset"
        query = {
            "project_id": "PROJECT ID",
            "analysis_type": "count",
            "event_collection": "purchases",
            "filters": [
                {
                    "property_name": "price",
                    "operator": "gte",
                    "property_value": 100
                }
            ],
            "timeframe": "this_500_days",
            "timezone": None,
            "interval": "daily",
            "group_by": ["ip_geo_info.country"]
        }
        index_by = "product.id"

        keen_response = {
            "project_id": self.project_id,
            "organization_id": self.organization_id,
            "dataset_name": dataset_name,
            "display_name": display_name,
            "query": query,
            "index_by": index_by,
            "last_scheduled_date": "1970-01-01T00:00:00.000Z",
            "latest_subtimeframe_available": "1970-01-01T00:00:00.000Z",
            "milliseconds_behind": 3600000
        }

        url = "{0}/{1}/projects/{2}/datasets/{3}".format(
            self.client.api.base_url,
            self.client.api.api_version,
            self.project_id,
            dataset_name
        )

        responses.add(responses.PUT, url, status=201, json=keen_response)

        dataset = self.client.cached_datasets.create(
            dataset_name, query, index_by, display_name
        )

        self.assertEqual(dataset, keen_response)

    def test_results_raises_with_no_keys(self):
        client = KeenClient(project_id=self.project_id)

        with self.assertRaises(exceptions.InvalidEnvironmentError):
            client.cached_datasets.results(
                "DATASET_ONE", "product.id", "this_100_days"
            )

    @responses.activate
    def test_results(self):
        keen_response = {
            "result": [
                {
                    "timeframe": {
                        "start": "2016-11-02T00:00:00.000Z",
                        "end": "2016-11-02T00:01:00.000Z"
                    },
                    "value": [
                        {
                            "exception.name": "ValueError",
                            "result": 20
                        },
                        {
                            "exception.name": "KeyError",
                            "result": 18
                        }
                    ]
                },
                {
                    "timeframe": {
                        "start": "2016-11-02T01:00:00.000Z",
                        "end": "2016-11-02T02:00:00.000Z"
                    },
                    "value": [
                        {
                            "exception.name": "ValueError",
                            "result": 1
                        },
                        {
                            "exception.name": "KeyError",
                            "result": 13
                        }
                    ]
                }
            ]
        }

        dataset_name = self.datasets[0]["dataset_name"]
        index_by = self.project_id
        timeframe = "this_two_hours"

        url = "{0}/{1}/projects/{2}/datasets/{3}/results?index_by={4}&timeframe={5}".format(
            self.client.api.base_url,
            self.client.api.api_version,
            self.project_id,
            dataset_name,
            index_by,
            timeframe
        )

        responses.add(
            responses.GET,
            url,
            status=200,
            json=keen_response,
            match_querystring=True
        )

        results = self.client.cached_datasets.results(
            dataset_name, index_by, timeframe
        )

        self.assertEqual(results, keen_response)

    @responses.activate
    def test_results_absolute_timeframe(self):
        keen_response = {
            "result": [
                {
                    "timeframe": {
                        "start": "2016-11-02T00:00:00.000Z",
                        "end": "2016-11-02T00:01:00.000Z"
                    },
                    "value": [
                        {
                            "exception.name": "ValueError",
                            "result": 20
                        },
                        {
                            "exception.name": "KeyError",
                            "result": 18
                        }
                    ]
                },
                {
                    "timeframe": {
                        "start": "2016-11-02T01:00:00.000Z",
                        "end": "2016-11-02T02:00:00.000Z"
                    },
                    "value": [
                        {
                            "exception.name": "ValueError",
                            "result": 1
                        },
                        {
                            "exception.name": "KeyError",
                            "result": 13
                        }
                    ]
                }
            ]
        }

        dataset_name = self.datasets[0]["dataset_name"]
        index_by = self.project_id
        timeframe = {
            "start": "2016-11-02T00:00:00.000Z",
            "end": "2016-11-02T02:00:00.000Z"
        }

        url = "{0}/{1}/projects/{2}/datasets/{3}/results?index_by={4}&timeframe={5}".format(
            self.client.api.base_url,
            self.client.api.api_version,
            self.project_id,
            dataset_name,
            index_by,
            json.dumps(timeframe)
        )

        responses.add(
            responses.GET,
            url,
            status=200,
            json=keen_response,
            match_querystring=True
        )

        results = self.client.cached_datasets.results(
            dataset_name, index_by, timeframe
        )

        self.assertEqual(results, keen_response)

    @responses.activate
    def test_results_multiple_index_by(self):
        keen_response = {
            "result": [
                {
                    "timeframe": {
                        "start": "2016-11-02T00:00:00.000Z",
                        "end": "2016-11-02T00:01:00.000Z"
                    },
                    "value": [
                        {
                            "exception.name": "ValueError",
                            "result": 20
                        },
                        {
                            "exception.name": "KeyError",
                            "result": 18
                        }
                    ]
                },
                {
                    "timeframe": {
                        "start": "2016-11-02T01:00:00.000Z",
                        "end": "2016-11-02T02:00:00.000Z"
                    },
                    "value": [
                        {
                            "exception.name": "ValueError",
                            "result": 1
                        },
                        {
                            "exception.name": "KeyError",
                            "result": 13
                        }
                    ]
                }
            ]
        }

        dataset_name = self.datasets[0]["dataset_name"]
        index_by = [self.project_id, 'another_id']
        timeframe = "this_two_hours"

        url = "{0}/{1}/projects/{2}/datasets/{3}/results?index_by={4}&timeframe={5}".format(
            self.client.api.base_url,
            self.client.api.api_version,
            self.project_id,
            dataset_name,
            json.dumps(index_by),
            timeframe
        )

        responses.add(
            responses.GET,
            url,
            status=200,
            json=keen_response,
            match_querystring=True
        )

        results = self.client.cached_datasets.results(
            dataset_name, index_by, timeframe
        )

        self.assertEqual(results, keen_response)

    def test_delete_raises_with_no_keys(self):
        client = KeenClient(project_id=self.project_id)
        with self.assertRaises(exceptions.InvalidEnvironmentError):
            client.cached_datasets.delete("MY_DATASET_NAME")

    def test_create_raises_with_read_key(self):
        client = KeenClient(project_id=self.project_id, read_key=self.read_key)
        with self.assertRaises(exceptions.InvalidEnvironmentError):
            client.cached_datasets.delete("MY_DATASET_NAME")

    @responses.activate
    def test_delete(self):
        dataset_name = "MY_DATASET_NAME"
        url = "{0}/{1}/projects/{2}/datasets/{3}".format(
            self.client.api.base_url, self.client.api.api_version, self.project_id, dataset_name)
        responses.add(responses.DELETE, url, status=204)

        response = self.client.cached_datasets.delete(dataset_name)

        self.assertTrue(response)
