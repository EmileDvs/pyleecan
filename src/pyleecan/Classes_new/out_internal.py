# Experimental dataclass generated from Generator/ClassesRef/Output/OutInternal.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

from ._pyleecan_class import PyleecanClass
from .out_elec import OutElec
from .out_mag import OutMag


@dataclass(eq=False)
class OutInternal(PyleecanClass):
    """Abstract class whose childs enable to store outputs related to a specific model

    Attributes
    ----------
    """

    def __post_init__(self):
        super().__post_init__()

    def _assert_parent_type(self, parent):
        if parent is not None and not isinstance(
            parent,
            (
                OutElec,
                OutMag,
            ),
        ):
            raise TypeError(
                "OutInternal parent must be an instance of OutElec or OutMag, or None; "
                + f"got {type(parent).__name__}"
            )
