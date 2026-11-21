from logging import getLogger
from warnings import warn

from ..loggers import DEFAULT_LOG_NAME


def get_logger(obj):
    """Get the object logger or its parent's one

    Parameters
    ----------
    obj :
        A pyleecan object

    Returns
    -------
    logger : logging.Logger
        Pyleecan object dedicated logger
    """

    warn(
        "get_logger is deprecated, use classes_common.logger_context.get_logger (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    if hasattr(obj, "logger_name"):  # Object logger
        return getLogger(obj.logger_name)
    elif hasattr(obj, "parent") and obj.parent != None:  # Parent logger
        return obj.parent.get_logger()
    else:  # Default logger
        return getLogger(DEFAULT_LOG_NAME)
