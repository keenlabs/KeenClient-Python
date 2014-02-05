Keen IO Official Python Client Library
======================================

[![Build Status](https://secure.travis-ci.org/keenlabs/KeenClient-Python.png)](http://travis-ci.org/keenlabs/KeenClient-Python)

This is the official Python Client for the [Keen IO](https://keen.io/) API. The
Keen IO API lets developers build analytics features directly into their apps.

This is still under active development. Stay tuned for improvements!

### Installation

Use pip to install!

    pip install keen

This client is known to work on Python 2.6, 2.7, 3.2, and 3.3

### Usage

To use this client with the Keen IO API, you have to configure your Keen IO Project ID and its access keys (if you need an account, [sign up here](https://keen.io/) - it's free).

Setting a write key is required for publishing events. Setting a read key is required for running queries. The recommended way to set this configuration information is via the environment. The keys you can set are `KEEN_PROJECT_ID`, `KEEN_WRITE_KEY`, and `KEEN_READ_KEY`.

If you don't want to use environment variables for some reason, you can directly set values as follows:

```python
    keen.project_id = "xxxx"
    keen.write_key = "yyyy"
    keen.read_key = "zzzz"
```

You can also configure unique client instances as follows:

```python
    from keen.client import KeenClient

    client = KeenClient(
        project_id="xxxx",
        write_key="yyyy",
        read_key="zzzz"
    )
```

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

Here are some examples of querying.  Let's assume you've added some events to the "purchases" collection.

```python
    keen.count("purchases") # => 100
    keen.sum("purchases", target_property="price") # => 10000
    keen.minimum("purchases", target_property="price") # => 20
    keen.maximum("purchases", target_property="price") # => 100
    keen.average("purchases", target_property="price") # => 49.2

    keen.sum("purchases", target_property="price", group_by="item.id") # => [{ "item.id": 123, "result": 240 }, { ... }]

    keen.count_unique("purchases", target_property="user.id") # => 3
    keen.select_unique("purchases", target_property="user.email") # => ["bob@aol.com", "joe@yahoo.biz"]

    keen.extraction("purchases", timeframe="today") # => [{ "price" => 20, ... }, { ... }]

    keen.multi_analysis("purchases", analyses={"total":{"analysis_type":"sum", "target_property":"price"}, "average":{"analysis_type":"average", "target_property":"price"}) # => {"total":10329.03, "average":933.93}

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

### To Do

* Asynchronous insert
* Scoped keys

### Questions & Support

If you have any questions, bugs, or suggestions, please
report them via Github Issues. Or, come chat with us anytime
at [users.keen.io](http://users.keen.io). We'd love to hear your feedback and ideas!

### Contributing
This is an open source project and we love involvement from the community! Hit us up with pull requests and issues.
