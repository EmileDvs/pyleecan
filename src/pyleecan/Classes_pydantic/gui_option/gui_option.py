# Experimental pydantic model generated from Generator/ClassesRef/GUI_Option/GUIOption.csv
"""Generated experimental pydantic model; do not edit by hand."""

from typing import ClassVar

from pydantic import Field

from .._legacy_model import LegacyModel
from .unit import Unit


class GUIOption(LegacyModel):
    """GUIOption

    Attributes
    ----------
    unit : Unit or None
        Unit options
        Default: Unit()
    """

    unit: Unit | None = Field(default_factory=lambda: Unit())
    """Unit options"""

    _package: ClassVar[str] = "GUIOption"
    """Name of the package of the legacy class module"""
