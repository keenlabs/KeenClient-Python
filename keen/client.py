import json
from keen import persistence_strategies, exceptions
from keen.api import KeenApi
from keen.persistence_strategies import BasePersistenceStrategy

__author__ = 'dkador'

class Event(object):
    """
    An event in Keen.
    """

    def __init__(self, project_id, collection_name, event_body,
                 timestamp=None):
        super(Event, self).__init__()
        self.project_id = project_id
        self.collection_name = collection_name
        self.event_body = event_body
        self.timestamp = timestamp

    def to_json(self):
        event_as_dict = {
            "body": self.event_body
        }
        if self.timestamp:
            event_as_dict["header"] = {"timestamp": self.timestamp.isoformat()}
        return json.dumps(event_as_dict)


class KeenClient(object):
    def __init__(self, project_id, auth_token, persistence_strategy=None):
        super(KeenClient, self).__init__()

        # do some validation
        if not project_id or not isinstance(project_id, basestring):
            raise exceptions.InvalidProjectIdError(project_id)
        if not auth_token or not isinstance(auth_token, basestring):
            raise exceptions.InvalidAuthTokenError(auth_token)

        if persistence_strategy:
            if not isinstance(persistence_strategy, BasePersistenceStrategy):
                raise exceptions.InvalidPersistenceStrategyError()
        if not persistence_strategy:
            keen_api = KeenApi(project_id, auth_token)
            persistence_strategy = persistence_strategies\
            .DirectPersistenceStrategy(keen_api)

        self.project_id = project_id
        self.auth_token = auth_token
        self.persistence_strategy = persistence_strategy

    def add_event(self, collection_name, event_body, timestamp=None):
        event = Event(self.project_id, collection_name, event_body,
                      timestamp=timestamp)
        self.persistence_strategy.persist(event)
