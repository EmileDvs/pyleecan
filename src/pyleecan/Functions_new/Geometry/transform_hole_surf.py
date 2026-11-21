"""Deprecated alias of Hole.transform_hole_surf (moved to the class, removed in Phase 2)."""

from warnings import warn


def transform_hole_surf(*args, **kwargs):
    """Deprecated: use Hole.transform_hole_surf"""
    from ...Classes_new.slot.hole import Hole

    warn(
        "transform_hole_surf is deprecated, use Hole.transform_hole_surf (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    return Hole.transform_hole_surf(*args, **kwargs)
