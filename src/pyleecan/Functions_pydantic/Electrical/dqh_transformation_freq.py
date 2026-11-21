"""Deprecated alias of DataFreq.n2dqh, DataFreq.dqh2n (moved to the class, removed in Phase 2)."""

from warnings import warn


def n2dqh_DataFreq(obj, *args, **kwargs):
    """Deprecated: use DataFreq.n2dqh"""
    from ...Classes_pydantic.scidatatool.data_freq import DataFreq

    warn(
        "n2dqh_DataFreq is deprecated, use DataFreq.n2dqh (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    return DataFreq.n2dqh(obj, *args, **kwargs)


def dqh2n_DataFreq(obj, *args, **kwargs):
    """Deprecated: use DataFreq.dqh2n"""
    from ...Classes_pydantic.scidatatool.data_freq import DataFreq

    warn(
        "dqh2n_DataFreq is deprecated, use DataFreq.dqh2n (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    return DataFreq.dqh2n(obj, *args, **kwargs)


def n2dqh(*args, **kwargs):
    """Deprecated: use SciDataTool.dqh_transformation.n2dqh_freq"""
    from ..SciDataTool.dqh_transformation import n2dqh_freq as function

    warn(
        "n2dqh is deprecated, use SciDataTool.dqh_transformation.n2dqh_freq (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    return function(*args, **kwargs)


def abc2dqh(*args, **kwargs):
    """Deprecated: use SciDataTool.dqh_transformation.abc2dqh_freq"""
    from ..SciDataTool.dqh_transformation import abc2dqh_freq as function

    warn(
        "abc2dqh is deprecated, use SciDataTool.dqh_transformation.abc2dqh_freq (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    return function(*args, **kwargs)


def dqh2n(*args, **kwargs):
    """Deprecated: use SciDataTool.dqh_transformation.dqh2n_freq"""
    from ..SciDataTool.dqh_transformation import dqh2n_freq as function

    warn(
        "dqh2n is deprecated, use SciDataTool.dqh_transformation.dqh2n_freq (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    return function(*args, **kwargs)


def dqh2abc(*args, **kwargs):
    """Deprecated: use SciDataTool.dqh_transformation.dqh2abc_freq"""
    from ..SciDataTool.dqh_transformation import dqh2abc_freq as function

    warn(
        "dqh2abc is deprecated, use SciDataTool.dqh_transformation.dqh2abc_freq (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    return function(*args, **kwargs)


def get_phase_dir_DataFreq(*args, **kwargs):
    """Deprecated: use SciDataTool.dqh_transformation.get_phase_dir_DataFreq"""
    from ..SciDataTool.dqh_transformation import get_phase_dir_DataFreq as function

    warn(
        "get_phase_dir_DataFreq is deprecated, use SciDataTool.dqh_transformation.get_phase_dir_DataFreq (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    return function(*args, **kwargs)


def get_phase_dir(*args, **kwargs):
    """Deprecated: use SciDataTool.dqh_transformation.get_phase_dir_freq"""
    from ..SciDataTool.dqh_transformation import get_phase_dir_freq as function

    warn(
        "get_phase_dir is deprecated, use SciDataTool.dqh_transformation.get_phase_dir_freq (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    return function(*args, **kwargs)
