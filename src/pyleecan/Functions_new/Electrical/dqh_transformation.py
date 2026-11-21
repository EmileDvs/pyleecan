"""Deprecated alias of DataTime.n2dqh, DataTime.dqh2n (moved to the class, removed in Phase 2)."""

from warnings import warn


def n2dqh_DataTime(obj, *args, **kwargs):
    """Deprecated: use DataTime.n2dqh"""
    from ...Classes_new.scidatatool.data_time import DataTime

    warn(
        "n2dqh_DataTime is deprecated, use DataTime.n2dqh (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    return DataTime.n2dqh(obj, *args, **kwargs)


def dqh2n_DataTime(obj, *args, **kwargs):
    """Deprecated: use DataTime.dqh2n"""
    from ...Classes_new.scidatatool.data_time import DataTime

    warn(
        "dqh2n_DataTime is deprecated, use DataTime.dqh2n (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    return DataTime.dqh2n(obj, *args, **kwargs)


def n2dqh(*args, **kwargs):
    """Deprecated: use SciDataTool.dqh_transformation.n2dqh"""
    from ..SciDataTool.dqh_transformation import n2dqh as function

    warn(
        "n2dqh is deprecated, use SciDataTool.dqh_transformation.n2dqh (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    return function(*args, **kwargs)


def n2abc(*args, **kwargs):
    """Deprecated: use SciDataTool.dqh_transformation.n2abc"""
    from ..SciDataTool.dqh_transformation import n2abc as function

    warn(
        "n2abc is deprecated, use SciDataTool.dqh_transformation.n2abc (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    return function(*args, **kwargs)


def abc2dqh(*args, **kwargs):
    """Deprecated: use SciDataTool.dqh_transformation.abc2dqh"""
    from ..SciDataTool.dqh_transformation import abc2dqh as function

    warn(
        "abc2dqh is deprecated, use SciDataTool.dqh_transformation.abc2dqh (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    return function(*args, **kwargs)


def dqh2n(*args, **kwargs):
    """Deprecated: use SciDataTool.dqh_transformation.dqh2n"""
    from ..SciDataTool.dqh_transformation import dqh2n as function

    warn(
        "dqh2n is deprecated, use SciDataTool.dqh_transformation.dqh2n (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    return function(*args, **kwargs)


def abc2n(*args, **kwargs):
    """Deprecated: use SciDataTool.dqh_transformation.abc2n"""
    from ..SciDataTool.dqh_transformation import abc2n as function

    warn(
        "abc2n is deprecated, use SciDataTool.dqh_transformation.abc2n (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    return function(*args, **kwargs)


def dqh2abc(*args, **kwargs):
    """Deprecated: use SciDataTool.dqh_transformation.dqh2abc"""
    from ..SciDataTool.dqh_transformation import dqh2abc as function

    warn(
        "dqh2abc is deprecated, use SciDataTool.dqh_transformation.dqh2abc (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    return function(*args, **kwargs)


def comp_Clarke_transform(*args, **kwargs):
    """Deprecated: use SciDataTool.dqh_transformation.comp_Clarke_transform"""
    from ..SciDataTool.dqh_transformation import comp_Clarke_transform as function

    warn(
        "comp_Clarke_transform is deprecated, use SciDataTool.dqh_transformation.comp_Clarke_transform (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    return function(*args, **kwargs)


def get_phase_dir_DataTime(*args, **kwargs):
    """Deprecated: use SciDataTool.dqh_transformation.get_phase_dir_DataTime"""
    from ..SciDataTool.dqh_transformation import get_phase_dir_DataTime as function

    warn(
        "get_phase_dir_DataTime is deprecated, use SciDataTool.dqh_transformation.get_phase_dir_DataTime (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    return function(*args, **kwargs)


def get_phase_dir(*args, **kwargs):
    """Deprecated: use SciDataTool.dqh_transformation.get_phase_dir"""
    from ..SciDataTool.dqh_transformation import get_phase_dir as function

    warn(
        "get_phase_dir is deprecated, use SciDataTool.dqh_transformation.get_phase_dir (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    return function(*args, **kwargs)
