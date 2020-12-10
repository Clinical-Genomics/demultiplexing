"""
    Demulutplexing Exceptions
"""


class DemuxError(Exception):
    """
    Base exception for the package
    """

    def __init__(self, message):
        super(DemuxError, self).__init__()
        self.message = message


class IndexReportError(DemuxError):
    """
    Exception for errors in index report module
    """
