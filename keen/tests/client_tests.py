from keen.client import KeenClient
from keen.tests.base_test_case import BaseTestCase

__author__ = 'dkador'

class ClientTests(BaseTestCase):
    def test_init(self):
        client = KeenClient("project_id", "auth_token")
        self.assert_is_not_none(client)