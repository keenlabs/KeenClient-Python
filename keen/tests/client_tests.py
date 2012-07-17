from keen import PersistenceStrategy, exceptions
from keen.client import KeenClient
from keen.tests.base_test_case import BaseTestCase

__author__ = 'dkador'

class ClientTests(BaseTestCase):
    def test_init(self):
        def positive_helper(project_id, auth_token, **kwargs):
            client = KeenClient(project_id, auth_token, **kwargs)
            self.assert_is_not_none(client)
            self.assert_equal(project_id, client.project_id)
            self.assert_equal(auth_token, client.auth_token)
            return client

        def negative_helper(expected_exception, project_id, auth_token,
                            **kwargs):
            with self.assert_raises(expected_exception) as cm:
                KeenClient(project_id, auth_token, **kwargs)
            # try to turn the exception into a string to test the __str__
            # method
            self.assert_true(str(cm.exception))
            return cm.exception

        # real strings for both project id and auth token should work
        positive_helper("project_id", "auth_token")

        # non-strings shouldn't work
        e = negative_helper(exceptions.InvalidProjectIdError, 5, "auth_token")
        self.assert_equal(5, e.project_id)
        negative_helper(exceptions.InvalidProjectIdError, None, "auth_token")
        negative_helper(exceptions.InvalidProjectIdError, "", "auth_token")
        e = negative_helper(exceptions.InvalidAuthTokenError, "project_id", 6)
        self.assert_equal(6, e.auth_token)
        negative_helper(exceptions.InvalidAuthTokenError, "project_id", None)
        negative_helper(exceptions.InvalidAuthTokenError, "project_id", "")

        # both persistence strategies should work
        client = positive_helper("project_id", "auth_token",
                        save_type=PersistenceStrategy.DIRECT)
        self.assert_equal(PersistenceStrategy.DIRECT,
                          client.persistence_strategy)
        positive_helper("project_id", "auth_token",
                        save_type=PersistenceStrategy.REDIS)
        self.assert_equal(PersistenceStrategy.REDIS,
                          client.persistence_strategy)
