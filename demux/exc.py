"""
    Demultiplexing exceptions
"""


class DemuxError(Exception):
    """
    Base exception for the package
    """

    def __init__(self, message: str = ""):
        super(DemuxError, self).__init__()
        self.message = message


class IndexReportError(DemuxError):
    """Exception for errors in index report module"""


class NoValidReagentKitFound(DemuxError):
    """Raised when no valid Reagent Kit is found in the run parameters file"""
