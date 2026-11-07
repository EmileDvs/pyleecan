# Experimental dataclass generated from Generator/ClassesRef/GUI_Option/GUIOption.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

from ._pyleecan_class import PyleecanClass
from .unit import Unit


@dataclass(eq=False)
class GUIOption(PyleecanClass):
    """GUIOption

    Attributes
    ----------
    unit : Unit or None
        Unit options
        Default: None
    """

    unit: Unit | None = None
    """Unit options"""

    def __post_init__(self):
        super().__post_init__()
