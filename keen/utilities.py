VERSION = "0.3.31"


def version():
    """
    Retrieves the current version of the SDK
    """
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
