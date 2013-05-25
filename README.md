Keen IO Official Python Client Library
======================================

[![Build Status](https://secure.travis-ci.org/keenlabs/KeenClient-Python.png?branch=new-keys)](http://travis-ci
.org/keenlabs/KeenClient-Python)

This is the official Python Client for the [Keen IO](https://keen.io/) API. The
Keen IO API lets developers build analytics features directly into their apps.

This is still under active development. Stay tuned for improvements!

### Installation

Use pip to install!

    pip install keen

This client is known to work on Python 2.7.3.

### Usage

To use this client with the Keen IO API, you have to configure your Keen IO Project ID and its access keys (if you need an account, [sign up here](https://keen.io/) - it's free).

##### Send Events to Keen IO

Once you have your Project ID, use the client like so:

    from keen.client import KeenClient
   
    project_id = "<YOUR_PROJECT_ID>"
    write_key  = "<YOUR_WRITE_KEY>"
    client = KeenClient(
        project_id, 
        write_key=write_key
    )
    client.add_event("sign_ups", {
        "username": "lloyd",
        "referred_by": "harry"
    }

That's it! After running your code, check your Keen IO Project to see the event has been added.

##### Do analysis with Keen IO

If you want to do analysis, configure you client like this:

    from keen.client import KeenClient

    project_id = "<YOUR_PROJECT_ID>"
    read_key = "<YOUR_READ_KEY>"
    client = KeenClient(
        project_id,
        read_key=read_key
    )

Here are some examples of querying.  Let's assume you've added some events to the "purchases" collection.

    client.count("purchases") # => 100
    client.sum("purchases", target_property="price") # => 10000
    client.minimum("purchases", target_property="price") # => 20
    client.maximum("purchases", target_property="price") # => 100
    client.average("purchases", target_property="price") # => 49.2

    client.sum("purchases", target_property="price", group_by="item.id") # => [{ "item.id": 123, "result": 240 }, { ... }]

    client.count_unique("purchases", target_property="user.id") # => 3
    client.select_unique("purchases", target_property="user.email") # => ["bob@aol.com", "joe@yahoo.biz"]

    client.extraction("purchases", timeframe="today") # => [{ "price" => 20, ... }, { ... }]

    client.multi_analysis("purchases", analyses={"total":{"analysis_type":"sum", "target_property":"price"}, "average":{"analysis_type":"average", "target_property":"price"}) # => {"total":10329.03, "average":933.93}



### Changelog

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

* Bulk event insert
* Asynchronous insert
* Scoped keys

### Questions & Support

If you have any questions, bugs, or suggestions, please
report them via Github Issues. Or, come chat with us anytime
at [users.keen.io](http://users.keen.io). We'd love to hear your feedback and ideas!

### Contributing
This is an open source project and we love involvement from the community! Hit us up with pull requests and issues.
