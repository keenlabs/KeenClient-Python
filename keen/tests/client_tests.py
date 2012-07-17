from keen import  exceptions, persistence_strategies
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

        # test persistence strategies

        # if you don't ask for a specific one, you get the direct strategy
        client = positive_helper("project_id", "auth_token")
        self.assert_is_instance(client.persistence_strategy,
                                persistence_strategies.DirectPersistenceStrategy)
        # specifying a valid one should work!
        client = positive_helper("project_id", "auth_token",
                                 persistence_strategy=None)
        self.assert_is_instance(client.persistence_strategy,
                                persistence_strategies.DirectPersistenceStrategy)
        # needs to be an instance of a strategy, not anything else
        negative_helper(exceptions.InvalidPersistenceStrategyError,
                        "project_id", "auth_token", persistence_strategy="abc")
        # needs to be an instance of a strategy, not the class
        negative_helper(exceptions.InvalidPersistenceStrategyError,
                        "project_id", "auth_token",
                        persistence_strategy=persistence_strategies.DirectPersistenceStrategy)

    def test_direct_persistence_strategy(self):
        project_id = "5004ded1163d66114f000000"
        auth_token = "2e79c6ec1d0145be8891bf668599c79a"
        client = KeenClient(project_id, auth_token)
        client.add_event("python_test", {"hello": "goodbye"})
