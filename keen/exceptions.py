__author__ = 'dkador'

class BaseKeenClientError(Exception):
    """
    Base class for all Keen Client errors.
    """

    def __str__(self):
        # all sub-classes should set self._message in their initializers
        return self._message


class InvalidProjectIdError(BaseKeenClientError):
    def __init__(self, project_id):
        super(InvalidProjectIdError, self).__init__(project_id)
        self.project_id = project_id
        self._message = "Invalid project ID: {}".format(project_id)


class InvalidAuthTokenError(BaseKeenClientError):
    def __init__(self, auth_token):
        super(InvalidAuthTokenError, self).__init__(auth_token)
        self.auth_token = auth_token
        self._message = "Invalid authorization token: {}".format(auth_token)


class InvalidPersistenceStrategyError(BaseKeenClientError):
    def __init__(self):
        super(InvalidPersistenceStrategyError, self).__init__()
        self._message = "Invalid persistence strategy. A persistence strategy" \
                        " must be an instance of BasePersistenceStrategy."


class KeenApiError(BaseKeenClientError):
    def __init__(self, api_error):
        super(KeenApiError, self).__init__(api_error)
        self.api_error = api_error
        self._message = "Error from Keen API. Details:\n Message: {}\nCode: "\
                        "{}".format(
            api_error["message"], api_error["error_code"]
        )