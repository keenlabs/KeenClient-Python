# Changelog


## 0.3.28

* Fix incorrect README.

## 0.3.27

* Return JSON response when uploading events in a batch.

## 0.3.26

* Removed unused `Padding` from requirements.txt to make python 3.x installs cleaner.

## 0.3.25

* Replaced defunct `pycrypto` library with `cryptodome`.
* Fixed UnicodeDecodeError under PY3 while installing in Windows.

## 0.3.24

* Updated documentation

## 0.3.23

* Added status code to JSON parse error response

## 0.3.22

* Added support for python 3.5

## 0.3.21

* Fixed bug with scoped key generation not working with newer Keen projects.

## 0.3.20

* Added `saved_queries` support
* Added Python 3.4 support

## 0.3.19

* Added `base_url` as a possible env variable

## 0.3.18

* Updated error handling to except `ValueError`

## 0.3.17

* Fixed timestamp overriding keen addons
* Added `get_collection` and `get_all_collections` methods

## 0.3.16

* Added `all_keys` parameter which allows users to expose all keys in query response.
* Added `delete_events` method.

## 0.3.15

* Added better error handling to surface all errors from HTTP API calls.

## 0.3.14

* Added compatibility for pip 1.0

## 0.3.13

* Added compatibility for pip < 1.5.6

## 0.3.12

* Made requirements more flexible.

## 0.3.11

* Added `requirements.txt` to pypi package.

## 0.3.10

* Fixed requirements in `setup.py`
* Updated test inputs and documentation.

## 0.3.9

* Added ```master_key``` parameter.

## 0.3.8

* Mocked tests.
* Added ```median``` query method.
* Added support for `$python setup.py test`.

## 0.3.7

* Upgraded to requests==2.5.1

## 0.3.6

* Added ```max_age``` parameter for caching.

## 0.3.5

* Added client configurable timeout to gets.

## 0.3.4

* Added ```percentile``` query method.

## 0.3.3

* Support ```interval``` parameter for multi analyses on the keen module.

## 0.3.2

* Reuse internal requests' session inside an instance of KeenApi.

## 0.3.1

* Support ```property_names``` parameter for extractions.

## 0.3.0

* Added client configurable timeout to posts.
* Upgraded to requests==2.2.1.

## 0.2.3

* Fixed sys.version_info issue with Python 2.6.

## 0.2.2

* Added interval to multi_analysis.

## 0.2.1

* Added stacktrace_id and unique_id to Keen API errors.

## 0.2.0

* Added add_events method to keen/__init__.py so it can be used at a module level.
* Added method to generate image beacon URLs.

## 0.1.9

* Added support for publishing events in batches
* Added support for configuring client automatically from environment
* Added methods on keen module directly

## 0.1.8

* Added querying support

## 0.1.7

* Bugfix to use write key when sending events - do not use ## 0.1.6!

## 0.1.6

* Changed project token -> project ID.
* Added support for read and write scoped keys.
* Added support for generating scoped keys yourself.
* Added support for python 2.6, 3.2, and 3.3

## 0.1.5

* Added documentation.
