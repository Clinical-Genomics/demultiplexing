"""
    Demultiplexing exceptions
"""


class DemuxError(Exception):
    """
    Base exception for the package
    """

    def __init__(self):
        super(DemuxError, self).__init__()


class IndexReportError(DemuxError):
    """
    Exception for errors in index report module
    """
