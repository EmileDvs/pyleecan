# Experimental dataclass generated from Generator/ClassesRef/Simulation/Drive.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass, field
from typing import ClassVar

from .._legacy_class import LegacyClass


@dataclass(eq=False)
class Drive(LegacyClass):
    """Abstract Drive class

    Attributes
    ----------
    Umax : float
        Maximum RMS voltage of the Drive
        Unit: V; Default: 800; Minimum: 0
    Imax : float
        Maximum RMS current of the Drive
        Unit: A; Default: 800; Minimum: 0
    is_current : bool
        True to generate current waveform, False for voltage
        Default: False
    """

    Umax: float = field(default=800, metadata={"unit": "V", "min": 0})
    """Maximum RMS voltage of the Drive"""
    Imax: float = field(default=800, metadata={"unit": "A", "min": 0})
    """Maximum RMS current of the Drive"""
    is_current: bool = False
    """True to generate current waveform, False for voltage"""

    _package: ClassVar[str] = "Simulation"
    """Name of the package of the legacy class module"""
