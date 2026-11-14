# Experimental dataclass generated from Generator/ClassesRef/GUI_Option/GUIOption.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass, field
from typing import ClassVar

from ._pyleecan_class import PyleecanClass
from .unit import Unit


@dataclass(eq=False)
class GUIOption(PyleecanClass):
    """GUIOption

    Attributes
    ----------
    unit : Unit or None
        Unit options
        Default: Unit()
    """

    unit: Unit | None = field(
        default_factory=lambda: Unit(), metadata={"default_class": "Unit"}
    )
    """Unit options"""

    _package: ClassVar[str] = "GUIOption"
    """Name of the package of the legacy class module"""
