# Experimental dataclass generated from Generator/ClassesRef/Simulation/OPdqf.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass, field
from typing import ClassVar

from .op_dq import OPdq


@dataclass(eq=False)
class OPdqf(OPdq):
    """Operating Point defined in DQH frame for WRSM

    Attributes
    ----------
    If_ref : float or None
        DC rotor current
        Unit: Arms; Default: None
    """

    If_ref: float | None = field(default=None, metadata={"unit": "Arms"})
    """DC rotor current"""

    _package: ClassVar[str] = "Simulation"
    """Name of the package of the legacy class module"""
