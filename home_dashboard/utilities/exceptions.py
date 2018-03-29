"""
Application defined errors.
"""

class Error(Exception):
    """
    Base class for exceptions in this module.
    """
    pass

class MeterError(Error):
    """
    Exception for something wrong with the meter.
    """

    def __init__(self, message):
        self.message = message
        super().__init__(message)

class ReadingError(Error):
    """
    Exception for something wrong with the reading.
    """

    def __init__(self, message):
        self.message = message
        super().__init__(message)
