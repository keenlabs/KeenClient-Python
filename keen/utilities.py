VERSION = None

def version():
  """
  Retrives the current version of the SDK
  """

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
      "X-Keensdkversion-X": "python-#{0}".format(version)
  }