"""Deprecated alias of Conductor.comp_cond_function (moved to the class, removed in Phase 2)."""

from warnings import warn


def comp_cond_function(*args, **kwargs):
    """Deprecated: use Conductor.comp_cond_function"""
    from ...Classes_pydantic.machine.conductor import Conductor

    warn(
        "comp_cond_function is deprecated, use Conductor.comp_cond_function (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    return Conductor.comp_cond_function(*args, **kwargs)
