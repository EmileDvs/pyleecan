# Experimental pydantic model generated from Generator/ClassesRef/Simulation/Drive.csv
"""Generated experimental pydantic model; do not edit by hand."""

from typing import ClassVar

from pydantic import Field

from .._legacy_model import LegacyModel


class Drive(LegacyModel):
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

    Umax: float = Field(default=800, ge=0, json_schema_extra={"unit": "V"})
    """Maximum RMS voltage of the Drive"""
    Imax: float = Field(default=800, ge=0, json_schema_extra={"unit": "A"})
    """Maximum RMS current of the Drive"""
    is_current: bool = False
    """True to generate current waveform, False for voltage"""

    _package: ClassVar[str] = "Simulation"
    """Name of the package of the legacy class module"""
