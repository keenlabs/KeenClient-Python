Keen IO Official Python Client Library
======================================

[![Build Status](https://secure.travis-ci.org/keenlabs/KeenClient-Python.png)](http://travis-ci.org/keenlabs/KeenClient-Python)

This is the official Python Client for the [Keen IO](https://keen.io/) API. The
Keen IO API lets developers build analytics features directly into their apps.

This is still under active development. Stay tuned for improvements!

### Installation

Use pip to install!

    pip install keen

This client is known to work on Python 2.6, 2.7, 3.2, 3.3, 3.4 and 3.5.

For versions of Python < 2.7.9, you’ll need to install pyasn1, ndg-httpsclient, pyOpenSSL.

### Usage

To use this client with the Keen IO API, you have to configure your Keen IO Project ID and its access keys (if you need an account, [sign up here](https://keen.io/) - it's free).

Setting a write key is required for publishing events. Setting a read key is required for running queries. The recommended way to set this configuration information is via the environment. The keys you can set are `KEEN_PROJECT_ID`, `KEEN_WRITE_KEY`, `KEEN_READ_KEY`, and `KEEN_MASTER_KEY`.

If you don't want to use environment variables for some reason, you can directly set values as follows:

```python
    keen.project_id = "xxxx"
    keen.write_key = "yyyy"
    keen.read_key = "zzzz"
    keen.master_key = "abcd"
```

For information on how to configure unique client instances, take a look at the [Advanced Usage](https://github.com/keenlabs/KeenClient-Python#advanced-usage) section below.

##### Send Events to Keen IO

Once you've set `KEEN_PROJECT_ID` and `KEEN_WRITE_KEY`, sending events is simple:

```python
    keen.add_event("sign_ups", {
        "username": "lloyd",
        "referred_by": "harry"
    })
```

##### Send Batch Events to Keen IO

You can upload Events in a batch, like so:

```python
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
```


That's it! After running your code, check your Keen IO Project to see the event/events has been added.

##### Do analysis with Keen IO

Here are some examples of querying. Let's assume you've added some events to the "purchases" collection. For more code samples, take a look at Keen's [docs](https://keen.io/docs/api/?python#)

```python
    keen.count("purchases", timeframe="this_14_days") # => 100
    keen.sum("purchases", target_property="price", timeframe="this_14_days") # => 10000
    keen.minimum("purchases", target_property="price", timeframe="this_14_days") # => 20
    keen.maximum("purchases", target_property="price", timeframe="this_14_days") # => 100
    keen.average("purchases", target_property="price", timeframe="this_14_days") # => 49.2

    keen.sum("purchases", target_property="price", group_by="item.id", timeframe="this_14_days") # => [{ "item.id": 123, "result": 240 }, { ... }]

    keen.count_unique("purchases", target_property="user.id", timeframe="this_14_days") # => 3
    keen.select_unique("purchases", target_property="user.email", timeframe="this_14_days") # => ["bob@aol.com", "joe@yahoo.biz"]

    keen.extraction("purchases", timeframe="today") # => [{ "price" => 20, ... }, { ... }]

    keen.multi_analysis("purchases", analyses={
        "total":{
            "analysis_type": "sum",
            "target_property":"price",
            "timeframe": "this_14_days"
        },
        "average":{
            "analysis_type": "average",
            "target_property":"price",
            "timeframe": "this_14_days"
        }
    ) # => {"total":10329.03, "average":933.93}

    step1 = {
        "event_collection": "signup",
        "actor_property": "user.email"
    }
    step2 = {
        "event_collection": "purchase",
        "actor_property": "user.email"
    }
    keen.funnel([step1, step2], timeframe="today") # => [2039, 201]
```

To return the full API response (as opposed to the singular "result" key), set `all_keys=True`.

For example, `keen.funnel([step1, step2], all_keys=True)` would return "result", "actors" and "steps" keys.

##### Delete Events

The Keen IO API allows you to [delete events](https://keen.io/docs/api/#delete-events) from event collections, optionally supplying filters, timeframe or timezone to narrow the scope of what you would like to delete.

You'll need to set your master_key.

```python
    keen.delete_events("event_collection", filters=[{"property_name": 'username', "operator": 'eq', "property_value": 'Bob'}])
```

#### Advanced Usage

See below for more options.

##### Configure Unique Client Instances

If you intend to send events or query from different projects within the same python file, you'll need to set up unique client instances (one per project). You can do this by assigning an instance of KeenClient to a variable like so:

```python
    from keen.client import KeenClient

    client = KeenClient(
        project_id="xxxx",  # your project ID for collecting cycling data
        write_key="yyyy",
        read_key="zzzz",
        master_key="abcd"
    )

    client_hike = KeenClient(
        project_id="xxxx",  # your project ID for collecting hiking data (different from the one above)
        write_key="yyyy",
        read_key="zzzz",
        master_key="abcd"
    )
```

You can send events like this:

```python
    # add an event to an event collection in your cycling project
    client.add_event(...)

    # or add an event to an event collection in your hiking project
    client_hike.add_event(...)
```

Similarly, you can query events like this:

```python
    client.count(...)
```

##### Saved Queries
You can manage your saved queries from the Keen python client.

```python
# Create a saved query
keen.saved_queries.create("name", saved_query_attributes)

# Get all saved queries
keen.saved_queries.all()

# Get one saved query
keen.saved_queries.get("saved-query-slug")

# Get saved query with results
keen.saved_queries.results("saved-query-slug")

# Update a saved query
saved_query_attributes = { refresh_rate: 14400 }
keen.saved_queries.update("saved-query-slug", saved_query_attributes)

# Delete a saved query
keen.saved_queries.delete("saved-query-slug")
```

##### Overwriting event timestamps

Two time-related properties are included in your event automatically. The properties “keen.timestamp” and “keen.created_at” are set at the time your event is recorded. You have the ability to overwrite the keen.timestamp property. This could be useful, for example, if you are backfilling historical data. Be sure to use [ISO-8601 Format](https://keen.io/docs/event-data-modeling/event-data-intro/#iso-8601-format).

Keen stores all date and time information in UTC!

```python
    keen.add_event("sign_ups", {
        "keen": {
            "timestamp": "2012-07-06T02:09:10.141Z"
        },
        "username": "lloyd",
        "referred_by": "harry"
    })
```

##### Get from Keen IO with a Timeout

By default, GET requests will timeout after 305 seconds. If you want to manually override this, you can create a KeenClient with the "get_timeout" parameter. This client will fail GETs if no bytes have been returned by the server in the specified time. For example:

```python
    from keen.client import KeenClient

    client = KeenClient(
        project_id="xxxx",
        write_key="yyyy",
        read_key="zzzz",
        get_timeout=100

    )
```

This will cause queries such as count(), sum(), and average() to timeout after 100 seconds. If this timeout limit is hit, a requests.Timeout will be raised. Due to a bug in the requests library, you might also see an SSLError (https://github.com/kennethreitz/requests/issues/1294)

##### Send to Keen IO with a Timeout

By default, POST requests will timeout after 305 seconds. If you want to manually override this, you can create a KeenClient with the "post_timeout" parameter. This client will fail POSTs if no bytes have been returned by the server in the specified time. For example:

```python
    from keen.client import KeenClient

    client = KeenClient(
        project_id="xxxx",
        write_key="yyyy",
        read_key="zzzz",
        master_key="abcd",
        post_timeout=100

    )
```

This will cause both add_event() and add_events() to timeout after 100 seconds. If this timeout limit is hit, a requests.Timeout will be raised. Due to a bug in the requests library, you might also see an SSLError (https://github.com/kennethreitz/requests/issues/1294)

##### Create Scoped Keys

The Python client enables you to create [Scoped Keys](https://keen.io/docs/security/#scoped-key) easily. For example:

```python
    from keen.client import KeenClient
    from keen import scoped_keys

    api_key = KEEN_MASTER_KEY

    write_key = scoped_keys.encrypt(api_key, {"allowed_operations": ["write"]})
    read_key = scoped_keys.encrypt(api_key, {"allowed_operations": ["read"]})
```

`write_key` and `read_key` now contain scoped keys based on your master API key.

### Testing

To run tests:
```
python setup.py tests
```

### Changelog

##### 0.3.23
+ Added status code to JSON parse error response

##### 0.3.22
+ Added support for python 3.5

##### 0.3.21
+ Fixed bug with scoped key generation not working with newer Keen projects.

##### 0.3.20
+ Added `saved_queries` support
+ Added Python 3.4 support

##### 0.3.19
+ Added `base_url` as a possible env variable

##### 0.3.18
+ Updated error handling to except `ValueError`

##### 0.3.17
+ Fixed timestamp overriding keen addons
+ Added `get_collection` and `get_all_collections` methods

##### 0.3.16
+ Added `all_keys` parameter which allows users to expose all keys in query response.
+ Added `delete_events` method.

##### 0.3.15
+ Added better error handling to surface all errors from HTTP API calls.

##### 0.3.14
+ Added compatibility for pip 1.0

##### 0.3.13
+ Added compatibility for pip < 1.5.6

##### 0.3.12
+ Made requirements more flexible.

##### 0.3.11
+ Added `requirements.txt` to pypi package.

##### 0.3.10
+ Fixed requirements in `setup.py`
+ Updated test inputs and documentation.

##### 0.3.9
+ Added ```master_key``` parameter.

##### 0.3.8
+ Mocked tests.
+ Added ```median``` query method.
+ Added support for `$python setup.py test`.

##### 0.3.7
+ Upgraded to requests==2.5.1

##### 0.3.6
+ Added ```max_age``` parameter for caching.

##### 0.3.5
+ Added client configurable timeout to gets.

##### 0.3.4
+ Added ```percentile``` query method.

##### 0.3.3

+ Support ```interval``` parameter for multi analyses on the keen module.

##### 0.3.2

+ Reuse internal requests' session inside an instance of KeenApi.

##### 0.3.1

+ Support ```property_names``` parameter for extractions.

##### 0.3.0

+ Added client configurable timeout to posts.
+ Upgraded to requests==2.2.1.

##### 0.2.3

+ Fixed sys.version_info issue with Python 2.6.

##### 0.2.2

+ Added interval to multi_analysis.

##### 0.2.1

+ Added stacktrace_id and unique_id to Keen API errors.

##### 0.2.0

+ Added add_events method to keen/__init__.py so it can be used at a module level.
+ Added method to generate image beacon URLs.

##### 0.1.9

+ Added support for publishing events in batches
+ Added support for configuring client automatically from environment
+ Added methods on keen module directly

##### 0.1.8

+ Added querying support

##### 0.1.7

+ Bugfix to use write key when sending events - do not use 0.1.6!

##### 0.1.6

+ Changed project token -> project ID.
+ Added support for read and write scoped keys.
+ Added support for generating scoped keys yourself.
+ Added support for python 2.6, 3.2, and 3.3

##### 0.1.5

+ Added documentation.

### To Do

* Asynchronous insert
* Scoped keys

### Questions & Support

If you have any questions, bugs, or suggestions, please
report them via Github Issues. We'd love to hear your feedback and ideas!

### Contributing
This is an open source project and we love involvement from the community! Hit us up with pull requests and issues.
