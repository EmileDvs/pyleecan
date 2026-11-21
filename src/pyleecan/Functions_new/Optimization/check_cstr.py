"""Deprecated alias of OptiGenAlgNsga2Deap.check_cstr (moved to the class, removed in Phase 2)."""

from warnings import warn


def check_cstr(obj, *args, **kwargs):
    """Deprecated: use OptiGenAlgNsga2Deap.check_cstr"""
    warn(
        "check_cstr is deprecated, use OptiGenAlgNsga2Deap.check_cstr (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    return obj.check_cstr(*args, **kwargs)
