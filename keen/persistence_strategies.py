import requests
from keen import exceptions

__author__ = 'dkador'

class BasePersistenceStrategy(object):
    """
    A persistence strategy is responsible for persisting a given event
    somewhere (i.e. directly to Keen, a local cache, a Redis queue, etc.)
    """

    def persist(self, event):
        """Persists the given event somewhere.

        :param event: the event to persist
        """
        raise NotImplementedError()


class DirectPersistenceStrategy(BasePersistenceStrategy):
    """
    A persistence strategy that saves directly to Keen and bypasses any local
    cache.
    """

    base_url = "https://api.keen.io"
    api_version = "2.0"

    def __init__(self, project_id, auth_token, base_url=None,
                 api_version=None):
        """ Initializer for DirectPersistenceStrategy.

        :param project_id: the Keen project id
        :param auth_token: the Keen authorization token
        :param base_url: the base_url of the Keen API
        :param api_version: the version of the Keen API to use

        """
        super(DirectPersistenceStrategy, self).__init__()
        self.project_id = project_id
        self.auth_token = auth_token
        if base_url:
            self.base_url = base_url
        if api_version:
            self.api_version = api_version

    def persist(self, event):
        url = "{}/{}/projects/{}/{}".format(self.base_url, self.api_version,
                                            self.project_id,
                                            event.collection_name)
        headers = {"Authorization": self.auth_token,
                   "Content-Type": "application/json"}
        payload = event.to_json()
        response = requests.post(url, data=payload, headers=headers)
        if response.status_code != 201:
            error = response.json
            raise exceptions.KeenApiError(error)


class RedisPersistenceStrategy(BasePersistenceStrategy):
    pass


class FilePersistenceStrategy(BasePersistenceStrategy):
    pass
