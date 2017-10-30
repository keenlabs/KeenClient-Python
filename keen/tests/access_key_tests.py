
from keen.tests.base_test_case import BaseTestCase
from keen.tests.client_tests import MockedResponse
from mock import patch

import keen

__author__ = 'BlackVegetable'

class AccessKeyTests(BaseTestCase):

    ACCESS_KEY_NAME = "Bob_Key"
    ACCESS_KEY_ID = "320104AEFFC569EEE60BCAC9BB064DFF9897E391AB8C59608AC0869AFD291B4E"
    ACCESS_KEY_RESPONSE = MockedResponse(
        status_code=201,
        json_response={'name': "Bob_Key",
                       'is_active': True,
                       'permitted': [],
                       'key': '320104AEFFC569EEE60BCAC9BB064DFF9897E391AB8C59608AC0869AFD291B4E',
                       'project_id': '55777979e085574e8ad3523c',
                       'options': {'saved_queries': None,
                                   'writes': None,
                                   'datasets': None,
                                   'cached_queries': None,
                                   'queries': None}})

    UPDATED_ACCESS_KEY_RESPONSE = MockedResponse(
        status_code=201,
        json_response={'name': "Jim_Key",
                       'is_active': False,
                       'permitted': ["queries"],
                       'key': '320104AEFFC569EEE60BCAC9BB064DFF9897E391AB8C59608AC0869AFD291B4E',
                       'project_id': '55777979e085574e8ad3523c',
                       'options': {'saved_queries': None,
                                   'writes': None,
                                   'datasets': None,
                                   'cached_queries': None,
                                   'queries': {
                                       "filters": [{
                                           "property_name": "customer.id",
                                           "operator": "eq",
                                           "property_value": "asdf12345z"
                                        }]}}})

    NO_CONTENT_RESPONSE = MockedResponse(status_code=204, json_response="")

    def setUp(self):
        super(AccessKeyTests, self).setUp()
        keen.project_id = "55777979e085574e8ad3523c"
        keen.write_key = "DEADBEEF"
        keen.read_key = "BADFEED"
        keen.master_key = "BADHORSE"
        self.keys_uri_prefix = "https://api.keen.io/3.0/projects/{0}/keys".format(keen.project_id)

    def _assert_proper_permissions(self, method, permission):
        self.assertTrue(permission in method.call_args[1]["headers"]["Authorization"])

    @patch("requests.Session.post")
    def test_create_access_key(self, post):
        post.return_value = self.ACCESS_KEY_RESPONSE
        resp = keen.create_access_key(self.ACCESS_KEY_NAME)
        self.assertTrue(self.ACCESS_KEY_NAME in post.call_args[1]["data"])
        self._assert_proper_permissions(post, keen.master_key)
        self.assertEqual(resp, self.ACCESS_KEY_RESPONSE.json())

    @patch("requests.Session.get")
    def test_list_access_keys(self, get):
        get.return_value = self.ACCESS_KEY_RESPONSE
        resp = keen.list_access_keys()
        self.assertEqual(self.keys_uri_prefix, get.call_args[0][0])
        self._assert_proper_permissions(get, keen.master_key)
        self.assertEqual(resp, self.ACCESS_KEY_RESPONSE.json())

    @patch("requests.Session.get")
    def test_get_access_key(self, get):
        get.return_value = self.ACCESS_KEY_RESPONSE
        resp = keen.get_access_key(self.ACCESS_KEY_ID)
        self.assertEqual("{0}/{1}".format(self.keys_uri_prefix, self.ACCESS_KEY_ID), get.call_args[0][0])
        self._assert_proper_permissions(get, keen.master_key)
        self.assertEqual(resp, self.ACCESS_KEY_RESPONSE.json())

    @patch("requests.Session.post")
    def test_revoke_access_key(self, post):
        post.return_value = self.NO_CONTENT_RESPONSE
        resp = keen.revoke_access_key(self.ACCESS_KEY_ID)
        self.assertEqual("{0}/{1}/revoke".format(self.keys_uri_prefix, self.ACCESS_KEY_ID), post.call_args[0][0])
        self._assert_proper_permissions(post, keen.master_key)
        self.assertEqual(resp, self.NO_CONTENT_RESPONSE.json())

    @patch("requests.Session.post")
    def test_unrevoke_access_key(self, post):
        post.return_value = self.NO_CONTENT_RESPONSE
        resp = keen.unrevoke_access_key(self.ACCESS_KEY_ID)
        self.assertEqual("{0}/{1}/unrevoke".format(self.keys_uri_prefix, self.ACCESS_KEY_ID), post.call_args[0][0])
        self._assert_proper_permissions(post, keen.master_key)
        self.assertEqual(resp, self.NO_CONTENT_RESPONSE.json())

    @patch("requests.Session.post")
    def test_update_access_key_full(self, post):
        # The update tests have a significant amount of logic that will not be tested via blackbox testing without
        # un-mocking Keen's API. So this is the only test that will really cover any of them, and not even very
        # well.
        post.return_value = self.UPDATED_ACCESS_KEY_RESPONSE
        options_dict = {"queries": self.UPDATED_ACCESS_KEY_RESPONSE.json_response["options"]["queries"]}
        resp = keen.update_access_key_full(self.ACCESS_KEY_ID,
                                           name=self.UPDATED_ACCESS_KEY_RESPONSE.json_response["name"],
                                           is_active=self.UPDATED_ACCESS_KEY_RESPONSE.json_response["is_active"],
                                           permitted=self.UPDATED_ACCESS_KEY_RESPONSE.json_response["permitted"],
                                           options=options_dict)
        self.assertEqual("{0}/{1}".format(self.keys_uri_prefix, self.ACCESS_KEY_ID), post.call_args[0][0])
        self._assert_proper_permissions(post, keen.master_key)
        self.assertEqual(resp, self.UPDATED_ACCESS_KEY_RESPONSE.json())

    @patch("requests.Session.get")
    @patch("requests.Session.post")
    def test_sanity_of_update_functions(self, post, get):
        post.return_value = self.UPDATED_ACCESS_KEY_RESPONSE
        get.return_value = self.UPDATED_ACCESS_KEY_RESPONSE
        # Ensure at the very least that the other access key functions don't crash when run.
        keen.update_access_key_name(self.ACCESS_KEY_ID, name="Marzipan")
        keen.add_access_key_permissions(self.ACCESS_KEY_ID, ["writes"])
        keen.remove_access_key_permissions(self.ACCESS_KEY_ID, ["writes"])
        keen.update_access_key_permissions(self.ACCESS_KEY_ID, ["writes", "cached_queries"])
        keen.update_access_key_options(self.ACCESS_KEY_ID, options={})
        self.assertTrue(True) # Best test assertion ever.
