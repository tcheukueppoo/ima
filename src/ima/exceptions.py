class OutOfBoundError(Exception):
    """Cannot go back, currently at the first page"""

class HTTPResponseError(Exception):
    """Error returned by the server"""

class FileExistsError(Exception):
    """File already exists on filesystem"""

class UnsupportedEngine(Exception):
    """Search engine is unsupported"""

class CannotGoBack(Exception):
    """Cannot Go back, it isn't your fault"""
