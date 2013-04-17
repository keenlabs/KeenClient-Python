Keen IO Official Python Client Library
======================================

This is the official Python Client for the [Keen IO](https://keen.io/) API. The
Keen IO API lets developers build analytics features directly into their apps.

This is still under active development. Stay tuned for improvements!

### Installation

Use pip to install!

    pip install keen

This client is known to work on Python 2.7.3.

### Usage

To use this client with the Keen IO API, you have to configure your Keen IO Project ID (if you need an account, [sign up here](https://keen.io/) - it's free).

Once you have your Project ID, use the client like so:

   from keen.client import KeenClient
   
    project_id = "<YOUR_PROJECT_ID">
    client = KeenClient(project_id)
    client.add_event("sign_ups", {
        "username": "lloyd",
        "referred_by": "harry"
    }
    
That's it! After running your code, check your Keen IO Project to see the event has been added.

### Changelog

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
