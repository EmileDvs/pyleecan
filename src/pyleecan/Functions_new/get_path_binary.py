"""Deprecated module: moved to utils.get_path_binary (removed in Phase 2)."""

from warnings import warn

from .utils.get_path_binary import get_path_binary

warn(
    "pyleecan.Functions.get_path_binary is deprecated, use pyleecan.Functions.utils.get_path_binary (removed in Phase 2)",
    DeprecationWarning,
    stacklevel=2,
)
