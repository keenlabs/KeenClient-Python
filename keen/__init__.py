__author__ = 'dkador'

class PersistenceStrategy:
    """
    An enum that defines the persistence strategy used by the KeenClient.
    Currently supported: DIRECT, which means any time add_event is called the
    client will call out directly to Keen, or REDIS, which means add_event
    will simply add the event to a defined Redis instance which can be
    cleared later.
    """
    DIRECT = 0,
    REDIS = 1