"""Retrocompatibility of the pyleecan files with the classes of this backend
(shared implementation: classes_common.retrocompatibility)."""

from ...classes_common import retrocompatibility as _common
from ...classes_common.retrocompatibility import (  # noqa: F401
    NORMALIZATION_CLASS_NAMES,
    OBJECT_VERSION_DICT,
    OP_MAT_VERSION,
    OP_VERSION,
    VARPARAM_VERSION,
    WIND_VERSION,
    _search_and_update,
    convert_HoleUD,
    convert_meshsolution_mesh,
    convert_normalization,
    convert_OP,
    convert_OP_matrix,
    convert_opticonstraint,
    convert_optidesignvar,
    convert_Winding,
    convert_Wmag_Hmag,
    create_update_dict,
    is_before_version,
    is_HoleUD_dict,
    is_MeshSolution_dict,
    is_OP_dict,
    is_OP_matrix_dict,
    is_OptiConstraint_dict,
    is_OptiDesignVar_dict,
    is_VarParam_dict,
    is_Winding_dict,
    is_Wmag_Hmag,
    is_yoke_notch,
    move_yoke_notch,
    rename_varparam,
)
from ...Classes_new._import import import_class


def convert_init_dict(init_dict):
    """Convert an init_dict from an old version of pyleecan to the current one
    (modification in place)

    Parameters
    ----------
    init_dict : dict
        The dictionnary to update
    """
    _common.convert_init_dict(init_dict, import_class=import_class)
