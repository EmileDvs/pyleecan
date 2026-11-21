"""Deprecated module: moved to utils.init_fig (removed in Phase 2)."""

from warnings import warn

from .utils.init_fig import copy_fig, init_fig, init_subplot

warn(
    "pyleecan.Functions.init_fig is deprecated, use pyleecan.Functions.utils.init_fig (removed in Phase 2)",
    DeprecationWarning,
    stacklevel=2,
)
