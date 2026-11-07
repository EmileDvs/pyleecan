# Experimental dataclass generated from Generator/ClassesRef/Simulation/OPdqf.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

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

    If_ref: float | None = None
    """DC rotor current"""
