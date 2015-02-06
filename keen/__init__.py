import os
from keen.client import KeenClient
from keen.exceptions import InvalidEnvironmentError

__author__ = 'dkador'

_client = None
project_id = None
write_key = None
read_key = None


def _initialize_client_from_environment():
    global _client, project_id, write_key, read_key

    if _client is None:
        # check environment for project ID and keys
        project_id = project_id or os.environ.get("KEEN_PROJECT_ID")
        write_key = write_key or os.environ.get("KEEN_WRITE_KEY")
        read_key = read_key or os.environ.get("KEEN_READ_KEY")

        if not project_id:
            raise InvalidEnvironmentError("Please set the KEEN_PROJECT_ID environment variable or set keen.project_id!")

        _client = KeenClient(project_id,
                             write_key=write_key,
                             read_key=read_key)


def add_event(event_collection, body, timestamp=None):
    _initialize_client_from_environment()
    _client.add_event(event_collection, body, timestamp=timestamp)


def add_events(events):
    _initialize_client_from_environment()
    _client.add_events(events)


def generate_image_beacon(event_collection, body, timestamp=None):
    _initialize_client_from_environment()
    return _client.generate_image_beacon(event_collection, body, timestamp=timestamp)


def count(event_collection, timeframe=None, timezone=None, interval=None, filters=None, group_by=None, max_age=None):
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
    example: {["property_name":"device", "operator":"eq", "property_value":"iPhone"}]
    :param group_by: string or array of strings, the name(s) of the properties you would
    like to group you results by.  example: "customer.id" or ["browser","operating_system"]
    :param max_age: an integer, greater than 30 seconds, the maximum 'staleness' you're
    willing to trade for increased query performance, in seconds

    """
    _initialize_client_from_environment()
    return _client.count(event_collection=event_collection, timeframe=timeframe, timezone=timezone,
                         interval=interval, filters=filters, group_by=group_by, max_age=max_age)


def sum(event_collection, target_property, timeframe=None, timezone=None, interval=None, filters=None,
        group_by=None, max_age=None):
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
    example: {["property_name":"device", "operator":"eq", "property_value":"iPhone"}]
    :param group_by: string or array of strings, the name(s) of the properties you would
    like to group you results by.  example: "customer.id" or ["browser","operating_system"]
    :param max_age: an integer, greater than 30 seconds, the maximum 'staleness' you're
    willing to trade for increased query performance, in seconds

    """
    _initialize_client_from_environment()
    return _client.sum(event_collection=event_collection, timeframe=timeframe, timezone=timezone,
                       interval=interval, filters=filters, group_by=group_by,
                       target_property=target_property, max_age=max_age)


def minimum(event_collection, target_property, timeframe=None, timezone=None, interval=None, filters=None,
            group_by=None, max_age=None):
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
    example: {["property_name":"device", "operator":"eq", "property_value":"iPhone"}]
    :param group_by: string or array of strings, the name(s) of the properties you would
    like to group you results by.  example: "customer.id" or ["browser","operating_system"]
    :param max_age: an integer, greater than 30 seconds, the maximum 'staleness' you're
    willing to trade for increased query performance, in seconds

    """
    _initialize_client_from_environment()
    return _client.minimum(event_collection=event_collection, timeframe=timeframe, timezone=timezone,
                           interval=interval, filters=filters, group_by=group_by,
                           target_property=target_property, max_age=max_age)


def maximum(event_collection, target_property, timeframe=None, timezone=None, interval=None, filters=None,
            group_by=None, max_age=None):
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
    example: {["property_name":"device", "operator":"eq", "property_value":"iPhone"}]
    :param group_by: string or array of strings, the name(s) of the properties you would
    like to group you results by.  example: "customer.id" or ["browser","operating_system"]
    :param max_age: an integer, greater than 30 seconds, the maximum 'staleness' you're
    willing to trade for increased query performance, in seconds

    """
    _initialize_client_from_environment()
    return _client.maximum(event_collection=event_collection, timeframe=timeframe, timezone=timezone,
                           interval=interval, filters=filters, group_by=group_by,
                           target_property=target_property, max_age=max_age)


def average(event_collection, target_property, timeframe=None, timezone=None, interval=None, filters=None,
            group_by=None, max_age=None):
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
    example: {["property_name":"device", "operator":"eq", "property_value":"iPhone"}]
    :param group_by: string or array of strings, the name(s) of the properties you would
    like to group you results by.  example: "customer.id" or ["browser","operating_system"]
    :param max_age: an integer, greater than 30 seconds, the maximum 'staleness' you're
    willing to trade for increased query performance, in seconds

    """
    _initialize_client_from_environment()
    return _client.average(event_collection=event_collection, timeframe=timeframe, timezone=timezone,
                           interval=interval, filters=filters, group_by=group_by,
                           target_property=target_property, max_age=max_age)


def median(event_collection, target_property, timeframe=None, timezone=None, interval=None, filters=None,
            group_by=None, max_age=None):
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
    example: {["property_name":"device", "operator":"eq", "property_value":"iPhone"}]
    :param group_by: string or array of strings, the name(s) of the properties you would
    like to group you results by.  example: "customer.id" or ["browser","operating_system"]
    :param max_age: an integer, greater than 30 seconds, the maximum 'staleness' you're
    willing to trade for increased query performance, in seconds

    """
    _initialize_client_from_environment()
    return _client.median(event_collection=event_collection, timeframe=timeframe, timezone=timezone,
                           interval=interval, filters=filters, group_by=group_by,
                           target_property=target_property, max_age=max_age)


def percentile(event_collection, target_property, percentile, timeframe=None, timezone=None, interval=None,
               filters=None, group_by=None, max_age=None):
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
    example: {["property_name":"device", "operator":"eq", "property_value":"iPhone"}]
    :param group_by: string or array of strings, the name(s) of the properties you would
    like to group you results by.  example: "customer.id" or ["browser","operating_system"]
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
        target_property=target_property,
        max_age=max_age,
    )


def count_unique(event_collection, target_property, timeframe=None, timezone=None, interval=None,
                 filters=None, group_by=None, max_age=None):
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
    example: {["property_name":"device", "operator":"eq", "property_value":"iPhone"}]
    :param group_by: string or array of strings, the name(s) of the properties you would
    like to group you results by.  example: "customer.id" or ["browser","operating_system"]
    :param max_age: an integer, greater than 30 seconds, the maximum 'staleness' you're
    willing to trade for increased query performance, in seconds

    """
    _initialize_client_from_environment()
    return _client.count_unique(event_collection=event_collection, timeframe=timeframe, timezone=timezone,
                                interval=interval, filters=filters, group_by=group_by,
                                target_property=target_property, max_age=max_age)


def select_unique(event_collection, target_property, timeframe=None, timezone=None, interval=None,
                  filters=None, group_by=None, max_age=None):
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
    example: {["property_name":"device", "operator":"eq", "property_value":"iPhone"}]
    :param group_by: string or array of strings, the name(s) of the properties you would
    like to group you results by.  example: "customer.id" or ["browser","operating_system"]
    :param max_age: an integer, greater than 30 seconds, the maximum 'staleness' you're
    willing to trade for increased query performance, in seconds

    """
    _initialize_client_from_environment()
    return _client.select_unique(event_collection=event_collection, timeframe=timeframe, timezone=timezone,
                                 interval=interval, filters=filters, group_by=group_by,
                                 target_property=target_property, max_age=max_age)


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
    example: {["property_name":"device", "operator":"eq", "property_value":"iPhone"}]
    :param latest: int, the number of most recent records you'd like to return
    :param email: string, optional string containing an email address to email results to
    :param property_names: string or list of strings, used to limit the properties returned

    """
    _initialize_client_from_environment()
    return _client.extraction(event_collection=event_collection, timeframe=timeframe, timezone=timezone,
                              filters=filters, latest=latest, email=email, property_names=property_names)


def funnel(steps, timeframe=None, timezone=None, max_age=None):
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
    return _client.funnel(steps=steps, timeframe=timeframe, timezone=timezone, max_age=max_age)


def multi_analysis(event_collection, analyses, timeframe=None, interval=None,
                   timezone=None, filters=None, group_by=None, max_age=None):
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
    example: {["property_name":"device", "operator":"eq", "property_value":"iPhone"}]
    :param group_by: string or array of strings, the name(s) of the properties you would
    like to group you results by.  example: "customer.id" or ["browser","operating_system"]
    :param max_age: an integer, greater than 30 seconds, the maximum 'staleness' you're
    willing to trade for increased query performance, in seconds

    """
    _initialize_client_from_environment()
    return _client.multi_analysis(event_collection=event_collection, timeframe=timeframe,
                                  interval=interval, timezone=timezone, filters=filters,
                                  group_by=group_by, analyses=analyses, max_age=max_age)
