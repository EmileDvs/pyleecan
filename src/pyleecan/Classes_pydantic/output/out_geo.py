# Experimental pydantic model generated from Generator/ClassesRef/Output/OutGeo.csv
"""Generated experimental pydantic model; do not edit by hand."""

from typing import ClassVar

from pydantic import Field

from .._pyleecan_model import PyleecanModel
from ..scidatatool.data import Data
from .out_geo_lam import OutGeoLam


class OutGeo(PyleecanModel):
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

    stator: OutGeoLam | None = None
    """Geometry output of the stator"""
    rotor: OutGeoLam | None = None
    """Geometry output of the rotor"""
    Wgap_mec: float | None = Field(default=None, json_schema_extra={"unit": "m"})
    """mechanical airgap width (minimal distance between the lamination including magnet)"""
    Wgap_mag: float | None = Field(default=None, json_schema_extra={"unit": "m"})
    """the magnetic airgap width (distance beetween the two Laminations bore radius)"""
    Rgap_mec: float | None = Field(default=None, json_schema_extra={"unit": "m"})
    """radius of the center of the mecanical airgap"""
    Lgap: float | None = Field(default=None, json_schema_extra={"unit": "m"})
    """Airgap active length"""
    logger_name: str = "Pyleecan.OutGeo"
    """Name of the logger to use"""
    angle_rotor_initial: float | None = Field(
        default=None, json_schema_extra={"unit": "rad"}
    )
    """Difference between the d axis angle of the stator and the rotor"""
    rot_dir: int | None = Field(default=None, ge=-1, le=1)
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

    _package: ClassVar[str] = "Output"
    """Name of the package of the legacy class module"""
