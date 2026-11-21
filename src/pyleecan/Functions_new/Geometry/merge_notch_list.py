"""Deprecated alias of Lamination.merge_notch_list (moved to the class, removed in Phase 2)."""

from warnings import warn


def merge_notch_list(*args, **kwargs):
    """Deprecated: use Lamination.merge_notch_list"""
    from ...Classes_new.machine.lamination import Lamination

    warn(
        "merge_notch_list is deprecated, use Lamination.merge_notch_list (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    return Lamination.merge_notch_list(*args, **kwargs)


from ...classes_common.errors import NotchError  # noqa: F401, E402
