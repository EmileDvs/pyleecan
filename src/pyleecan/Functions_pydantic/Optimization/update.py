"""Deprecated alias of OptiGenAlgNsga2Deap.update (moved to the class, removed in Phase 2)."""

from warnings import warn


def update(*args, **kwargs):
    """Deprecated: use OptiGenAlgNsga2Deap.update"""
    from ...Classes_pydantic.optimization.opti_gen_alg_nsga_2_deap import (
        OptiGenAlgNsga2Deap,
    )

    warn(
        "update is deprecated, use OptiGenAlgNsga2Deap.update (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    return OptiGenAlgNsga2Deap.update(*args, **kwargs)
