__author__ = 'dkador'

class BasePersistenceStrategy(object):
    """
    A persistence strategy is responsible for persisting a given event
    somewhere (i.e. directly to Keen, a local cache, a Redis queue, etc.)
    """

    def persist(self):
        raise NotImplementedError()


class DirectPersistenceStrategy(BasePersistenceStrategy):
    """
    A persistence strategy that saves directly to Keen and bypasses any local
    cache.
    """

    def persist(self):
        pass


class RedisPersistenceStrategy(BasePersistenceStrategy):
    pass


class FilePersistenceStrategy(BasePersistenceStrategy):
    pass
