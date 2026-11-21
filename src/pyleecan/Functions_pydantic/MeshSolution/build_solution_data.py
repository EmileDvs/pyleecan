"""Deprecated alias of SolutionData.build_solution_data (moved to the class, removed in Phase 2)."""

from warnings import warn


def build_solution_data(*args, **kwargs):
    """Deprecated: use SolutionData.build_solution_data"""
    from ...Classes_pydantic.mesh.solution_data import SolutionData

    warn(
        "build_solution_data is deprecated, use SolutionData.build_solution_data (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    return SolutionData.build_solution_data(*args, **kwargs)
