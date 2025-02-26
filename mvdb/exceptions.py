class mvdbBaseException(Exception):
    """Base exception class for mvdb pkg."""

    pass


class DuplicateMovieError(mvdbBaseException):
    """Exception raised when a duplicate movie entry is added to catalog."""

    pass
