"""Runtime information on the classes of this package.

Binding of the shared ``classes_common.class_info.ClassInfo`` to the classes of
this package.
"""

from ..classes_common.class_info import ClassInfo as _ClassInfo
from ._pyleecan_model import PyleecanModel

PYLEECAN_BASES = (PyleecanModel,)
"""Bases of the classes of this package"""


class ClassInfo(_ClassInfo):
    """Information on all the classes of this package (see the shared ClassInfo)."""

    def __init__(self):
        super().__init__(__package__)
