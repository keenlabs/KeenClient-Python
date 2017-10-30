import os
from keen.client import KeenClient
from keen.exceptions import InvalidEnvironmentError

__author__ = 'dkador'

_client = None
project_id = None
write_key = None
read_key = None
master_key = None
base_url = None

def _initialize_client_from_environment():
    ''' Initialize a KeenClient instance using environment variables. '''
    global _client, project_id, write_key, read_key, master_key, base_url

    if _client is None:
        # check environment for project ID and keys
        project_id = project_id or os.environ.get("KEEN_PROJECT_ID")
        write_key = write_key or os.environ.get("KEEN_WRITE_KEY")
        read_key = read_key or os.environ.get("KEEN_READ_KEY")
        master_key = master_key or os.environ.get("KEEN_MASTER_KEY")
        base_url = base_url or os.environ.get("KEEN_BASE_URL")

        if not project_id:
            raise InvalidEnvironmentError("Please set the KEEN_PROJECT_ID environment variable or set keen.project_id!")

        _client = KeenClient(project_id,
                             write_key=write_key,
                             read_key=read_key,
                             master_key=master_key,
                             base_url=base_url)


def add_event(event_collection, body, timestamp=None):
    """ Adds an event.

    Depending on the persistence strategy of the client,
    this will either result in the event being uploaded to Keen
    immediately or will result in saving the event to some local cache.

    :param event_collection: the name of the collection to insert the
    event to
    :param body: dict, the body of the event to insert the event to
    :param timestamp: datetime, optional, the timestamp of the event
    """
    _initialize_client_from_environment()
    _client.add_event(event_collection, body, timestamp=timestamp)


def add_events(events):
    """ Adds a batch of events.

    Depending on the persistence strategy of the client,
    this will either result in the event being uploaded to Keen
    immediately or will result in saving the event to some local cache.

    :param events: dictionary of events
    """
    _initialize_client_from_environment()
    return _client.add_events(events)


def generate_image_beacon(event_collection, body, timestamp=None):
    """ Generates an image beacon URL.

    :param event_collection: the name of the collection to insert the
    event to
    :param body: dict, the body of the event to insert the event to
    :param timestamp: datetime, optional, the timestamp of the event
    """
    _initialize_client_from_environment()
    return _client.generate_image_beacon(event_collection, body, timestamp=timestamp)


def count(event_collection, timeframe=None, timezone=None, interval=None, filters=None, group_by=None, order_by=None,
          max_age=None, limit=None):
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
    like to group you results by.  example: "customer.id" or ["browser","operating_system"]
    :param order_by: dictionary or list of dictionary objects containing the property_name(s)
    to order by and the desired direction(s) of sorting.
    Example: {"property_name":"result", "direction":keen.direction.DESCENDING}
    May not be used without a group_by specified.
    :param limit: positive integer limiting the displayed results of a query using order_by
    :param max_age: an integer, greater than 30 seconds, the maximum 'staleness' you're
    willing to trade for increased query performance, in seconds

    """
    _initialize_client_from_environment()
    return _client.count(event_collection=event_collection, timeframe=timeframe, timezone=timezone,
                         interval=interval, filters=filters, group_by=group_by, order_by=order_by,
                         max_age=max_age, limit=limit)


def sum(event_collection, target_property, timeframe=None, timezone=None, interval=None, filters=None,
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
    like to group you results by.  example: "customer.id" or ["browser","operating_system"]
    :param order_by: dictionary or list of dictionary objects containing the property_name(s)
    to order by and the desired direction(s) of sorting.
    Example: {"property_name":"result", "direction":keen.direction.DESCENDING}
    May not be used without a group_by specified.
    :param limit: positive integer limiting the displayed results of a query using order_by
    :param max_age: an integer, greater than 30 seconds, the maximum 'staleness' you're
    willing to trade for increased query performance, in seconds

    """
    _initialize_client_from_environment()
    return _client.sum(event_collection=event_collection, timeframe=timeframe, timezone=timezone,
                       interval=interval, filters=filters, group_by=group_by, order_by=order_by,
                       target_property=target_property, max_age=max_age, limit=limit)


def minimum(event_collection, target_property, timeframe=None, timezone=None, interval=None, filters=None,
            group_by=None, order_by=None, max_age=None, limit=None):
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
    like to group you results by.  example: "customer.id" or ["browser","operating_system"]
    :param order_by: dictionary or list of dictionary objects containing the property_name(s)
    to order by and the desired direction(s) of sorting.
    Example: {"property_name":"result", "direction":keen.direction.DESCENDING}
    May not be used without a group_by specified.
    :param limit: positive integer limiting the displayed results of a query using order_by
    :param max_age: an integer, greater than 30 seconds, the maximum 'staleness' you're
    willing to trade for increased query performance, in seconds

    """
    _initialize_client_from_environment()
    return _client.minimum(event_collection=event_collection, timeframe=timeframe, timezone=timezone,
                           interval=interval, filters=filters, group_by=group_by, order_by=order_by,
                           target_property=target_property, max_age=max_age, limit=limit)


def maximum(event_collection, target_property, timeframe=None, timezone=None, interval=None, filters=None,
            group_by=None, order_by=None, max_age=None, limit=None):
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
    like to group you results by.  example: "customer.id" or ["browser","operating_system"]
    :param order_by: dictionary or list of dictionary objects containing the property_name(s)
    to order by and the desired direction(s) of sorting.
    Example: {"property_name":"result", "direction":keen.direction.DESCENDING}
    May not be used without a group_by specified.
    :param limit: positive integer limiting the displayed results of a query using order_by
    :param max_age: an integer, greater than 30 seconds, the maximum 'staleness' you're
    willing to trade for increased query performance, in seconds

    """
    _initialize_client_from_environment()
    return _client.maximum(event_collection=event_collection, timeframe=timeframe, timezone=timezone,
                           interval=interval, filters=filters, group_by=group_by, order_by=order_by,
                           target_property=target_property, max_age=max_age, limit=limit)


def average(event_collection, target_property, timeframe=None, timezone=None, interval=None, filters=None,
            group_by=None, order_by=None, max_age=None, limit=None):
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
    like to group you results by.  example: "customer.id" or ["browser","operating_system"]
    :param order_by: dictionary or list of dictionary objects containing the property_name(s)
    to order by and the desired direction(s) of sorting.
    Example: {"property_name":"result", "direction":keen.direction.DESCENDING}
    May not be used without a group_by specified.
    :param limit: positive integer limiting the displayed results of a query using order_by
    :param max_age: an integer, greater than 30 seconds, the maximum 'staleness' you're
    willing to trade for increased query performance, in seconds

    """
    _initialize_client_from_environment()
    return _client.average(event_collection=event_collection, timeframe=timeframe, timezone=timezone,
                           interval=interval, filters=filters, group_by=group_by, order_by=order_by,
                           target_property=target_property, max_age=max_age, limit=limit)


def median(event_collection, target_property, timeframe=None, timezone=None, interval=None, filters=None,
           group_by=None, order_by=None, max_age=None, limit=None):
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
    like to group you results by.  example: "customer.id" or ["browser","operating_system"]
    :param order_by: dictionary or list of dictionary objects containing the property_name(s)
    to order by and the desired direction(s) of sorting.
    Example: {"property_name":"result", "direction":keen.direction.DESCENDING}
    May not be used without a group_by specified.
    :param limit: positive integer limiting the displayed results of a query using order_by
    :param max_age: an integer, greater than 30 seconds, the maximum 'staleness' you're
    willing to trade for increased query performance, in seconds

    """
    _initialize_client_from_environment()
    return _client.median(event_collection=event_collection, timeframe=timeframe, timezone=timezone,
                          interval=interval, filters=filters, group_by=group_by, order_by=order_by,
                          target_property=target_property, max_age=max_age)


def percentile(event_collection, target_property, percentile, timeframe=None, timezone=None, interval=None,
               filters=None, group_by=None, order_by=None, max_age=None, limit=None):
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
    like to group you results by.  example: "customer.id" or ["browser","operating_system"]
    :param order_by: dictionary or list of dictionary objects containing the property_name(s)
    to order by and the desired direction(s) of sorting.
    Example: {"property_name":"result", "direction":keen.direction.DESCENDING}
    May not be used without a group_by specified.
    :param limit: positive integer limiting the displayed results of a query using order_by
    :param max_age: an integer, greater than 30 seconds, the maximum 'staleness' you're
    willing to trade for increased query performance, in seconds

    """
    _initialize_client_from_environment()
    return _client.percentile(
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


def count_unique(event_collection, target_property, timeframe=None, timezone=None, interval=None,
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
    like to group you results by.  example: "customer.id" or ["browser","operating_system"]
    :param order_by: dictionary or list of dictionary objects containing the property_name(s)
    to order by and the desired direction(s) of sorting.
    Example: {"property_name":"result", "direction":keen.direction.DESCENDING}
    May not be used without a group_by specified.
    :param limit: positive integer limiting the displayed results of a query using order_by
    :param max_age: an integer, greater than 30 seconds, the maximum 'staleness' you're
    willing to trade for increased query performance, in seconds

    """
    _initialize_client_from_environment()
    return _client.count_unique(event_collection=event_collection, timeframe=timeframe, timezone=timezone,
                                interval=interval, filters=filters, group_by=group_by, order_by=order_by,
                                target_property=target_property, max_age=max_age, limit=limit)


def select_unique(event_collection, target_property, timeframe=None, timezone=None, interval=None,
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
    like to group you results by.  example: "customer.id" or ["browser","operating_system"]
    :param order_by: dictionary or list of dictionary objects containing the property_name(s)
    to order by and the desired direction(s) of sorting.
    Example: {"property_name":"result", "direction":keen.direction.DESCENDING}
    May not be used without a group_by specified.
    :param limit: positive integer limiting the displayed results of a query using order_by
    :param max_age: an integer, greater than 30 seconds, the maximum 'staleness' you're
    willing to trade for increased query performance, in seconds

    """
    _initialize_client_from_environment()
    return _client.select_unique(event_collection=event_collection, timeframe=timeframe, timezone=timezone,
                                 interval=interval, filters=filters, group_by=group_by, order_by=order_by,
                                 target_property=target_property, max_age=max_age, limit=limit)


def extraction(event_collection, timeframe=None, timezone=None, filters=None, latest=None, email=None,
               property_names=None):
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
    _initialize_client_from_environment()
    return _client.extraction(event_collection=event_collection, timeframe=timeframe, timezone=timezone,
                              filters=filters, latest=latest, email=email, property_names=property_names)


def funnel(*args, **kwargs):
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

    """
    _initialize_client_from_environment()
    return _client.funnel(*args, **kwargs)


def multi_analysis(event_collection, analyses, timeframe=None, interval=None, timezone=None,
                   filters=None, group_by=None, order_by=None, max_age=None, limit=None):
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
    like to group you results by.  example: "customer.id" or ["browser","operating_system"]
    :param order_by: dictionary or list of dictionary objects containing the property_name(s)
    to order by and the desired direction(s) of sorting.
    Example: {"property_name":"result", "direction":keen.direction.DESCENDING}
    May not be used without a group_by specified.
    :param limit: positive integer limiting the displayed results of a query using order_by
    :param max_age: an integer, greater than 30 seconds, the maximum 'staleness' you're
    willing to trade for increased query performance, in seconds

    """
    _initialize_client_from_environment()
    return _client.multi_analysis(event_collection=event_collection, timeframe=timeframe,
                                  interval=interval, timezone=timezone, filters=filters,
                                  group_by=group_by, order_by=order_by, analyses=analyses,
                                  max_age=max_age, limit=limit)


def delete_events(*args, **kwargs):
    """ Performs a delete for events.

    Returns true upon success.

    :param event_collection: string, the event collection from which event are being deleted
    :param timeframe: string or dict, the timeframe in which the events
    happened example: "previous_7_days"
    :param timezone: int, the timezone you'd like to use for the timeframe
    and interval in seconds
    :param filters: array of dict, contains the filters you'd like to apply to the data
    example: [{"property_name":"device", "operator":"eq", "property_value":"iPhone"}]

    """
    _initialize_client_from_environment()
    return _client.delete_events(*args, **kwargs)


def get_collection(*args, **kwargs):
    """ Returns event collection schema

    :param event_collection: string, the event collection from which schema is to be returned,
    if left blank will return schema for all collections
    """
    _initialize_client_from_environment()
    return _client.get_collection(*args, **kwargs)


def get_all_collections():
    """ Returns event collection schema for all events

    """
    _initialize_client_from_environment()
    return _client.get_all_collections()

def create_access_key(name, is_active=True, permitted=[], options={}):
    """ Creates a new access key. A master key must be set first.

    :param name: the name of the access key to create
    :param is_active: Boolean value dictating whether this key is currently active (default True)
    :param permitted: list of strings describing which operation types this key will permit
                      Legal values include "writes", "queries", "saved_queries", "cached_queries",
                      "datasets", and "schema".
    :param options: dictionary containing more details about the key's permitted and restricted
                    functionality
    """
    _initialize_client_from_environment()
    return _client.create_access_key(name=name, is_active=is_active,
                                     permitted=permitted, options=options)

def list_access_keys():
    """
    Returns a list of all access keys in this project. A master key must be set first.
    """
    _initialize_client_from_environment()
    return _client.list_access_keys()

def get_access_key(access_key_id):
    """
    Returns details on a particular access key. A master key must be set first.

    :param access_key_id: the 'key' value of the access key to retreive data from
    """
    _initialize_client_from_environment()
    return _client.get_access_key(access_key_id)

def update_access_key_name(access_key_id, name):
    """
    Updates only the name portion of an access key.

    :param access_key_id: the 'key' value of the access key to change the name of
    :param name: the new name to give this access key
    """
    _initialize_client_from_environment()
    return _client.update_access_key_name(access_key_id, name)

def add_access_key_permissions(access_key_id, permissions):
    """
    Adds to the existing list of permissions on this key with the contents of this list.
    Will not remove any existing permissions or modify the remainder of the key.

    :param access_key_id: the 'key' value of the access key to add permissions to
    :param permissions: the new permissions to add to the existing list of permissions
    """
    _initialize_client_from_environment()
    return _client.add_access_key_permissions(access_key_id, permissions)

def remove_access_key_permissions(access_key_id, permissions):
    """
    Removes a list of permissions from the existing list of permissions.
    Will not remove all existing permissions unless all such permissions are included
    in this list. Not to be confused with key revocation.

    See also: revoke_access_key()

    :param access_key_id: the 'key' value of the access key to remove some permissions from
    :param permissions: the permissions you wish to remove from this access key
    """
    _initialize_client_from_environment()
    return _client.remove_access_key_permissions(access_key_id, permissions)

def update_access_key_permissions(access_key_id, permissions):
    """
    Replaces all of the permissions on the access key but does not change
    non-permission properties such as the key's name.

    See also: add_access_key_permissions() and remove_access_key_permissions().

    :param access_key_id: the 'key' value of the access key to change the permissions of
    :param permissions: the new list of permissions for this key
    """
    _initialize_client_from_environment()
    return _client.update_access_key_permissions(access_key_id, permissions)

def update_access_key_options(access_key_id, options):
    """
    Replaces all of the options on the access key but does not change
    non-option properties such as permissions or the key's name.

    :param access_key_id: the 'key' value of the access key to change the options of
    :param options: the new dictionary of options for this key
    """
    _initialize_client_from_environment()
    return _client.update_access_key_options(access_key_id, options)

def update_access_key_full(access_key_id, name, is_active, permitted, options):
    """
    Replaces the 'name', 'is_active', 'permitted', and 'options' values of a given key.
    A master key must be set first.

    :param access_key_id: the 'key' value of the access key for which the values will be replaced
    :param name: the new name desired for this access key
    :param is_active: whether the key should become enabled (True) or revoked (False)
    :param permitted: the new list of permissions desired for this access key
    :param options: the new dictionary of options for this access key
    """
    _initialize_client_from_environment()
    return _client.update_access_key_full(access_key_id, name, is_active, permitted, options)

def revoke_access_key(access_key_id):
    """
    Revokes an access key. "Bad dog! No biscuit!"

    :param access_key_id: the 'key' value of the access key to revoke
    """
    _initialize_client_from_environment()
    return _client.revoke_access_key(access_key_id)

def unrevoke_access_key(access_key_id):
    """
    Re-enables an access key.

    :param access_key_id: the 'key' value of the access key to re-enable (unrevoke)
    """
    _initialize_client_from_environment()
    return _client.unrevoke_access_key(access_key_id)
