class Error(Exception):
    """Base class of exceptions in py2dmat"""

    pass


class InputError(Error):
    """Exception raised for errors in inputs

    Attributes
    ==========
    message: str
        explanation
    """

    def __init__(self, message: str) -> None:
        self.message = message
