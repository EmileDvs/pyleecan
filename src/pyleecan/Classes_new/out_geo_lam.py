# Experimental dataclass generated from Generator/ClassesRef/Output/OutGeoLam.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass, field
from typing import Any

import numpy as np

from ._pyleecan_class import PyleecanClass


@dataclass(eq=False)
class OutGeoLam(PyleecanClass):
    """Gather the geometrical and the global outputs of a lamination

    Attributes
    ----------
    name_phase : list or None
        Name of the phases of the winding (if any)
        Default: []
    BH_curve : ndarray or None
        B(H) curve (two columns matrix, H and B(H))
        Default: None
    Ksfill : float or None
        Slot fill factor
        Default: None
    S_slot : float or None
        Slot surface
        Unit: m^2; Default: None
    S_slot_wind : float or None
        Slot winding surface
        Unit: m^2; Default: None
    S_wind_act : float or None
        Conductor active surface
        Unit: m^2; Default: None
    per_a : int or None
        Number of spatial periodicities of the lamination
        Default: None
    is_antiper_a : bool or None
        True if an spatial anti-periodicity is possible after the periodicities
        Default: None
    per_t : int or None
        Number of time periodicities of the lamination
        Default: None
    is_antiper_t : bool or None
        True if an time anti-periodicity is possible after the periodicities
        Default: None
    """

    name_phase: list[Any] | None = field(default_factory=list)
    """Name of the phases of the winding (if any)"""
    BH_curve: np.ndarray | None = None
    """B(H) curve (two columns matrix, H and B(H))"""
    Ksfill: float | None = None
    """Slot fill factor"""
    S_slot: float | None = None
    """Slot surface"""
    S_slot_wind: float | None = None
    """Slot winding surface"""
    S_wind_act: float | None = None
    """Conductor active surface"""
    per_a: int | None = None
    """Number of spatial periodicities of the lamination"""
    is_antiper_a: bool | None = None
    """True if an spatial anti-periodicity is possible after the periodicities"""
    per_t: int | None = None
    """Number of time periodicities of the lamination"""
    is_antiper_t: bool | None = None
    """True if an time anti-periodicity is possible after the periodicities"""
