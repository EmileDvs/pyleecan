# Experimental dataclass generated from Generator/ClassesRef/Import/Import.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass
from typing import ClassVar

from .._legacy_class import LegacyClass


@dataclass(eq=False)
class Import(LegacyClass):
    """Abstract class for Data Import/Generation

    Attributes
    ----------
    """

    _package: ClassVar[str] = "Import"
    """Name of the package of the legacy class module"""
