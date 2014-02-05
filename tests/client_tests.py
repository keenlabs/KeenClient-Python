# -*- coding: utf-8 -*-
import os
import sys
import base64

import datetime
import decimal
import requests

import keen
from keen import exceptions, persistence_strategies, scoped_keys
from keen.client import KeenClient

from .base_test_case import BaseTestCase

try:
    import simplejson as json
except ImportError:
    import json


class ClientTests(BaseTestCase):

    def setUp(self):
        super(ClientTests, self).setUp()
        keen._client = None
        keen.project_id = None
        keen.write_key = None
        keen.read_key = None

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

    def test_module_level_add_event(self):
        keen.project_id = "5004ded1163d66114f000000"
        api_key = "2e79c6ec1d0145be8891bf668599c79a"
        keen.write_key = scoped_keys.encrypt(api_key, {"allowed_operations": ["write"]})
        # client = KeenClient(project_id, write_key=write_key, read_key=read_key)
        keen.add_event("python_test", {"hello": "goodbye"})

    def test_module_level_add_events(self):
        keen.project_id = "5004ded1163d66114f000000"
        api_key = "2e79c6ec1d0145be8891bf668599c79a"
        keen.write_key = scoped_keys.encrypt(api_key, {"allowed_operations": ["write"]})
        # client = KeenClient(project_id, write_key=write_key, read_key=read_key)
        keen.add_events({"python_test": [{"hello": "goodbye"}]})

    def test_environment_variables(self):
        # try addEvent w/out having environment variables
        keen._client = None
        keen.project_id = None
        keen.write_key = None
        keen.read_key = None
        self.assert_raises(exceptions.InvalidEnvironmentError,
                           keen.add_event, "python_test", {"hello": "goodbye"})

        os.environ["KEEN_PROJECT_ID"] = "12345"

        self.assert_raises(exceptions.InvalidEnvironmentError,
                           keen.add_event, "python_test", {"hello": "goodbye"})

        # force client to reinitialize
        keen._client = None
        os.environ["KEEN_WRITE_KEY"] = "abcde"
        self.assert_raises(exceptions.KeenApiError,
                           keen.add_event, "python_test", {"hello": "goodbye"})

    def test_configure_through_code(self):
        keen.project_id = "123456"
        self.assert_raises(exceptions.InvalidEnvironmentError,
                           keen.add_event, "python_test", {"hello": "goodbye"})

        # force client to reinitialize
        keen._client = None
        keen.write_key = "abcdef"
        self.assert_raises(exceptions.KeenApiError,
                           keen.add_event, "python_test", {"hello": "goodbye"})

    def test_generate_image_beacon(self):
        keen.project_id = "5004ded1163d66114f000000"
        api_key = "2e79c6ec1d0145be8891bf668599c79a"
        keen.write_key = scoped_keys.encrypt(api_key, {"allowed_operations": ["write"]})

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

        # make sure URL works
        response = requests.get(url)
        self.assert_equal(200, response.status_code)
        self.assert_equal(
            b"GIF89a\x01\x00\x01\x00\x80\x01\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\n\x00\x01\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02L\x01\x00;",
            response.content)

    def test_generate_image_beacon_timestamp(self):
        # make sure using a timestamp works

        keen.project_id = "5004ded1163d66114f000000"
        api_key = "2e79c6ec1d0145be8891bf668599c79a"
        keen.write_key = scoped_keys.encrypt(api_key, {"allowed_operations": ["write"]})

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


class QueryTests(BaseTestCase):

    def setUp(self):
        super(QueryTests, self).setUp()
        keen._client = None
        keen.project_id = "5004ded1163d66114f000000"
        api_key = "2e79c6ec1d0145be8891bf668599c79a"
        keen.write_key = scoped_keys.encrypt(api_key, {"allowed_operations": ["write"]})
        keen.read_key = scoped_keys.encrypt(api_key, {"allowed_operations": ["read"]})
        keen.add_event("query test", {"number": 5, "string": "foo"})
        keen.add_event("step2", {"number": 5, "string": "foo"})

    def tearDown(self):
        keen.project_id = None
        keen.write_key = None
        keen.read_key = None
        keen._client = None
        super(QueryTests, self).tearDown()

    def get_filter(self):
        return [{"property_name": "number", "operator": "eq", "property_value": 5}]

    def test_count(self):
        resp = keen.count("query test", timeframe="today", filters=self.get_filter())
        assert isinstance(resp, int)

    def test_sum(self):
        resp = keen.sum("query test", target_property="number", timeframe="today")
        assert isinstance(resp, int)

    def test_minimum(self):
        resp = keen.minimum("query test", target_property="number", timeframe="today")
        assert isinstance(resp, int)

    def test_maximum(self):
        resp = keen.maximum("query test", target_property="number", timeframe="today")
        assert isinstance(resp, int)

    def test_average(self):
        resp = keen.average("query test", target_property="number", timeframe="today")
        assert type(resp) in (float, int)

    def test_count_unique(self):
        resp = keen.count_unique("query test", target_property="number", timeframe="today")
        assert isinstance(resp, int)

    def test_select_unique(self):
        resp = keen.select_unique("query test", target_property="number", timeframe="today")
        assert isinstance(resp, list)

    def test_extraction(self):
        resp = keen.extraction("query test", timeframe="today")
        assert isinstance(resp, list)

    def test_multi_analysis(self):
        resp = keen.multi_analysis("query test",
                                   analyses={"total": {"analysis_type": "sum", "target_property": "number"}},
                                   timeframe="today")
        assert isinstance(resp, dict)
        assert isinstance(resp["total"], int)

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
        resp = keen.funnel([step1, step2])
        assert isinstance(resp, list), resp

    def test_group_by(self):
        resp = keen.count("query test", timeframe="today", group_by="number")
        assert isinstance(resp, list)

    def test_multi_group_by(self):
        resp = keen.count("query test", timeframe="today", group_by=["number", "string"])
        assert isinstance(resp, list)
        assert len(resp) == 1

    def test_interval(self):
        resp = keen.count("query test", timeframe="this_2_days", interval="daily")
        assert isinstance(resp, list)


class DefaultJSONEncoderTests(BaseTestCase):

    def setUp(self):
        super(DefaultJSONEncoderTests, self).setUp()
        api_key = "2e79c6ec1d0145be8891bf668599c79a"
        self.client = KeenClient(project_id='5004ded1163d66114f000000',
                                 write_key=scoped_keys.encrypt(api_key, {"allowed_operations": ["write"]}),
                                 read_key=scoped_keys.encrypt(api_key, {"allowed_operations": ["read"]}))

    def tearDown(self):
        self.client = None
        super(DefaultJSONEncoderTests, self).tearDown()

    def test_default_encoder_with_datetime_type(self):
        self.assert_raises(TypeError,
                           self.client.add_event,
                           "sign_ups",
                           {
                               "username": "lloyd",
                               "referred_by": "harry",
                               "confirmed_at": datetime.datetime.utcnow()
                           })


class CustomEncoder(json.JSONEncoder):

    """JSON Encoder class that handles conversion for a number of types not
    supported by the default json library


    - datetime.* objects will be converted with their isoformat() function.
    - Decimal will be converted to a unicode string

    :returns: object that can be converted to json
    """

    def td_format(self, td_object):
        seconds = int(td_object.total_seconds())
        periods = [
            ('year', 60 * 60 * 24 * 365),
            ('month', 60 * 60 * 24 * 30),
            ('day', 60 * 60 * 24),
            ('hour', 60 * 60),
            ('minute', 60),
            ('second', 1)
        ]

        strings = []
        for period_name, period_seconds in periods:
            if seconds > period_seconds:
                period_value, seconds = divmod(seconds, period_seconds)
                if period_value == 1:
                    strings.append("%s %s" % (period_value, period_name))
                else:
                    strings.append("%s %ss" % (period_value, period_name))

        return ", ".join(strings)

    def default(self, obj):
        if isinstance(obj, (datetime.datetime, datetime.date, datetime.time)):
            return obj.isoformat()
        elif isinstance(obj, (datetime.timedelta)):
            return self.td_format(obj)
        elif isinstance(obj, (decimal.Decimal)):
            return unicode(obj)
        else:
            return json.JSONEncoder.default(self, obj)


class CustomJSONEncoderTests(BaseTestCase):

    def setUp(self):
        super(CustomJSONEncoderTests, self).setUp()
        api_key = "2e79c6ec1d0145be8891bf668599c79a"
        self.client = KeenClient(project_id='5004ded1163d66114f000000',
                                 write_key=scoped_keys.encrypt(api_key, {"allowed_operations": ["write"]}),
                                 read_key=scoped_keys.encrypt(api_key, {"allowed_operations": ["read"]}),
                                 json_encoder=CustomEncoder)

    def tearDown(self):
        self.client = None
        super(CustomJSONEncoderTests, self).tearDown()

    def test_custom_encoder_with_datetime_type(self):
        self.client.add_event("sign_ups", {
            "username": "lloyd",
            "referred_by": "harry",
            "confirmed_at": datetime.datetime.utcnow()
        })


# only need to test unicode separately in python2
if sys.version_info[0] > 3:

    class UnicodeTests(BaseTestCase):

        def setUp(self):
            super(UnicodeTests, self).setUp()
            keen._client = None
            keen.project_id = unicode("5004ded1163d66114f000000")
            api_key = unicode("2e79c6ec1d0145be8891bf668599c79a")
            keen.write_key = unicode(api_key)

        def test_unicode(self):
            keen.add_event(unicode("unicode test"), {unicode("number"): 5, "string": unicode("foo")})

        def tearDown(self):
            keen.project_id = None
            keen.write_key = None
            keen.read_key = None
            keen._client = None
            super(UnicodeTests, self).tearDown()
