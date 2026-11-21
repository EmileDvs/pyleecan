"""Deprecated alias of Data.animate_as_gif (moved to the class, removed in Phase 2)."""

from warnings import warn


def animate_as_gif(*args, **kwargs):
    """Deprecated: use Data.animate_as_gif"""
    from ...Classes_pydantic.scidatatool.data import Data

    warn(
        "animate_as_gif is deprecated, use Data.animate_as_gif (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    return Data.animate_as_gif(*args, **kwargs)
