"""Deprecated alias of Winding.reverse_wind_mat, Winding.reverse_layer, Winding.change_layer, Winding.permute_B_C (moved to the class, removed in Phase 2)."""

from warnings import warn


def reverse_wind_mat(*args, **kwargs):
    """Deprecated: use Winding.reverse_wind_mat"""
    from ...Classes_new.machine.winding import Winding

    warn(
        "reverse_wind_mat is deprecated, use Winding.reverse_wind_mat (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    return Winding.reverse_wind_mat(*args, **kwargs)


def reverse_layer(*args, **kwargs):
    """Deprecated: use Winding.reverse_layer"""
    from ...Classes_new.machine.winding import Winding

    warn(
        "reverse_layer is deprecated, use Winding.reverse_layer (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    return Winding.reverse_layer(*args, **kwargs)


def change_layer(*args, **kwargs):
    """Deprecated: use Winding.change_layer"""
    from ...Classes_new.machine.winding import Winding

    warn(
        "change_layer is deprecated, use Winding.change_layer (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    return Winding.change_layer(*args, **kwargs)


def permute_B_C(*args, **kwargs):
    """Deprecated: use Winding.permute_B_C"""
    from ...Classes_new.machine.winding import Winding

    warn(
        "permute_B_C is deprecated, use Winding.permute_B_C (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    return Winding.permute_B_C(*args, **kwargs)
