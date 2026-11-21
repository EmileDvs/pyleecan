"""Logger of the pyleecan objects without the parent chain (PLAN.md Step 9).

The legacy ``get_logger`` walks the parents of an object up to one with a
``logger_name`` (the simulation and its models get per-simulation logger names
from ``Simulation.init_logger``, with the per-simulation log file). Here:

1. the object's own ``logger_name`` (set by ``init_logger`` on the simulation,
   its models and the output);
2. else the simulation being run: ``Simulation.run`` sets the logger context
   (``logger_context(simulation)``), the name is read when the logger is
   requested (after ``init_logger``), nested simulations get their own context;
3. else the parents (legacy layer of Phase 1, removed with the parent links);
4. else the default logger.

Shared by the class backends: methods and functions call
``get_logger(obj)`` (generator pass, ``modernize.redirect_get_logger``).
"""

from contextlib import contextmanager
from contextvars import ContextVar
from logging import Logger, getLogger

from ..loggers import DEFAULT_LOG_NAME

_CONTEXT = ContextVar("pyleecan_logger_context", default=None)
"""Object giving the logger name of the simulation in progress"""


def _logger_name(obj):
    name = getattr(obj, "logger_name", None)
    return name if name not in (None, "") else None


def get_logger(obj=None) -> Logger:
    """Get the logger of a pyleecan object

    Parameters
    ----------
    obj : object, optional
        A pyleecan object (None: the logger of the simulation in progress)

    Returns
    -------
    logger : logging.Logger
        Logger of the object, of the simulation in progress or the default one
    """
    name = _logger_name(obj)
    if name is None:  # The simulation in progress
        context = _CONTEXT.get()
        if context is not None:
            name = _logger_name(context)
    if name is None:  # Legacy layer: the parents (Phase 1)
        parent = getattr(obj, "parent", None)
        visited = set()
        while parent is not None and id(parent) not in visited and name is None:
            visited.add(id(parent))
            name = _logger_name(parent)
            parent = getattr(parent, "parent", None)
    return getLogger(name if name is not None else DEFAULT_LOG_NAME)


@contextmanager
def logger_context(obj):
    """Use the logger of obj for the objects without logger in the block

    Parameters
    ----------
    obj : object
        Object with a logger_name (a Simulation), read when a logger is
        requested
    """
    token = _CONTEXT.set(obj)
    try:
        yield obj
    finally:
        _CONTEXT.reset(token)
