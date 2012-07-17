import json
from keen import persistence_strategies

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
        self.project_id = project_id
        self.auth_token = auth_token
        if not persistence_strategy:
            persistence_strategy = persistence_strategies\
            .DirectPersistenceStrategy(project_id, auth_token)
        self.persistence_strategy = persistence_strategy

    def add_event(self, collection_name, event_body, timestamp=None):
        event = Event(self.project_id, collection_name, event_body,
                      timestamp=timestamp)
        self.persistence_strategy.persist(event)
