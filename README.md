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
    })

##### Send Batch Events to Keen IO

You can upload Events in a batch, like so:

    client.add_events({
        "sign_ups": [
            { "username": "nameuser1" },
            { "username": "nameuser2" } 
        ],
        "purchases": [
            { "price": 5 },
            { "price": 6 }
        ]
    })


##### Do analysis with Keen IO

    TODO
    
That's it! After running your code, check your Keen IO Project to see the event has been added.

### Changelog

##### 0.1.8

+ Added support for publishing events in batches

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
