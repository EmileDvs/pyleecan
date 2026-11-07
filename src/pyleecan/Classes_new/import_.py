# Experimental dataclass generated from Generator/ClassesRef/Import/Import.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

from ._pyleecan_class import PyleecanClass
from .drive import Drive
from .import_data import ImportData


@dataclass(eq=False)
class Import(PyleecanClass):
    """Abstract class for Data Import/Generation

    Attributes
    ----------
    """

    def __post_init__(self):
        super().__post_init__()

    def _assert_parent_type(self, parent):
        if parent is not None and not isinstance(
            parent,
            (
                Drive,
                ImportData,
            ),
        ):
            raise TypeError(
                "Import parent must be an instance of Drive or ImportData, or None; "
                + f"got {type(parent).__name__}"
            )
