# encoding: utf-8

"""
Exception types for the last.fm library.
"""

class LastFMError(Exception):
    """
    The base class for all errors that can be raised by the last.fm library.
    """
    pass
    
class UnderspecifiedError(LastFMError, TypeError):
    """
    Raised when insufficient information is passed to a lookup method.
    """
    pass

class APIError(LastFMError):
    """
    The base class for errors returned by the last.fm servers.
    """
    
    def __new__(typ, message, code=None):
        if code and typ is APIError and code in api_errors:
            return api_errors[code](message, code)
        return LastFMError.__new__(typ, message)

class InvalidServiceError(APIError):
	pass

class InvalidMethodError(APIError):
	pass

class AuthenticationFailedError(APIError):
	pass

class InvalidFormatError(APIError):
	pass

class InvalidParametersError(APIError):
	pass

class InvalidResourceError(APIError):
	pass

class InvalidSessionKeyError(APIError):
	pass

class InvalidAPIKeyError(APIError):
	pass

class ServiceOfflineError(APIError):
	pass

class SubscribersOnlyError(APIError):
	pass

api_errors = {
    2: InvalidServiceError,
    3: InvalidMethodError,
    4: AuthenticationFailedError,
    5: InvalidFormatError,
    6: InvalidParametersError,
    7: InvalidResourceError,
    9: InvalidSessionKeyError,
    10: InvalidAPIKeyError,
    11: ServiceOfflineError,
    12: SubscribersOnlyError
}
