"""Deprecated module: moved to utils.make_ndarray_equal (removed in Phase 2)."""

from warnings import warn

from .utils.make_ndarray_equal import make_ndarray_equal

warn(
    "pyleecan.Functions.make_ndarray_equal is deprecated, use pyleecan.Functions.utils.make_ndarray_equal (removed in Phase 2)",
    DeprecationWarning,
    stacklevel=2,
)
