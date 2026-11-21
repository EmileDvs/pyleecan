"""Deprecated alias of Output.get_frame_meshsolution (moved to the class, removed in Phase 2)."""

from warnings import warn


def get_frame_meshsolution(obj, *args, **kwargs):
    """Deprecated: use Output.get_frame_meshsolution"""
    warn(
        "get_frame_meshsolution is deprecated, use Output.get_frame_meshsolution (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    return obj.get_frame_meshsolution(*args, **kwargs)
