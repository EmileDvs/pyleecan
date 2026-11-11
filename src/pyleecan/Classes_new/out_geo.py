# Experimental dataclass generated from Generator/ClassesRef/Output/OutGeo.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass, field

from ._pyleecan_class import PyleecanClass
from .data import Data
from .out_geo_lam import OutGeoLam


@dataclass(eq=False)
class OutGeo(PyleecanClass):
    """Gather the geometrical and the global outputs

    Attributes
    ----------
    stator : OutGeoLam or None
        Geometry output of the stator
        Default: None
    rotor : OutGeoLam or None
        Geometry output of the rotor
        Default: None
    Wgap_mec : float or None
        mechanical airgap width (minimal distance between the lamination including magnet)
        Unit: m; Default: None
    Wgap_mag : float or None
        the magnetic airgap width (distance beetween the two Laminations bore radius)
        Unit: m; Default: None
    Rgap_mec : float or None
        radius of the center of the mecanical airgap
        Unit: m; Default: None
    Lgap : float or None
        Airgap active length
        Unit: m; Default: None
    logger_name : str
        Name of the logger to use
        Default: "Pyleecan.OutGeo"
    angle_rotor_initial : float or None
        Difference between the d axis angle of the stator and the rotor
        Unit: rad; Default: None
    rot_dir : int or None
        Rotation direction of the rotor (rot_dir*N0, default value given by ROT_DIR_REF)
        Default: None; Minimum: -1; Maximum: 1
    per_a : int or None
        Number of spatial periodicities of the machine
        Default: None
    is_antiper_a : bool or None
        True if an spatial anti-periodicity is possible after the periodicities
        Default: None
    per_t_S : int or None
        Number of time periodicities of the machine in static referential
        Default: None
    is_antiper_t_S : bool or None
        True if an time anti-periodicity is possible after the periodicities in static referential
        Default: None
    axes_dict : {Data} or None
        Dict containing axes data without periodicities used for plots and to have simulation full time/angle vectors
        Default: None
    per_t_R : int or None
        Number of time periodicities of the machine in rotating referential
        Default: None
    is_antiper_t_R : bool or None
        True if an time anti-periodicity is possible after the periodicities in rotating referential
        Default: None
    """

    stator: OutGeoLam | None = field(
        default=None, metadata={"default_class": "OutGeoLam"}
    )
    """Geometry output of the stator"""
    rotor: OutGeoLam | None = field(
        default=None, metadata={"default_class": "OutGeoLam"}
    )
    """Geometry output of the rotor"""
    Wgap_mec: float | None = None
    """mechanical airgap width (minimal distance between the lamination including magnet)"""
    Wgap_mag: float | None = None
    """the magnetic airgap width (distance beetween the two Laminations bore radius)"""
    Rgap_mec: float | None = None
    """radius of the center of the mecanical airgap"""
    Lgap: float | None = None
    """Airgap active length"""
    logger_name: str = "Pyleecan.OutGeo"
    """Name of the logger to use"""
    angle_rotor_initial: float | None = None
    """Difference between the d axis angle of the stator and the rotor"""
    rot_dir: int | None = None
    """Rotation direction of the rotor (rot_dir*N0, default value given by ROT_DIR_REF)"""
    per_a: int | None = None
    """Number of spatial periodicities of the machine"""
    is_antiper_a: bool | None = None
    """True if an spatial anti-periodicity is possible after the periodicities"""
    per_t_S: int | None = None
    """Number of time periodicities of the machine in static referential"""
    is_antiper_t_S: bool | None = None
    """True if an time anti-periodicity is possible after the periodicities in static referential"""
    axes_dict: dict[str, Data] | None = None
    """Dict containing axes data without periodicities used for plots and to have simulation full time/angle vectors"""
    per_t_R: int | None = None
    """Number of time periodicities of the machine in rotating referential"""
    is_antiper_t_R: bool | None = None
    """True if an time anti-periodicity is possible after the periodicities in rotating referential"""
