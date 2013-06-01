from keen import exceptions, persistence_strategies, scoped_keys
from keen.client import KeenClient
from keen.tests.base_test_case import BaseTestCase

__author__ = 'dkador'


class ClientTests(BaseTestCase):
    def test_init(self):
        def positive_helper(project_id, **kwargs):
            client = KeenClient(project_id, **kwargs)
            self.assert_not_equal(client, None)
            self.assert_equal(project_id, client.project_id)
            return client

        def negative_helper(expected_exception, project_id,
                            **kwargs):
            try:
                KeenClient(project_id, **kwargs)
            except expected_exception as e:
                self.assert_true(str(e))
                return e

        # real strings for project id should work
        positive_helper("project_id")

        # non-strings shouldn't work
        e = negative_helper(exceptions.InvalidProjectIdError, 5)
        self.assert_equal(5, e.project_id)
        negative_helper(exceptions.InvalidProjectIdError, None)
        negative_helper(exceptions.InvalidProjectIdError, "")

        # test persistence strategies

        # if you don't ask for a specific one, you get the direct strategy
        client = positive_helper("project_id")
        self.assert_true(isinstance(client.persistence_strategy,
                                    persistence_strategies.DirectPersistenceStrategy))
        # specifying a valid one should work!
        client = positive_helper("project_id",
                                 persistence_strategy=None)
        self.assert_true(isinstance(client.persistence_strategy,
                                    persistence_strategies.DirectPersistenceStrategy))
        # needs to be an instance of a strategy, not anything else
        negative_helper(exceptions.InvalidPersistenceStrategyError,
                        "project_id", persistence_strategy="abc")
        # needs to be an instance of a strategy, not the class
        negative_helper(exceptions.InvalidPersistenceStrategyError,
                        "project_id",
                        persistence_strategy=persistence_strategies.DirectPersistenceStrategy)

    def test_direct_persistence_strategy(self):
        project_id = "5004ded1163d66114f000000"
        api_key = "2e79c6ec1d0145be8891bf668599c79a"
        write_key = scoped_keys.encrypt(api_key, {"allowed_operations": ["write"]})
        read_key = scoped_keys.encrypt(api_key, {"allowed_operations": ["read"]})
        client = KeenClient(project_id, write_key=write_key, read_key=read_key)
        client.add_event("python_test", {"hello": "goodbye"})
        client.add_event("python_test", {"hello": "goodbye"})
        client.add_events(
            {"sign_ups": [
                    { 
                      "username": "timmy",
                      "referred_by": "steve",
                      "son_of": "my_mom"
                    },
            ],
            "purchases": [
                { "price": 5 },
                { "price": 6 },
                { "price": 7 }
            ]})

class QueryTests(BaseTestCase):
    def setUp(self):
        project_id = "5004ded1163d66114f000000"
        api_key = "2e79c6ec1d0145be8891bf668599c79a"
        write_key = scoped_keys.encrypt(api_key, {"allowed_operations": ["write"]})
        read_key = scoped_keys.encrypt(api_key, {"allowed_operations": ["read"]})
        self.client = KeenClient(project_id, write_key=write_key, read_key=read_key)
        self.client.add_event("query test", {"number":5})
        self.client.add_event("step2", {"number":5})

    def get_filter(self):
        return [{"property_name":"number","operator":"eq","property_value":5}]

    def test_count(self):
        resp = self.client.count("query test", timeframe="today", filters=self.get_filter())
        assert type(resp) is int

    def test_sum(self):
        resp = self.client.sum("query test", target_property="number", timeframe="today")
        assert type(resp) is int

    def test_minimum(self):
        resp = self.client.minimum("query test", target_property="number", timeframe="today")
        assert type(resp) is int

    def test_maximum(self):
        resp = self.client.maximum("query test", target_property="number", timeframe="today")
        assert type(resp) is int

    def test_average(self):
        resp = self.client.average("query test", target_property="number", timeframe="today")
        assert type(resp) is float

    def test_count_unique(self):
        resp = self.client.count_unique("query test", target_property="number", timeframe="today")
        assert type(resp) is int

    def test_select_unique(self):
        resp = self.client.select_unique("query test", target_property="number", timeframe="today")
        assert type(resp) is list

    def test_extraction(self):
        resp = self.client.extraction("query test", timeframe="today")
        assert type(resp) is list

    def test_multi_analysis(self):
        resp = self.client.multi_analysis("query test", analyses={"total":{"analysis_type":"sum", "target_property":"number"}}, timeframe="today")
        assert type(resp) is dict
        assert type(resp["total"]) is int

    def test_funnel(self):
        step1 = {
            "event_collection": "query test",
            "actor_property": "number",
            "timeframe": "today"
        }
        step2 = {
            "event_collection": "step2",
            "actor_property": "number",
            "timeframe": "today"
        }
        resp = self.client.funnel([step1, step2])
        assert type(resp) is list, resp

    def test_group_by(self):
        resp = self.client.count("query test", timeframe="today", group_by="number")
        assert type(resp) is list

    def test_interval(self):
        resp = self.client.count("query test", timeframe="this_2_days", interval="daily")
        assert type(resp) is list
