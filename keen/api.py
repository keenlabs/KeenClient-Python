# -*- coding: utf-8 -*-

import requests
from keen import exceptions

try:
    import simplejson as json
except ImportError:
    import json


__author__ = 'dkador'


class KeenApi(object):
    """
    Responsible for communicating with the Keen API. Used by multiple
    persistence strategies or async processing.
    """

    # the default base URL of the Keen API
    base_url = "https://api.keen.io"
    # the default version of the Keen API
    api_version = "3.0"
    # the default JSON encoder class
    json_encoder = json.JSONEncoder


    # self says it belongs to KeenApi/andOr is the object passed into KeenApi
    # __init__ create keenapi object whenever KeenApi class is invoked
    def __init__(self, project_id,
                 write_key=None, read_key=None,
                 base_url=None, api_version=None, json_encoder=None):
        """
        Initializes a KeenApi object

        :param project_id: the Keen project ID
        :param write_key: a Keen IO Scoped Key for Writes
        :param read_key: a Keen IO Scoped Key for Reads
        :param base_url: optional, set this to override where API requests
        are sent
        :param api_version: string, optional, set this to override what API
        version is used
        :param json_encoder: optional, class for custom encoding, inherited 
        from json.JSONEncoder
        """
        # super? recreates the object with values passed into KeenApi
        super(KeenApi, self).__init__()
        self.project_id = project_id
        self.write_key = write_key
        self.read_key = read_key
        if base_url:
            self.base_url = base_url
        if api_version:
            self.api_version = api_version
        if json_encoder:
            self.json_encoder = json_encoder

    def post_event(self, event):
        """
        Posts a single event to the Keen IO API. The write key must be set first.

        :param event: an Event to upload
        """
        if not self.write_key:
            raise exceptions.InvalidEnvironmentError(
                "The Keen IO API requires a write key to send events. "
                "Please set a 'write_key' when initializing the "
                "KeenApi object."
            )

        url = "{0}/{1}/projects/{2}/events/{3}".format(self.base_url, self.api_version,
                                                       self.project_id,
                                                       event.event_collection)
        headers = {"Content-Type": "application/json", "Authorization": self.write_key}
        payload = event.to_json(json_encoder=self.json_encoder)
        response = requests.post(url, data=payload, headers=headers)
        if response.status_code != 201:
            error = response.json()
            raise exceptions.KeenApiError(error)

    def post_events(self, events):

        """
        Posts a single event to the Keen IO API. The write key must be set first.

        :param events: an Event to upload
        """
        if not self.write_key:
            raise exceptions.InvalidEnvironmentError(
                "The Keen IO API requires a write key to send events. "
                "Please set a 'write_key' when initializing the "
                "KeenApi object."
            )

        url = "{0}/{1}/projects/{2}/events".format(self.base_url, self.api_version,
                                                   self.project_id)
        headers = {"Content-Type": "application/json", "Authorization": self.write_key}
        payload = json.dumps(events, cls=self.json_encoder)
        response = requests.post(url, data=payload, headers=headers)
        if response.status_code != 200:
            error = response.json()
            raise exceptions.KeenApiError(error)

    def query(self, analysis_type, params):
        """
        Performs a query using the Keen IO analysis API.  A read key must be set first.

        """
        if not self.read_key:
            raise exceptions.InvalidEnvironmentError(
                "The Keen IO API requires a read key to perform queries. "
                "Please set a 'read_key' when initializing the "
                "KeenApi object."
            )

        url = "{0}/{1}/projects/{2}/queries/{3}".format(self.base_url, self.api_version,
                                                        self.project_id, analysis_type)

        headers = {"Authorization": self.read_key}
        payload = params
        response = requests.get(url, params=payload, headers=headers)
        if response.status_code != 200:
            error = response.json()
            raise exceptions.KeenApiError(error)

        return response.json()["result"]
