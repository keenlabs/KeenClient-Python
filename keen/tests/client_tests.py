import base64
import json
import os
import datetime
from nose.tools import raises
import requests
from keen import exceptions, persistence_strategies, scoped_keys
import keen
from keen.client import KeenClient
from keen.tests.base_test_case import BaseTestCase
from mock import patch, MagicMock
import sys

__author__ = 'dkador'


class MockedResponse(object):
    def __init__(self, status_code, json_response):
        self.status_code = status_code
        self.json_response = json_response

    def json(self):
        return self.json_response


class MockedFailedResponse(MockedResponse):
    def json(self):
        return self.json_response


@patch("requests.Session.post")
class ClientTests(BaseTestCase):

    SINGLE_ADD_RESPONSE = MockedResponse(status_code=201, json_response={"result": {"hello": "goodbye"}})

    MULTI_ADD_RESPONSE = MockedResponse(status_code=200, json_response={"result": {"hello": "goodbye"}})

    def setUp(self):
        super(ClientTests, self).setUp()
        api_key = "2e79c6ec1d0145be8891bf668599c79a"
        keen._client = None
        keen.project_id = "5004ded1163d66114f000000"
        keen.write_key = scoped_keys.encrypt(api_key, {"allowed_operations": ["write"]})
        keen.read_key = scoped_keys.encrypt(api_key, {"allowed_operations": ["read"]})
        keen.master_key = None

    def test_init(self, post):
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

    def test_direct_persistence_strategy(self, post):
        post.return_value = self.SINGLE_ADD_RESPONSE
        keen.add_event("python_test", {"hello": "goodbye"})
        keen.add_event("python_test", {"hello": "goodbye"})

        post.return_value = self.MULTI_ADD_RESPONSE
        keen.add_events(
            {
                "sign_ups": [{
                    "username": "timmy",
                    "referred_by": "steve",
                    "son_of": "my_mom"
                }],
                "purchases": [
                    {"price": 5},
                    {"price": 6},
                    {"price": 7}
                ]}
        )

    def test_module_level_add_event(self, post):
        post.return_value = self.SINGLE_ADD_RESPONSE
        keen.add_event("python_test", {"hello": "goodbye"})

    def test_module_level_add_events(self, post):
        post.return_value = self.MULTI_ADD_RESPONSE
        keen.add_events({"python_test": [{"hello": "goodbye"}]})

    def test_post_timeout_single(self, post):
        post.side_effect = requests.Timeout
        self.assert_raises(requests.Timeout, keen.add_event, "python_test", {"hello": "goodbye"})

    def test_post_timeout_batch(self, post):
        post.side_effect = requests.Timeout
        self.assert_raises(requests.Timeout, keen.add_events, {"python_test": [{"hello": "goodbye"}]})

    def test_environment_variables(self, post):
        post.return_value = MockedFailedResponse(
            status_code=401,
            # "message" is the description, "error_code" is the name of the class.
            json_response={"message": "authorization error", "error_code": "AdminOnlyEndpointError"},
        )
        # try addEvent w/out having environment variables
        keen._client = None
        keen.project_id = None
        keen.write_key = None
        keen.read_key = None
        keen.master_key = None
        self.assert_raises(exceptions.InvalidEnvironmentError,
                           keen.add_event, "python_test", {"hello": "goodbye"})

        os.environ["KEEN_PROJECT_ID"] = "12345"

        self.assert_raises(exceptions.InvalidEnvironmentError,
                           keen.add_event, "python_test", {"hello": "goodbye"})

        # force client to reinitialize
        keen._client = None
        os.environ["KEEN_PROJECT_ID"] = "12345"
        os.environ["KEEN_WRITE_KEY"] = "abcde"

        self.assert_raises(exceptions.KeenApiError,
                           keen.add_event, "python_test", {"hello": "goodbye"})

    def test_new_client_instance(self, post):
        exp_project_id = "xxxx1234"
        exp_write_key = "yyyy4567"
        exp_read_key = "zzzz8912"
        exp_master_key = "abcd3456"

        # create Client instance
        client = KeenClient(
            project_id=exp_project_id,
            write_key=exp_write_key,
            read_key=exp_read_key,
            master_key=exp_master_key
        )

        # assert values
        self.assertEquals(exp_project_id, client.api.project_id)
        self.assertEquals(exp_write_key, client.api.write_key)
        self.assertEquals(exp_read_key, client.api.read_key)
        self.assertEquals(exp_master_key, client.api.master_key)

    def test_set_keys_using_env_var(self, post):
        # reset Client settings
        keen._client = None
        keen.project_id = None
        keen.write_key = None
        keen.read_key = None
        keen.master_key = None

        # set env vars
        exp_project_id = os.environ["KEEN_PROJECT_ID"] = "xxxx5678"
        exp_write_key = os.environ["KEEN_WRITE_KEY"] = "yyyy8901"
        exp_read_key = os.environ["KEEN_READ_KEY"] = "zzzz2345"
        exp_master_key = os.environ["KEEN_MASTER_KEY"] = "abcd1234"

        keen._initialize_client_from_environment()

        # test values
        self.assertEquals(exp_project_id, keen.project_id)
        self.assertEquals(exp_write_key, keen.write_key)
        self.assertEquals(exp_read_key, keen.read_key)
        self.assertEquals(exp_master_key, keen.master_key)
        self.assertEquals(exp_project_id, keen._client.api.project_id)
        self.assertEquals(exp_write_key, keen._client.api.write_key)
        self.assertEquals(exp_read_key, keen._client.api.read_key)
        self.assertEquals(exp_master_key, keen._client.api.master_key)

        # remove env vars
        del os.environ["KEEN_PROJECT_ID"]
        del os.environ["KEEN_WRITE_KEY"]
        del os.environ["KEEN_READ_KEY"]
        del os.environ["KEEN_MASTER_KEY"]

    def test_set_keys_using_package_var(self, post):
        exp_project_id = keen.project_id = "uuuu5678"
        exp_write_key = keen.write_key = "vvvv8901"
        exp_read_key = keen.read_key = "wwwww2345"
        exp_master_key = keen.master_key = "abcd4567"

        keen._initialize_client_from_environment()

        # test values
        self.assertEquals(exp_project_id, keen.project_id)
        self.assertEquals(exp_write_key, keen.write_key)
        self.assertEquals(exp_read_key, keen.read_key)
        self.assertEquals(exp_master_key, keen.master_key)
        self.assertEquals(exp_project_id, keen._client.api.project_id)
        self.assertEquals(exp_write_key, keen._client.api.write_key)
        self.assertEquals(exp_read_key, keen._client.api.read_key)
        self.assertEquals(exp_master_key, keen._client.api.master_key)

    def test_configure_through_code(self, post):
        client = KeenClient(project_id="123456", read_key=None, write_key=None)
        self.assert_raises(exceptions.InvalidEnvironmentError,
                           client.add_event, "python_test", {"hello": "goodbye"})

        # force client to reinitialize
        client = KeenClient(project_id="123456", read_key=None, write_key="abcdef")
        with patch("requests.Session.post") as post:
            post.return_value = MockedFailedResponse(
                status_code=401,
                json_response={"message": "authorization error", "error_code": "AdminOnlyEndpointError"},
            )
            self.assert_raises(exceptions.KeenApiError,
                               client.add_event, "python_test", {"hello": "goodbye"})

    def test_generate_image_beacon(self, post):
        event_collection = "python_test hello!?"
        event_data = {"a": "b"}
        data = self.base64_encode(json.dumps(event_data))

        # module level should work
        url = keen.generate_image_beacon(event_collection, event_data)
        expected = "https://api.keen.io/3.0/projects/{0}/events/{1}?api_key={2}&data={3}".format(
            keen.project_id, self.url_escape(event_collection), keen.write_key.decode(sys.getdefaultencoding()), data
        )
        self.assert_equal(expected, url)

        # so should instance level
        client = KeenClient(keen.project_id, write_key=keen.write_key, read_key=None)
        url = client.generate_image_beacon(event_collection, event_data)
        self.assert_equal(expected, url)

    def test_generate_image_beacon_timestamp(self, post):
        # make sure using a timestamp works

        event_collection = "python_test"
        event_data = {"a": "b"}
        timestamp = datetime.datetime.utcnow()
        data = self.base64_encode(json.dumps({"a": "b", "keen": {"timestamp": timestamp.isoformat()}}))

        url = keen.generate_image_beacon(event_collection, event_data, timestamp=timestamp)
        expected = "https://api.keen.io/3.0/projects/{0}/events/{1}?api_key={2}&data={3}".format(
            keen.project_id, self.url_escape(event_collection), keen.write_key.decode(sys.getdefaultencoding()), data
        )
        self.assert_equal(expected, url)

    def base64_encode(self, string_to_encode):
        try:
            # python 2
            return base64.b64encode(string_to_encode)
        except TypeError:
            # python 3
            import sys
            encoding = sys.getdefaultencoding()
            base64_bytes = base64.b64encode(bytes(string_to_encode, encoding))
            return base64_bytes.decode(encoding)

    def url_escape(self, url):
        try:
            import urllib
            return urllib.quote(url)
        except AttributeError:
            import urllib.parse
            return urllib.parse.quote(url)


@patch("requests.Session.get")
class QueryTests(BaseTestCase):

    INT_RESPONSE = MockedResponse(status_code=200, json_response={"result": 2})

    LIST_RESPONSE = MockedResponse(
        status_code=200, json_response={"result": [{"value": {"total": 1}}, {"value": {"total": 2}}]})

    def setUp(self):
        super(QueryTests, self).setUp()
        keen._client = None
        keen.project_id = "5004ded1163d66114f000000"
        api_key = "2e79c6ec1d0145be8891bf668599c79a"
        keen.write_key = scoped_keys.encrypt(api_key, {"allowed_operations": ["write"]})
        keen.read_key = scoped_keys.encrypt(api_key, {"allowed_operations": ["read"]})
        # keen.add_event("query test", {"number": 5, "string": "foo"})
        # keen.add_event("step2", {"number": 5, "string": "foo"})

    def tearDown(self):
        keen.project_id = None
        keen.write_key = None
        keen.read_key = None
        keen.master_key = None
        keen._client = None
        super(QueryTests, self).tearDown()

    def get_filter(self):
        return [{"property_name": "number", "operator": "eq", "property_value": 5}]

    def test_count(self, get):
        get.return_value = self.INT_RESPONSE
        resp = keen.count("query test", timeframe="today", filters=self.get_filter())
        self.assertEqual(type(resp), int)

    def test_sum(self, get):
        get.return_value = self.INT_RESPONSE
        resp = keen.sum("query test", target_property="number", timeframe="today")
        self.assertEqual(type(resp), int)

    def test_minimum(self, get):
        get.return_value = self.INT_RESPONSE
        resp = keen.minimum("query test", target_property="number", timeframe="today")
        self.assertEqual(type(resp), int)

    def test_maximum(self, get):
        get.return_value = self.INT_RESPONSE
        resp = keen.maximum("query test", target_property="number", timeframe="today")
        self.assertEqual(type(resp), int)

    def test_average(self, get):
        get.return_value = self.INT_RESPONSE
        resp = keen.average("query test", target_property="number", timeframe="today")
        self.assertTrue(type(resp) in (int, float), type(resp))

    def test_median(self, get):
        get.return_value = self.INT_RESPONSE
        resp = keen.median("query test", target_property="number", timeframe="today")
        self.assertTrue(type(resp) in (int, float), type(resp))

    def test_percentile(self, get):
        get.return_value = self.INT_RESPONSE
        resp = keen.percentile("query test", target_property="number", percentile=80, timeframe="today")
        self.assertTrue(type(resp) in (int, float), type(resp))

    def test_count_unique(self, get):
        get.return_value = self.INT_RESPONSE
        resp = keen.count_unique("query test", target_property="number", timeframe="today")
        self.assertEqual(type(resp), int)

    def test_select_unique(self, get):
        get.return_value = self.LIST_RESPONSE
        resp = keen.select_unique("query test", target_property="number", timeframe="today")
        self.assertEqual(type(resp), list)

    def test_extraction(self, get):
        get.return_value = self.LIST_RESPONSE
        resp = keen.extraction("query test", timeframe="today", property_names=["number"])
        self.assertEqual(type(resp), list)
        for event in resp:
            self.assertTrue("string" not in event)

    def test_multi_analysis(self, get):
        get.return_value = self.LIST_RESPONSE
        resp = keen.multi_analysis("query test",
                                   analyses={"total": {"analysis_type": "sum", "target_property": "number"}},
                                   timeframe="today", interval="hourly")
        self.assertEqual(type(resp), list)
        for result in resp:
            self.assertEqual(type(result["value"]["total"]), int)

    def test_funnel(self, get):
        get.return_value = self.LIST_RESPONSE

        step1 = {
            "event_collection": "signed up",
            "actor_property": "visitor.guid",
            "timeframe": "today"
        }
        step2 = {
            "event_collection": "completed profile",
            "actor_property": "user.guid",
            "timeframe": "today"
        }

        resp = keen.funnel([step1, step2])
        self.assertEqual(type(resp), list)

    def test_funnel_return_all_keys(self, get):
        get.return_value = MockedResponse(status_code=200, json_response={
            "result": [],
            "actors": [],
            "random_key": [],
            "steps": []
        })

        resp = keen.funnel([1, 2], all_keys=True)
        self.assertEquals(type(resp), dict)
        self.assertIn("actors", resp)
        self.assertIn("random_key", resp)

    def test_group_by(self, get):
        get.return_value = self.LIST_RESPONSE
        resp = keen.count("query test", timeframe="today", group_by="number")
        self.assertEqual(type(resp), list)

    def test_multi_group_by(self, get):
        get.return_value = self.LIST_RESPONSE
        resp = keen.count("query test", timeframe="today", group_by=["number", "string"])
        self.assertEqual(type(resp), list)

    def test_interval(self, get):
        get.return_value = self.LIST_RESPONSE
        resp = keen.count("query test", timeframe="this_2_days", interval="daily")
        self.assertEqual(type(resp), list)

    def test_passing_invalid_custom_api_client(self, get):
        class CustomApiClient(object):
            def __init__(self, project_id, write_key=None, read_key=None,
                         base_url=None, api_version=None, **kwargs):
                super(CustomApiClient, self).__init__()
                self.project_id = project_id
                self.write_key = write_key
                self.read_key = read_key
                if base_url:
                    self.base_url = base_url
                if api_version:
                    self.api_version = api_version

        api_key = "2e79c6ec1d0145be8891bf668599c79a"
        client = KeenClient("5004ded1163d66114f000000", write_key=scoped_keys.encrypt(api_key, {"allowed_operations": ["write"]}), read_key=scoped_keys.encrypt(api_key, {"allowed_operations": ["read"]}), api_class=CustomApiClient)

        # Should raise an error, we never added this method on our class
        # But it shows it is actually using our class
        self.assertRaises(TypeError, client.add_event)

    def test_timeout_count(self, get):
        get.side_effect = requests.Timeout
        client = KeenClient(keen.project_id, write_key=None, read_key=keen.read_key, get_timeout=0.0001)
        self.assert_raises(requests.Timeout, client.count, "query test", timeframe="today", filters=self.get_filter())
        # Make sure the requests library was called with `timeout`.
        self.assert_equals(get.call_args[1]["timeout"], 0.0001)


@patch("requests.Session.delete")
class DeleteTests(BaseTestCase):

    def setUp(self):
        super(DeleteTests, self).setUp()
        keen._client = None
        keen.project_id = "1k4jb23kjbkjkjsd"
        keen.master_key = "sdofnasofagaergub"

    def tearDown(self):
        keen._client = None
        keen.project_id = None
        keen.master_key = None
        super(DeleteTests, self).tearDown()

    def test_delete_events(self, delete):
        delete.return_value = MockedRequest(status_code=204, json_response=[])
        # Assert that the mocked delete function is called the way we expect.
        keen.delete_events("foo", filters=[{"property_name": 'username', "operator": 'eq', "property_value": 'Bob'}])
        # Check that the URL is generated correctly.
        self.assertEqual("https://api.keen.io/3.0/projects/1k4jb23kjbkjkjsd/events/foo", delete.call_args[0][0])
        # Check that the master_key is in the Authorization header.
        self.assertTrue(keen.master_key in delete.call_args[1]["headers"]["Authorization"])

# only need to test unicode separately in python2
if sys.version_info[0] < 3:

    class UnicodeTests(BaseTestCase):
        def setUp(self):
            super(UnicodeTests, self).setUp()
            keen._client = None
            keen.project_id = unicode("5004ded1163d66114f000000")
            api_key = unicode("2e79c6ec1d0145be8891bf668599c79a")
            keen.write_key = unicode(api_key)

        @patch("requests.Session.post", MagicMock(return_value=MockedResponse(status_code=201, json_response=[0, 1, 2])))
        def test_add_event_with_unicode(self):
            keen.add_event(unicode("unicode test"), {unicode("number"): 5, "string": unicode("foo")})

        def tearDown(self):
            keen.project_id = None
            keen.write_key = None
            keen.read_key = None
            keen.master_key = None
            keen._client = None
            super(UnicodeTests, self).tearDown()
