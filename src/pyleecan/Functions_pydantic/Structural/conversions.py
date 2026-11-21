"""Deprecated aliases (merged into SciDataTool.conversions, removed in Phase 2)."""

from warnings import warn

from ...classes_common.errors import DimError  # noqa: F401


def xyz_to_rphiz(*args, **kwargs):
    """Deprecated: use SciDataTool.conversions.xyz_to_rphiz"""
    from ..SciDataTool.conversions import xyz_to_rphiz as function

    warn(
        "xyz_to_rphiz is deprecated, use SciDataTool.conversions.xyz_to_rphiz (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    return function(*args, **kwargs)


def rphiz_to_xyz(*args, **kwargs):
    """Deprecated: use SciDataTool.conversions.rphiz_to_xyz_3d"""
    from ..SciDataTool.conversions import rphiz_to_xyz_3d as function

    warn(
        "rphiz_to_xyz is deprecated, use SciDataTool.conversions.rphiz_to_xyz_3d (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    return function(*args, **kwargs)


def xyz_to_rphiz_field(*args, **kwargs):
    """Deprecated: use SciDataTool.conversions.xyz_to_rphiz_field"""
    from ..SciDataTool.conversions import xyz_to_rphiz_field as function

    warn(
        "xyz_to_rphiz_field is deprecated, use SciDataTool.conversions.xyz_to_rphiz_field (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    return function(*args, **kwargs)


def rphiz_to_xyz_field(*args, **kwargs):
    """Deprecated: use SciDataTool.conversions.rphiz_to_xyz_field"""
    from ..SciDataTool.conversions import rphiz_to_xyz_field as function

    warn(
        "rphiz_to_xyz_field is deprecated, use SciDataTool.conversions.rphiz_to_xyz_field (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    return function(*args, **kwargs)


def cart2pol(*args, **kwargs):
    """Deprecated: use SciDataTool.conversions.cart2pol_points"""
    from ..SciDataTool.conversions import cart2pol_points as function

    warn(
        "cart2pol is deprecated, use SciDataTool.conversions.cart2pol_points (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    return function(*args, **kwargs)


def pol2cart(*args, **kwargs):
    """Deprecated: use SciDataTool.conversions.pol2cart_points"""
    from ..SciDataTool.conversions import pol2cart_points as function

    warn(
        "pol2cart is deprecated, use SciDataTool.conversions.pol2cart_points (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    return function(*args, **kwargs)
