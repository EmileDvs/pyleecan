"""Deprecated alias of OptiGenAlgNsga2Deap.evaluate (moved to the class, removed in Phase 2)."""

from warnings import warn


def evaluate(obj, *args, **kwargs):
    """Deprecated: use OptiGenAlgNsga2Deap.evaluate"""
    warn(
        "evaluate is deprecated, use OptiGenAlgNsga2Deap.evaluate (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    return obj.evaluate(*args, **kwargs)
