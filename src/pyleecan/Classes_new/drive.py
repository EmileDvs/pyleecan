# Experimental dataclass generated from Generator/ClassesRef/Simulation/Drive.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

from ._pyleecan_class import PyleecanClass


@dataclass(eq=False)
class Drive(PyleecanClass):
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

    Umax: float = 800
    """Maximum RMS voltage of the Drive"""
    Imax: float = 800
    """Maximum RMS current of the Drive"""
    is_current: bool = False
    """True to generate current waveform, False for voltage"""

    def __post_init__(self):
        super().__post_init__()
