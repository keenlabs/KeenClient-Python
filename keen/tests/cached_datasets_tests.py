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
