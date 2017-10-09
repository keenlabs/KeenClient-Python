Keen IO Official Python Client Library
======================================

|build-status|

This is the official Python Client for the `Keen IO <https://keen.io/>`_ API. The
Keen IO API lets developers build analytics features directly into their apps.

This is still under active development. Stay tuned for improvements!

Installation
------------

Use pip to install!

::

    pip install keen

This client is known to work on Python 2.6, 2.7, 3.2, 3.3, 3.4, 3.5 and 3.6.

For versions of Python < 2.7.9, you’ll need to install pyasn1, ndg-httpsclient, pyOpenSSL.

Usage
-----

To use this client with the Keen IO API, you have to configure your Keen IO Project ID and its access
keys (if you need an account, `sign up here <https://keen.io/>`_ - it's free).

Setting a write key is required for publishing events. Setting a read key is required for
running queries. The recommended way to set this configuration information is via the environment.
The keys you can set are `KEEN_PROJECT_ID`, `KEEN_WRITE_KEY`, `KEEN_READ_KEY`, and `KEEN_MASTER_KEY`.
As per the `Principle of Least Privilege <https://en.wikipedia.org/wiki/Principle_of_least_privilege>`_, it's recommended that you not use the master_key if not 
necessary. This SDK will expect and use the precise key for a given operation, and throw an
exception in cases of misuse.

If you don't want to use environment variables for some reason, you can directly set values as follows:

.. code-block:: python

    keen.project_id = "xxxx"
    keen.write_key = "yyyy"
    keen.read_key = "zzzz"
    keen.master_key = "abcd" # not required for typical usage


For information on how to configure unique client instances, take a look at the
`Advanced Usage <#advanced-usage>`_ section below.

Send Events to Keen IO
``````````````````````

Once you've set `KEEN_PROJECT_ID` and `KEEN_WRITE_KEY`, sending events is simple:

.. code-block:: python

    keen.add_event("sign_ups", {
        "username": "lloyd",
        "referred_by": "harry"
    })


Send Batch Events to Keen IO
````````````````````````````

You can upload Events in a batch, like so:

.. code-block:: python

    # uploads 4 events total - 2 to the "sign_ups" collection and 2 to the "purchases" collection
    keen.add_events({
        "sign_ups": [
            { "username": "nameuser1" },
            { "username": "nameuser2" }
        ],
        "purchases": [
            { "price": 5 },
            { "price": 6 }
        ]
    })


That's it! After running your code, check your Keen IO Project to see the event/events has been added.

Do analysis with Keen IO
````````````````````````

Here are some examples of querying. Let's assume you've added some events to the "purchases" collection.
For more code samples, take a look at Keen's `docs <https://keen.io/docs/api/?python#>`_

.. code-block:: python

    keen.count("purchases", timeframe="this_14_days") # => 100
    keen.sum("purchases", target_property="price", timeframe="this_14_days") # => 10000
    keen.minimum("purchases", target_property="price", timeframe="this_14_days") # => 20
    keen.maximum("purchases", target_property="price", timeframe="this_14_days") # => 100
    keen.average("purchases", target_property="price", timeframe="this_14_days") # => 49.2

    keen.sum("purchases", target_property="price", group_by="item.id", timeframe="this_14_days") # => [{ "item.id": 123, "result": 240 }, { ... }]

    keen.count_unique("purchases", target_property="user.id", timeframe="this_14_days") # => 3
    keen.select_unique("purchases", target_property="user.email", timeframe="this_14_days") # => ["bob@aol.com", "joe@yahoo.biz"]

    keen.extraction("purchases", timeframe="today") # => [{ "price" => 20, ... }, { ... }]

    keen.multi_analysis(
        "purchases",
        analyses={
            "total":{
                "analysis_type": "sum",
                "target_property": "price"
            },
            "average":{
                "analysis_type": "average",
                "target_property": "price"
            }
        },
        timeframe='this_14_days'
    ) # => {"total":10329.03, "average":933.93}

    step1 = {
        "event_collection": "sign_ups",
        "actor_property": "user.email"
    }
    step2 = {
        "event_collection": "purchases",
        "actor_property": "user.email"
    }
    keen.funnel([step1, step2], timeframe="today") # => [2039, 201]


To return the full API response from a funnel analysis (as opposed to the singular "result" key), set `all_keys=True`.

For example, `keen.funnel([step1, step2], timeframe="today", all_keys=True)` would return "result", "actors" and "steps" keys.

Delete Events
`````````````

The Keen IO API allows you to `delete events <https://keen.io/docs/api/#delete-events>`_ from event collections, optionally supplying filters, timeframe or timezone to narrow the scope of what you would like to delete.

You'll need to set your master_key.

.. code-block:: python

    keen.delete_events("event_collection", filters=[{"property_name": 'username', "operator": 'eq', "property_value": 'Bob'}])

Advanced Usage
``````````````

See below for more options.

Check Batch Upload Response For Errors
''''''''''''''''''''''''''''''''''''''

When you upload events in a batch, some of them may succeed and some of them may have errors. The Keen API returns information on each. Here's an example:

Upload code (remember, Keen IO doesn't allow periods in property names):

.. code-block:: python

    response = keen.add_events({
        "sign_ups": [
            { "username": "nameuser1" },
            { "username": "nameuser2", "an.invalid.property.name": 1 }
        ],
        "purchases": [
            { "price": 5 },
            { "price": 6 }
        ]
    })

That code would result in the following API JSON response:

.. code-block:: javascript

    {
        "sign_ups": [
            {"success": true},
            {"success": false, "error": {"name": "some_error_name", "description": "some longer description"}}
        ],
        "purchases": [
            {"success": true},
            {"success": true}
        ]
    }

So in python, to check on the results of your batch, you'd have code like so:

.. code-block:: python

    batch = {
        "sign_ups": [
            { "username": "nameuser1" },
            { "username": "nameuser2", "an.invalid.property.name": 1 }
        ],
        "purchases": [
            { "price": 5 },
            { "price": 6 }
        ]
    }
    response = keen.add_events(batch)

    for collection in response:
        collection_result = response[collection]
        event_count = 0
        for individual_result in collection_result:
            if not individual_result["success"]:
                print("Event had error! Collection: '{}'. Event body: '{}'.".format(collection, batch[collection][event_count]))
            event_count += 1

Configure Unique Client Instances
'''''''''''''''''''''''''''''''''

If you intend to send events or query from different projects within the same python file, you'll need to set up
unique client instances (one per project). You can do this by assigning an instance of KeenClient to a variable like so:

.. code-block:: python

    from keen.client import KeenClient

    client = KeenClient(
        project_id="xxxx",  # your project ID for collecting cycling data
        write_key="yyyy",
        read_key="zzzz",
        master_key="abcd" # not required for typical usage
    )

    client_hike = KeenClient(
        project_id="xxxx",  # your project ID for collecting hiking data (different from the one above)
        write_key="yyyy",
        read_key="zzzz",
        master_key="abcd" # not required for typical usage
    )


You can send events like this:

.. code-block:: python

    # add an event to an event collection in your cycling project
    client.add_event(...)

    # or add an event to an event collection in your hiking project
    client_hike.add_event(...)


Similarly, you can query events like this:

.. code-block:: python

    client.count(...)


Saved Queries
'''''''''''''

You can manage your `saved queries <https://keen.io/docs/api/?shell#saved-queries>`_ from the Keen python client.

.. code-block:: python

    # Create your KeenClient
    from keen.client import KeenClient

    client = KeenClient(
        project_id="xxxx",  # your project ID
        read_key="zzzz",
        master_key="abcd" # Most Saved Query functionality requires master_key
    )

    # Create a saved query
    saved_query_attributes = {
        # NOTE : For now, refresh_rate must explicitly be set to 0 unless you
        # intend to create a Cached Query.
        "refresh_rate": 0,
        "query": {
            "analysis_type": "count",
            "event_collection": "purchases",
            "timeframe": "this_2_weeks",
            "filters": [{
                "property_name": "price",
                "operator": "gte",
                "property_value": 1.00
            }]
        }
    }

    client.saved_queries.create("saved-query-name", saved_query_attributes)

    # Get all saved queries
    client.saved_queries.all()

    # Get one saved query
    client.saved_queries.get("saved-query-name")

    # Get saved query with results
    client.saved_queries.results("saved-query-name")

    # NOTE : Updating Saved Queries requires sending the entire query definition. Any attribute not
    # sent is interpreted as being cleared/removed. This means that properties set via another
    # client, including the Projects Explorer Web UI, will be lost this way.
    # 
    # The update() function makes this easier by allowing client code to just specify the
    # properties that need updating. To do this, it will retrieve the existing query definition
    # first, which means there will be two HTTP requests. Use update_full() in code that already
    # has a full query definition that can reasonably be expected to be current.

    # Update a saved query to now be a cached query with the minimum refresh rate of 4 hrs...

    # ...using partial update:
    client.saved_queries.update("saved-query-name", { "refresh_rate": 14400 })

    # ...using full update, if we've already fetched the query definition:
    saved_query_attributes["refresh_rate"] = 14400
    client.saved_queries.update_full("saved-query-name", saved_query_attributes)

    # Update a saved query to a new resource name...

    # ...using partial update:
    client.saved_queries.update("saved-query-name", { "query_name": "cached-query-name" })

    # ...using full update, if we've already fetched the query definition or have it lying around
    # for whatever reason. We send "refresh_rate" again, along with the entire definition, or else
    # it would be reset:
    saved_query_attributes["query_name"] = "cached-query-name"
    client.saved_queries.update_full("saved-query-name", saved_query_attributes)

    # Delete a saved query (use the new resource name since we just changed it)
    client.saved_queries.delete("cached-query-name")


Overwriting event timestamps
''''''''''''''''''''''''''''

Two time-related properties are included in your event automatically. The properties “keen.timestamp”
and “keen.created_at” are set at the time your event is recorded. You have the ability to overwrite the
keen.timestamp property. This could be useful, for example, if you are backfilling historical data. Be
sure to use `ISO-8601 Format <https://keen.io/docs/event-data-modeling/event-data-intro/#iso-8601-format>`_.

Keen stores all date and time information in UTC!

.. code-block:: python

    keen.add_event("sign_ups", {
        "keen": {
            "timestamp": "2012-07-06T02:09:10.141Z"
        },
        "username": "lloyd",
        "referred_by": "harry"
    })


Get from Keen IO with a Timeout
'''''''''''''''''''''''''''''''

By default, GET requests will timeout after 305 seconds. If you want to manually override this, you can
create a KeenClient with the "get_timeout" parameter. This client will fail GETs if no bytes have been
returned by the server in the specified time. For example:

.. code-block:: python

    from keen.client import KeenClient

    client = KeenClient(
        project_id="xxxx",
        write_key="yyyy",
        read_key="zzzz",
        get_timeout=100
    )


This will cause queries such as count(), sum(), and average() to timeout after 100 seconds. If this timeout
limit is hit, a requests.Timeout will be raised. Due to a bug in the requests library, you might also see an
SSLError (`#1294 <https://github.com/kennethreitz/requests/issues/1294>`_)

Send to Keen IO with a Timeout
''''''''''''''''''''''''''''''

By default, POST requests will timeout after 305 seconds. If you want to manually override this, you can
create a KeenClient with the "post_timeout" parameter. This client will fail POSTs if no bytes have been
returned by the server in the specified time. For example:

.. code-block:: python

    from keen.client import KeenClient

    client = KeenClient(
        project_id="xxxx",
        write_key="yyyy",
        post_timeout=100
    )


This will cause both add_event() and add_events() to timeout after 100 seconds. If this timeout limit is hit, a requests.Timeout will be raised. Due to a bug in the requests library, you might also see an SSLError (https://github.com/kennethreitz/requests/issues/1294)

Create Scoped Keys
''''''''''''''''''

The Python client enables you to create `Scoped Keys <https://keen.io/docs/security/#scoped-key>`_ easily. For example:

.. code-block:: python

    from keen.client import KeenClient
    from keen import scoped_keys

    api_key = KEEN_MASTER_KEY

    write_key = scoped_keys.encrypt(api_key, {"allowed_operations": ["write"]})
    read_key = scoped_keys.encrypt(api_key, {"allowed_operations": ["read"]})


`write_key` and `read_key` now contain scoped keys based on your master API key.

Testing
-------

To run tests:

::

    python setup.py test


Changelog
---------

This project is in alpha stage at version 0.4.0 . See the full CHANGELOG `here <./CHANGELOG.rst>`_.

To Do
-----

* Asynchronous insert
* Scoped keys

Questions & Support
-------------------

If you have any questions, bugs, or suggestions, please
report them via Github Issues. We'd love to hear your feedback and ideas!

Contributing
------------

This is an open source project and we love involvement from the community! Hit us up with pull requests and issues. Here are our `guidelines <./CONTRIBUTING.md>`_ for how to contribute.

.. |build-status| image:: https://secure.travis-ci.org/keenlabs/KeenClient-Python.png
    :target: http://travis-ci.org/keenlabs/KeenClient-Python
    :alt: Build status
