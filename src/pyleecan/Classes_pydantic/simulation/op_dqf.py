# Experimental pydantic model generated from Generator/ClassesRef/Simulation/OPdqf.csv
"""Generated experimental pydantic model; do not edit by hand."""

from typing import ClassVar

from pydantic import Field

from .op_dq import OPdq


class OPdqf(OPdq):
    """Operating Point defined in DQH frame for WRSM

    Attributes
    ----------
    If_ref : float or None
        DC rotor current
        Unit: Arms; Default: None
    """

    If_ref: float | None = Field(default=None, json_schema_extra={"unit": "Arms"})
    """DC rotor current"""

    _package: ClassVar[str] = "Simulation"
    """Name of the package of the legacy class module"""
