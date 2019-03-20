import base64
import copy
import json
import sys
from keen import persistence_strategies, exceptions, saved_queries, cached_datasets
from keen.api import KeenApi
from keen.persistence_strategies import BasePersistenceStrategy

__author__ = 'dkador'


class Event(object):
    """
    An event in Keen.
    """

    def __init__(self, project_id, event_collection, event_body,
                 timestamp=None):
        """ Initializes a new Event.

        :param project_id: the Keen project ID to insert the event to
        :param event_collection: the Keen collection name to insert the event to
        :param event_body: a dict that contains the body of the event to insert
        :param timestamp: optional, specify a datetime to override the
        timestamp associated with the event in Keen
        """
        super(Event, self).__init__()
        self.project_id = project_id
        self.event_collection = event_collection
        self.event_body = event_body
        self.timestamp = timestamp

    def to_json(self):
        """ Serializes the event to JSON.

        :returns: a string
        """
        event_as_dict = copy.deepcopy(self.event_body)
        if self.timestamp:
            if "keen" in event_as_dict:
                event_as_dict["keen"]["timestamp"] = self.timestamp.isoformat()
            else:
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

    GET requests will timeout after 305 seconds by default.

    POST requests will timeout after 305 seconds by default.
    """

    def __init__(self, project_id, write_key=None, read_key=None,
                 persistence_strategy=None, api_class=KeenApi, get_timeout=305, post_timeout=305,
                 master_key=None, base_url=None):
        """ Initializes a KeenClient object.

        :param project_id: the Keen IO project ID
        :param write_key: a Keen IO Scoped Key for Writes
        :param read_key: a Keen IO Scoped Key for Reads
        :param persistence_strategy: optional, the strategy to use to persist
        the event
        :param get_timeout: optional, the timeout on GET requests
        :param post_timeout: optional, the timeout on POST requests
        :param master_key: a Keen IO Master API Key
        """
        super(KeenClient, self).__init__()

        # do some validation
        self.check_project_id(project_id)

        # Set up an api client to be used for querying and optionally passed
        # into a default persistence strategy.
        self.api = api_class(project_id, write_key=write_key, read_key=read_key,
                             get_timeout=get_timeout, post_timeout=post_timeout,
                             master_key=master_key, base_url=base_url)

        if persistence_strategy:
            # validate the given persistence strategy
            if not isinstance(persistence_strategy, BasePersistenceStrategy):
                raise exceptions.InvalidPersistenceStrategyError()
        if not persistence_strategy:
            # setup a default persistence strategy
            persistence_strategy = persistence_strategies \
                .DirectPersistenceStrategy(self.api)

        self.project_id = project_id
        self.persistence_strategy = persistence_strategy
        self.get_timeout = get_timeout
        self.post_timeout = post_timeout
        self.saved_queries = saved_queries.SavedQueriesInterface(self.api)
        self.cached_datasets = cached_datasets.CachedDatasetsInterface(self.api)

    if sys.version_info[0] < 3:
        @staticmethod
        def check_project_id(project_id):

            ''' Python 2.x-compatible string typecheck. '''

            if not project_id or not isinstance(project_id, basestring):
                raise exceptions.InvalidProjectIdError(project_id)
    else:
        @staticmethod
        def check_project_id(project_id):

            ''' Python 3.x-compatible string typecheck. '''

            if not project_id or not isinstance(project_id, str):
                raise exceptions.InvalidProjectIdError(project_id)

    def add_event(self, event_collection, event_body, timestamp=None):
        """ Adds an event.

        Depending on the persistence strategy of the client,
        this will either result in the event being uploaded to Keen
        immediately or will result in saving the event to some local cache.

        :param event_collection: the name of the collection to insert the
        event to
        :param event_body: dict, the body of the event to insert the event to
        :param timestamp: datetime, optional, the timestamp of the event
        """
        event = Event(self.project_id, event_collection, event_body,
                      timestamp=timestamp)
        self.persistence_strategy.persist(event)

    def add_events(self, events):
        """ Adds a batch of events.

        Depending on the persistence strategy of the client,
        this will either result in the event being uploaded to Keen
        immediately or will result in saving the event to some local cache.

        :param events: dictionary of events
        """
        return self.persistence_strategy.batch_persist(events)

    def generate_image_beacon(self, event_collection, event_body, timestamp=None):
        """ Generates an image beacon URL.

        :param event_collection: the name of the collection to insert the
        event to
        :param event_body: dict, the body of the event to insert the event to
        :param timestamp: datetime, optional, the timestamp of the event
        """
        event = Event(self.project_id, event_collection, event_body,
                      timestamp=timestamp)
        event_json = event.to_json()
        return "{0}/{1}/projects/{2}/events/{3}?api_key={4}&data={5}".format(
            self.api.base_url, self.api.api_version, self.project_id, self._url_escape(event_collection),
            self.api.write_key.decode(sys.getdefaultencoding()), self._base64_encode(event_json)
        )

    def delete_events(self, event_collection, timeframe=None, timezone=None, filters=None):
        """ Deletes events.

        :param event_collection: string, the event collection from which event are being deleted
        :param timeframe: string or dict, the timeframe in which the events happened
        example: "previous_7_days"
        :param timezone: int, the timezone you'd like to use for the timeframe
        and interval in seconds
        :param filters: array of dict, contains the filters you'd like to apply to the data
        example: [{"property_name":"device", "operator":"eq", "property_value":"iPhone"}]

        """
        params = self.get_params(timeframe=timeframe, timezone=timezone, filters=filters)
        return self.api.delete_events(event_collection, params)

    def get_collection(self, event_collection):
        """ Returns event collection schema

        :param event_collection: string, the event collection from which schema is to be returned,
        if left blank will return schema for all collections
        """

        return self.api.get_collection(event_collection)

    def get_all_collections(self):
        """ Returns event collection schema for all events

        """

        return self.api.get_all_collections()

    def create_access_key(self, name, is_active=True, permitted=[], options={}):
        """
        Creates a new access key. A master key must be set first.

        :param name: the name of the access key to create
        :param is_active: Boolean value dictating whether this key is currently active (default True)
        :param permitted: list of strings describing which operation types this key will permit
                          Legal values include "writes", "queries", "saved_queries", "cached_queries",
                          "datasets", and "schema".
        :param options: dictionary containing more details about the key's permitted and restricted
                        functionality
        """

        return self.api.create_access_key(name=name, is_active=is_active,
                                          permitted=permitted, options=options)

    def list_access_keys(self):
        """
        Returns a list of all access keys in this project. A master key must be set first.
        """
        return self.api.list_access_keys()

    def get_access_key(self, access_key_id):
        """
        Returns details on a particular access key. A master key must be set first.

        :param access_key_id: the 'key' value of the access key to retreive data from
        """
        return self.api.get_access_key(access_key_id)

    def update_access_key_name(self, access_key_id, name):
        """
        Updates only the name portion of an access key.

        :param access_key_id: the 'key' value of the access key to change the name of
        :param name: the new name to give this access key
        """
        return self.api.update_access_key_name(access_key_id, name)

    def add_access_key_permissions(self, access_key_id, permissions):
        """
        Adds to the existing list of permissions on this key with the contents of this list.
        Will not remove any existing permissions or modify the remainder of the key.

        :param access_key_id: the 'key' value of the access key to add permissions to
        :param permissions: the new permissions to add to the existing list of permissions
        """
        return self.api.add_access_key_permissions(access_key_id, permissions)

    def remove_access_key_permissions(self, access_key_id, permissions):
        """
        Removes a list of permissions from the existing list of permissions.
        Will not remove all existing permissions unless all such permissions are included
        in this list. Not to be confused with key revocation.

        See also: revoke_access_key()

        :param access_key_id: the 'key' value of the access key to remove some permissions from
        :param permissions: the permissions you wish to remove from this access key
        """
        return self.api.remove_access_key_permissions(access_key_id, permissions)

    def update_access_key_permissions(self, access_key_id, permissions):
        """
        Replaces all of the permissions on the access key but does not change
        non-permission properties such as the key's name.

        See also: add_access_key_permissions() and remove_access_key_permissions().

        :param access_key_id: the 'key' value of the access key to change the permissions of
        :param permissions: the new list of permissions for this key
        """
        return self.api.update_access_key_permissions(access_key_id, permissions)

    def update_access_key_options(self, access_key_id, options):
        """
        Replaces all of the options on the access key but does not change
        non-option properties such as permissions or the key's name.

        :param access_key_id: the 'key' value of the access key to change the options of
        :param options: the new dictionary of options for this key
        """
        return self.api.update_access_key_options(access_key_id, options)

    def update_access_key_full(self, access_key_id, name, is_active, permitted, options):
        """
        Replaces the 'name', 'is_active', 'permitted', and 'options' values of a given key.
        A master key must be set first.

        :param access_key_id: the 'key' value of the access key for which the values will be replaced
        :param name: the new name desired for this access key
        :param is_active: whether the key should become enabled (True) or revoked (False)
        :param permitted: the new list of permissions desired for this access key
        :param options: the new dictionary of options for this access key
        """
        return self.api.update_access_key_full(access_key_id, name, is_active, permitted, options)

    def revoke_access_key(self, access_key_id):
        """
        Revokes an access key. "Bad dog! No biscuit!"

        :param access_key_id: the 'key' value of the access key to revoke
        """
        return self.api.revoke_access_key(access_key_id)

    def unrevoke_access_key(self, access_key_id):
        """
        Re-enables an access key.

        :param access_key_id: the 'key' value of the access key to re-enable (unrevoke)
        """
        return self.api.unrevoke_access_key(access_key_id)

    def _base64_encode(self, string_to_encode):
        """ Base64 encodes a string, with either Python 2 or 3.

        :param string_to_encode: the string to encode
        """
        try:
            # python 2
            return base64.b64encode(string_to_encode)
        except TypeError:
            # python 3
            encoding = sys.getdefaultencoding()
            base64_bytes = base64.b64encode(bytes(string_to_encode, encoding))
            return base64_bytes.decode(encoding)

    def _url_escape(self, url):
        try:
            import urllib
            return urllib.quote(url)
        except AttributeError:
            import urllib.parse
            return urllib.parse.quote(url)

    def count(self, event_collection, timeframe=None, timezone=None, interval=None,
              filters=None, group_by=None, order_by=None, max_age=None, limit=None):
        """ Performs a count query

        Counts the number of events that meet the given criteria.

        :param event_collection: string, the name of the collection to query
        :param timeframe: string or dict, the timeframe in which the events
        happened example: "previous_7_days"
        :param timezone: int, the timezone you'd like to use for the timeframe
        and interval in seconds
        :param interval: string, the time interval used for measuring data over
        time example: "daily"
        :param filters: array of dict, contains the filters you'd like to apply to the data
        example: [{"property_name":"device", "operator":"eq", "property_value":"iPhone"}]
        :param group_by: string or array of strings, the name(s) of the properties you would
        like to group your results by.  example: "customer.id" or ["browser","operating_system"]
        :param order_by: dictionary or list of dictionary objects containing the property_name(s)
        to order by and the desired direction(s) of sorting.
        Example: {"property_name":"result", "direction":keen.direction.DESCENDING}
        May not be used without a group_by specified.
        :param limit: positive integer limiting the displayed results of a query using order_by
        :param max_age: an integer, greater than 30 seconds, the maximum 'staleness' you're
        willing to trade for increased query performance, in seconds

        """
        params = self.get_params(event_collection=event_collection, timeframe=timeframe, timezone=timezone,
                                 interval=interval, filters=filters, group_by=group_by, order_by=order_by,
                                 max_age=max_age, limit=limit)
        return self.api.query("count", params)

    def sum(self, event_collection, target_property, timeframe=None, timezone=None, interval=None, filters=None,
            group_by=None, order_by=None, max_age=None, limit=None):
        """ Performs a sum query

        Adds the values of a target property for events that meet the given criteria.

        :param event_collection: string, the name of the collection to query
        :param target_property: string, the name of the event property you would like use
        :param timeframe: string or dict, the timeframe in which the events
        happened example: "previous_7_days"
        :param timezone: int, the timezone you'd like to use for the timeframe
        and interval in seconds
        :param interval: string, the time interval used for measuring data over
        time example: "daily"
        :param filters: array of dict, contains the filters you'd like to apply to the data
        example: [{"property_name":"device", "operator":"eq", "property_value":"iPhone"}]
        :param group_by: string or array of strings, the name(s) of the properties you would
        like to group your results by.  example: "customer.id" or ["browser","operating_system"]
        :param order_by: dictionary or list of dictionary objects containing the property_name(s)
        to order by and the desired direction(s) of sorting.
        Example: {"property_name":"result", "direction":keen.direction.DESCENDING}
        May not be used without a group_by specified.
        :param limit: positive integer limiting the displayed results of a query using order_by
        :param max_age: an integer, greater than 30 seconds, the maximum 'staleness' you're
        willing to trade for increased query performance, in seconds

        """
        params = self.get_params(event_collection=event_collection, timeframe=timeframe, timezone=timezone,
                                 interval=interval, filters=filters, group_by=group_by, order_by=order_by,
                                 target_property=target_property, max_age=max_age, limit=limit)
        return self.api.query("sum", params)

    def minimum(self, event_collection, target_property, timeframe=None, timezone=None, interval=None,
                filters=None, group_by=None, order_by=None, max_age=None, limit=None):
        """ Performs a minimum query

        Finds the minimum value of a target property for events that meet the given criteria.

        :param event_collection: string, the name of the collection to query
        :param target_property: string, the name of the event property you would like use
        :param timeframe: string or dict, the timeframe in which the events
        happened example: "previous_7_days"
        :param timezone: int, the timezone you'd like to use for the timeframe
        and interval in seconds
        :param interval: string, the time interval used for measuring data over
        time example: "daily"
        :param filters: array of dict, contains the filters you'd like to apply to the data
        example: [{"property_name":"device", "operator":"eq", "property_value":"iPhone"}]
        :param group_by: string or array of strings, the name(s) of the properties you would
        like to group your results by.  example: "customer.id" or ["browser","operating_system"]
        :param order_by: dictionary or list of dictionary objects containing the property_name(s)
        to order by and the desired direction(s) of sorting.
        Example: {"property_name":"result", "direction":keen.direction.DESCENDING}
        May not be used without a group_by specified.
        :param limit: positive integer limiting the displayed results of a query using order_by
        :param max_age: an integer, greater than 30 seconds, the maximum 'staleness' you're
        willing to trade for increased query performance, in seconds

        """
        params = self.get_params(event_collection=event_collection, timeframe=timeframe, timezone=timezone,
                                 interval=interval, filters=filters, group_by=group_by,
                                 target_property=target_property, max_age=max_age, limit=limit)
        return self.api.query("minimum", params)

    def maximum(self, event_collection, target_property, timeframe=None, timezone=None, interval=None,
                filters=None, group_by=None, order_by=None, max_age=None, limit=None):
        """ Performs a maximum query

        Finds the maximum value of a target property for events that meet the given criteria.

        :param event_collection: string, the name of the collection to query
        :param target_property: string, the name of the event property you would like use
        :param timeframe: string or dict, the timeframe in which the events
        happened example: "previous_7_days"
        :param timezone: int, the timezone you'd like to use for the timeframe
        and interval in seconds
        :param interval: string, the time interval used for measuring data over
        time example: "daily"
        :param filters: array of dict, contains the filters you'd like to apply to the data
        example: [{"property_name":"device", "operator":"eq", "property_value":"iPhone"}]
        :param group_by: string or array of strings, the name(s) of the properties you would
        like to group your results by.  example: "customer.id" or ["browser","operating_system"]
        :param order_by: dictionary or list of dictionary objects containing the property_name(s)
        to order by and the desired direction(s) of sorting.
        Example: {"property_name":"result", "direction":keen.direction.DESCENDING}
        May not be used without a group_by specified.
        :param limit: positive integer limiting the displayed results of a query using order_by
        :param max_age: an integer, greater than 30 seconds, the maximum 'staleness' you're
        willing to trade for increased query performance, in seconds

        """
        params = self.get_params(event_collection=event_collection, timeframe=timeframe, timezone=timezone,
                                 interval=interval, filters=filters, group_by=group_by, order_by=order_by,
                                 target_property=target_property, max_age=max_age, limit=limit)
        return self.api.query("maximum", params)

    def average(self, event_collection, target_property, timeframe=None, timezone=None, interval=None,
                filters=None, group_by=None, order_by=None, max_age=None, limit=None):
        """ Performs a average query

        Finds the average of a target property for events that meet the given criteria.

        :param event_collection: string, the name of the collection to query
        :param target_property: string, the name of the event property you would like use
        :param timeframe: string or dict, the timeframe in which the events
        happened example: "previous_7_days"
        :param timezone: int, the timezone you'd like to use for the timeframe
        and interval in seconds
        :param interval: string, the time interval used for measuring data over
        time example: "daily"
        :param filters: array of dict, contains the filters you'd like to apply to the data
        example: [{"property_name":"device", "operator":"eq", "property_value":"iPhone"}]
        :param group_by: string or array of strings, the name(s) of the properties you would
        like to group your results by.  example: "customer.id" or ["browser","operating_system"]
        :param order_by: dictionary or list of dictionary objects containing the property_name(s)
        to order by and the desired direction(s) of sorting.
        Example: {"property_name":"result", "direction":keen.direction.DESCENDING}
        May not be used without a group_by specified.
        :param limit: positive integer limiting the displayed results of a query using order_by
        :param max_age: an integer, greater than 30 seconds, the maximum 'staleness' you're
        willing to trade for increased query performance, in seconds

        """
        params = self.get_params(event_collection=event_collection, timeframe=timeframe, timezone=timezone,
                                 interval=interval, filters=filters, group_by=group_by, order_by=order_by,
                                 target_property=target_property, max_age=max_age, limit=limit)
        return self.api.query("average", params)

    def median(self, event_collection, target_property, timeframe=None, timezone=None, interval=None,
                filters=None, group_by=None, order_by=None, max_age=None, limit=None):
        """ Performs a median query

        Finds the median of a target property for events that meet the given criteria.

        :param event_collection: string, the name of the collection to query
        :param target_property: string, the name of the event property you would like use
        :param timeframe: string or dict, the timeframe in which the events
        happened example: "previous_7_days"
        :param timezone: int, the timezone you'd like to use for the timeframe
        and interval in seconds
        :param interval: string, the time interval used for measuring data over
        time example: "daily"
        :param filters: array of dict, contains the filters you'd like to apply to the data
        example: [{"property_name":"device", "operator":"eq", "property_value":"iPhone"}]
        :param group_by: string or array of strings, the name(s) of the properties you would
        like to group your results by.  example: "customer.id" or ["browser","operating_system"]
        :param order_by: dictionary or list of dictionary objects containing the property_name(s)
        to order by and the desired direction(s) of sorting.
        Example: {"property_name":"result", "direction":keen.direction.DESCENDING}
        May not be used without a group_by specified.
        :param limit: positive integer limiting the displayed results of a query using order_by
        :param max_age: an integer, greater than 30 seconds, the maximum 'staleness' you're
        willing to trade for increased query performance, in seconds

        """
        params = self.get_params(event_collection=event_collection, timeframe=timeframe, timezone=timezone,
                                 interval=interval, filters=filters, group_by=group_by, order_by=order_by,
                                 target_property=target_property, max_age=max_age, limit=limit)
        return self.api.query("median", params)

    def percentile(self, event_collection, target_property, percentile, timeframe=None, timezone=None,
                   interval=None, filters=None, group_by=None, order_by=None, max_age=None, limit=None):
        """ Performs a percentile query

        Finds the percentile of a target property for events that meet the given criteria.

        :param event_collection: string, the name of the collection to query
        :param target_property: string, the name of the event property you would like use
        :param percentile: float, the specific percentile you wish to calculate,
        supporting 0-100 with two decimal places of precision for example, 99.99
        :param timeframe: string or dict, the timeframe in which the events
        happened example: "previous_7_days"
        :param timezone: int, the timezone you'd like to use for the timeframe
        and interval in seconds
        :param interval: string, the time interval used for measuring data over
        time example: "daily"
        :param filters: array of dict, contains the filters you'd like to apply to the data
        example: [{"property_name":"device", "operator":"eq", "property_value":"iPhone"}]
        :param group_by: string or array of strings, the name(s) of the properties you would
        like to group your results by.  example: "customer.id" or ["browser","operating_system"]
        :param order_by: dictionary or list of dictionary objects containing the property_name(s)
        to order by and the desired direction(s) of sorting.
        Example: {"property_name":"result", "direction":keen.direction.DESCENDING}
        May not be used without a group_by specified.
        :param limit: positive integer limiting the displayed results of a query using order_by
        :param max_age: an integer, greater than 30 seconds, the maximum 'staleness' you're
        willing to trade for increased query performance, in seconds

        """
        params = self.get_params(
            event_collection=event_collection,
            timeframe=timeframe,
            percentile=percentile,
            timezone=timezone,
            interval=interval,
            filters=filters,
            group_by=group_by,
            order_by=order_by,
            target_property=target_property,
            max_age=max_age,
            limit=limit
        )
        return self.api.query("percentile", params)

    def count_unique(self, event_collection, target_property, timeframe=None, timezone=None, interval=None,
                     filters=None, group_by=None, order_by=None, max_age=None, limit=None):
        """ Performs a count unique query

        Counts the unique values of a target property for events that meet the given criteria.

        :param event_collection: string, the name of the collection to query
        :param target_property: string, the name of the event property you would like use
        :param timeframe: string or dict, the timeframe in which the events
        happened example: "previous_7_days"
        :param timezone: int, the timezone you'd like to use for the timeframe
        and interval in seconds
        :param interval: string, the time interval used for measuring data over
        time example: "daily"
        :param filters: array of dict, contains the filters you'd like to apply to the data
        example: [{"property_name":"device", "operator":"eq", "property_value":"iPhone"}]
        :param group_by: string or array of strings, the name(s) of the properties you would
        like to group your results by.  example: "customer.id" or ["browser","operating_system"]
        :param order_by: dictionary or list of dictionary objects containing the property_name(s)
        to order by and the desired direction(s) of sorting.
        Example: {"property_name":"result", "direction":keen.direction.DESCENDING}
        May not be used without a group_by specified.
        :param limit: positive integer limiting the displayed results of a query using order_by
        :param max_age: an integer, greater than 30 seconds, the maximum 'staleness' you're
        willing to trade for increased query performance, in seconds

        """
        params = self.get_params(event_collection=event_collection, timeframe=timeframe, timezone=timezone,
                                 interval=interval, filters=filters, group_by=group_by, order_by=order_by,
                                 target_property=target_property, max_age=max_age, limit=limit)
        return self.api.query("count_unique", params)

    def select_unique(self, event_collection, target_property, timeframe=None, timezone=None, interval=None,
                      filters=None, group_by=None, order_by=None, max_age=None, limit=None):
        """ Performs a select unique query

        Returns an array of the unique values of a target property for events that meet the given criteria.

        :param event_collection: string, the name of the collection to query
        :param target_property: string, the name of the event property you would like use
        :param timeframe: string or dict, the timeframe in which the events
        happened example: "previous_7_days"
        :param timezone: int, the timezone you'd like to use for the timeframe
        and interval in seconds
        :param interval: string, the time interval used for measuring data over
        time example: "daily"
        :param filters: array of dict, contains the filters you'd like to apply to the data
        example: [{"property_name":"device", "operator":"eq", "property_value":"iPhone"}]
        :param group_by: string or array of strings, the name(s) of the properties you would
        like to group your results by.  example: "customer.id" or ["browser","operating_system"]
        :param order_by: dictionary or list of dictionary objects containing the property_name(s)
        to order by and the desired direction(s) of sorting.
        Example: {"property_name":"result", "direction":keen.direction.DESCENDING}
        May not be used without a group_by specified.
        :param limit: positive integer limiting the displayed results of a query using order_by
        :param max_age: an integer, greater than 30 seconds, the maximum 'staleness' you're
        willing to trade for increased query performance, in seconds

        """
        params = self.get_params(event_collection=event_collection, timeframe=timeframe, timezone=timezone,
                                 interval=interval, filters=filters, group_by=group_by, order_by=order_by,
                                 target_property=target_property, max_age=max_age, limit=limit)
        return self.api.query("select_unique", params)

    def extraction(self, event_collection, timeframe=None, timezone=None, filters=None, latest=None,
                   email=None, property_names=None):
        """ Performs a data extraction

        Returns either a JSON object of events or a response
         indicating an email will be sent to you with data.

        :param event_collection: string, the name of the collection to query
        :param timeframe: string or dict, the timeframe in which the events
        happened example: "previous_7_days"
        :param timezone: int, the timezone you'd like to use for the timeframe
        and interval in seconds
        :param filters: array of dict, contains the filters you'd like to apply to the data
        example: [{"property_name":"device", "operator":"eq", "property_value":"iPhone"}]
        :param latest: int, the number of most recent records you'd like to return
        :param email: string, optional string containing an email address to email results to
        :param property_names: string or list of strings, used to limit the properties returned

        """
        params = self.get_params(event_collection=event_collection, timeframe=timeframe, timezone=timezone,
                                 filters=filters, latest=latest, email=email, property_names=property_names)
        return self.api.query("extraction", params)

    def funnel(self, steps, timeframe=None, timezone=None, max_age=None, all_keys=False):
        """ Performs a Funnel query

        Returns an object containing the results for each step of the funnel.

        :param steps: array of dictionaries, one for each step. example:
        [{"event_collection":"signup","actor_property":"user.id"},
        {"event_collection":"purchase","actor_property:"user.id"}]
        :param timeframe: string or dict, the timeframe in which the events
        happened example: "previous_7_days"
        :param timezone: int, the timezone you'd like to use for the timeframe
        and interval in seconds
        :param max_age: an integer, greater than 30 seconds, the maximum 'staleness' you're
        willing to trade for increased query performance, in seconds
        :all_keys: set to true to return all keys on response (i.e. "result", "actors", "steps")

        """
        params = self.get_params(
            steps=steps,
            timeframe=timeframe,
            timezone=timezone,
            max_age=max_age,
        )

        return self.api.query("funnel", params, all_keys=all_keys)

    def multi_analysis(self, event_collection, analyses, timeframe=None, interval=None, timezone=None, filters=None,
                       group_by=None, order_by=None, max_age=None, limit=None):
        """ Performs a multi-analysis query

        Returns a dictionary of analysis results.

        :param event_collection: string, the name of the collection to query
        :param analyses: dict, the types of analyses you'd like to run.  example:
        {"total money made":{"analysis_type":"sum","target_property":"purchase.price",
        "average price":{"analysis_type":"average","target_property":"purchase.price"}
        :param timeframe: string or dict, the timeframe in which the events
        happened example: "previous_7_days"
        :param interval: string, the time interval used for measuring data over
        time example: "daily"
        :param timezone: int, the timezone you'd like to use for the timeframe
        and interval in seconds
        :param filters: array of dict, contains the filters you'd like to apply to the data
        example: [{"property_name":"device", "operator":"eq", "property_value":"iPhone"}]
        :param group_by: string or array of strings, the name(s) of the properties you would
        like to group your results by.  example: "customer.id" or ["browser","operating_system"]
        :param order_by: dictionary or list of dictionary objects containing the property_name(s)
        to order by and the desired direction(s) of sorting.
        Example: {"property_name":"result", "direction":keen.direction.DESCENDING}
        May not be used without a group_by specified.
        :param limit: positive integer limiting the displayed results of a query using order_by
        :param max_age: an integer, greater than 30 seconds, the maximum 'staleness' you're
        willing to trade for increased query performance, in seconds

        """
        params = self.get_params(
            event_collection=event_collection,
            timeframe=timeframe,
            interval=interval,
            timezone=timezone,
            filters=filters,
            group_by=group_by,
            order_by=order_by,
            analyses=analyses,
            max_age=max_age,
            limit=limit
        )

        return self.api.query("multi_analysis", params)

    def get_params(self, event_collection=None, timeframe=None, timezone=None, interval=None, filters=None,
                   group_by=None, order_by=None, target_property=None, latest=None, email=None, analyses=None,
                   steps=None, property_names=None, percentile=None, max_age=None, limit=None):
        params = {}
        if event_collection:
            params["event_collection"] = event_collection
        if timeframe:
            if type(timeframe) is dict:
                params["timeframe"] = json.dumps(timeframe)
            else:
                params["timeframe"] = timeframe
        if timezone:
            params["timezone"] = timezone
        if interval:
            params["interval"] = interval
        if filters:
            params["filters"] = json.dumps(filters)
        if group_by:
            if type(group_by) is list:
                params["group_by"] = json.dumps(group_by)
            else:
                params["group_by"] = group_by
        if order_by:
            if isinstance(order_by, list):
                params["order_by"] = json.dumps(order_by)
            else:
                params["order_by"] = json.dumps([order_by])
        if limit:
            params["limit"] = limit
        if target_property:
            params["target_property"] = target_property
        if latest:
            params["latest"] = latest
        if email:
            params["email"] = email
        if analyses:
            params["analyses"] = json.dumps(analyses)
        if steps:
            params["steps"] = json.dumps(steps)
        if property_names:
            params["property_names"] = json.dumps(property_names)
        if percentile:
            params["percentile"] = percentile
        if max_age:
            params["max_age"] = max_age

        return params
