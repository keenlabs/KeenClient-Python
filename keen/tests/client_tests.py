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
        client = KeenClient(project_id, write_key=write_key)
        client.add_event("python_test", {"hello": "goodbye"})