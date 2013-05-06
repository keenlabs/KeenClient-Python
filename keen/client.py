import copy
from keen import persistence_strategies, exceptions
from keen.api import KeenApi
from keen.persistence_strategies import BasePersistenceStrategy
# Try to load the faster json, for local dev and tests
try:
    import ujson as json
except:
    from django.utils import simplejson as json

__author__ = 'dkador'


class Event(object):
    """
    An event in Keen.
    """

    def __init__(self, project_id, collection_name, event_body,
                 timestamp=None):
        """ Initializes a new Event.

        :param project_id: the Keen project ID to insert the event to
        :param collection_name: the Keen collection name to insert the event to
        :param event_body: a dict that contains the body of the event to insert
        :param timestamp: optional, specify a datetime to override the
        timestamp associated with the event in Keen
        """
        super(Event, self).__init__()
        self.project_id = project_id
        self.collection_name = collection_name
        self.event_body = event_body
        self.timestamp = timestamp

    def to_json(self):
        """ Serializes the event to JSON.

        :returns: a string
        """
        event_as_dict = copy.deepcopy(self.event_body)
        if self.timestamp:
            event_as_dict["keen"] = {"timestamp": self.timestamp.isoformat()}
        return json.dumps(event_as_dict)


class KeenClient(object):
    """ The Keen Client is the main object to use to interface with Keen. It
    requires a project ID and one or both of write_key and read_key.

    Optionally, you can also specify a persistence strategy to elect how
    events are handled when they're added. The default strategy is to send
    the event directly to Keen, in-line. This may not always be the best
    idea, though, so we support other strategies (such as persisting
    to a local Redis queue for later processing).
    """

    def __init__(self, project_id, write_key=None, read_key=None,
                 persistence_strategy=None):
        """ Initializes a KeenClient object.

        :param project_id: the Keen IO project ID
        :param write_key: a Keen IO Scoped Key for Writes
        :param read_key: a Keen IO Scoped Key for Reads
        :param persistence_strategy: optional, the strategy to use to persist
        the event
        """
        super(KeenClient, self).__init__()

        # do some validation
        if not project_id or not isinstance(project_id, str):
            raise exceptions.InvalidProjectIdError(project_id)

        if persistence_strategy:
            # validate the given persistence strategy
            if not isinstance(persistence_strategy, BasePersistenceStrategy):
                raise exceptions.InvalidPersistenceStrategyError()
        if not persistence_strategy:
            # setup a default persistence strategy
            keen_api = KeenApi(project_id, write_key=write_key, read_key=read_key)
            persistence_strategy = persistence_strategies \
                .DirectPersistenceStrategy(keen_api)

        self.project_id = project_id
        self.persistence_strategy = persistence_strategy

    def add_event(self, collection_name, event_body, timestamp=None):
        """ Adds an event.

        Depending on the persistence strategy of the client,
        this will either result in the event being uploaded to Keen
        immediately or will result in saving the event to some local cache.

        :param collection_name: the name of the collection to insert the
        event to
        :param event_body: dict, the body of the event to insert the event to
        :param timestamp: datetime, optional, the timestamp of the event
        """
        event = Event(self.project_id, collection_name, event_body,
                      timestamp=timestamp)
        self.persistence_strategy.persist(event)
