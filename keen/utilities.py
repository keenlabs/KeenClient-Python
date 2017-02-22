import os

VERSION = None

def version():
    """
    Retrieves the current version of the SDK
    """

    global VERSION
    if VERSION is None:
        version_file = open(os.path.join('.', 'VERSION'))
        VERSION = version_file.read().strip()

    return VERSION

def headers(api_key):
    """
    Helper function to easily get the correct headers for an endpoint

    :params api_key: The appropriate API key for the request being made
    """

    return {
      "Content-Type": "application/json",
      "Authorization": api_key,
      "Keen-Sdk": "python-{0}".format(version())
    }
