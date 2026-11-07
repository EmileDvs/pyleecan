# Experimental dataclass generated from Generator/ClassesRef/Simulation/SliceModel.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass, field
from typing import Any

import numpy as np
from scipy.stats import norm

from ..Functions.Plot import dict_2D
from ..Functions.SciDataTool.Plot.plot_2D import plot_2D
from ._pyleecan_class import PyleecanClass
from .data_pattern import DataPattern
from .magnetics import Magnetics
from .norm_ref import NormRef
from .out_mag import OutMag


@dataclass(eq=False)
class SliceModel(PyleecanClass):
    """Class to hande slices in magnetics model

    Attributes
    ----------
    type_distribution : str or None
        Type of slice distribution to use for rotor skew if linear and continuous ("uniform", "gauss", "user-defined")
        Default: None
    Nslices : int
        Number of slices
        Default: 5
    z_list : list or None
        List of slice positions
        Unit: m; Default: []
    angle_rotor : ndarray or None
        Array of rotor skew angles in case of skew
        Unit: rad; Default: None
    angle_stator : ndarray or None
        Array of stator skew angles in case of skew
        Unit: rad; Default: None
    L : float or None
        Machine length (mean of rotor/stator lengths)
        Unit: m; Default: None
    is_step : bool or None
        True to define slices as steps
        Default: None
    is_skew : bool or None
        True if slices account for skew
        Default: None
    """

    type_distribution: str | None = None
    """Type of slice distribution to use for rotor skew if linear and continuous ("uniform", "gauss", "user-defined")"""
    Nslices: int = 5
    """Number of slices"""
    z_list: list[Any] | None = field(default_factory=list)
    """List of slice positions"""
    angle_rotor: np.ndarray | None = None
    """Array of rotor skew angles in case of skew"""
    angle_stator: np.ndarray | None = None
    """Array of stator skew angles in case of skew"""
    L: float | None = None
    """Machine length (mean of rotor/stator lengths)"""
    is_step: bool | None = None
    """True to define slices as steps"""
    is_skew: bool | None = None
    """True if slices account for skew"""

    def __post_init__(self):
        super().__post_init__()

    def _assert_parent_type(self, parent):
        if parent is not None and not isinstance(
            parent,
            (
                Magnetics,
                OutMag,
            ),
        ):
            raise TypeError(
                "SliceModel parent must be an instance of Magnetics or OutMag, or None; "
                + f"got {type(parent).__name__}"
            )

    # Inlined from Methods.Simulation.SliceModel.get_data
    def get_data(self):
        """Return the slice data object

        Parameters
        ----------
        self : SliceModel
            a SliceModel object

        Returns
        -------
        Slice: DataPattern
            Slice axis

        """

        # Get all z values
        values_whole = np.array(self.z_list)

        # Keep only unique values of relative skew between stator and rotor
        (_, unique_indices, rebuild_indices) = np.unique(
            (self.angle_stator - self.angle_rotor).round(decimals=4),
            return_index=True,
            return_inverse=True,
        )
        values = values_whole[unique_indices]
        unique_indices = unique_indices.tolist()
        rebuild_indices = rebuild_indices.tolist()

        # Setup other parameters
        normalizations = {"x L": NormRef(ref=self.L)}
        is_step = self.is_step

        # Create DataPattern
        Slice = DataPattern(
            name="z",
            unit="m",
            values=values,
            rebuild_indices=rebuild_indices,
            unique_indices=unique_indices,
            values_whole=values_whole,
            is_step=is_step,
            normalizations=normalizations,
        )

        return Slice

    # Inlined from Methods.Simulation.SliceModel.get_distribution
    def get_distribution(self):
        """Returns the slice distribution

        Parameters
        ----------
        self : SliceModel
            a SliceModel object

        Returns
        -------
        z_list : list
            list of slice positions (to be multiplied by lamination length)
        """

        if self.Nslices == 1:
            z_list = [0]

        else:
            type_distribution = self.type_distribution

            if type_distribution not in ["uniform", "gauss", "user-defined"]:
                raise InputError(
                    "Unknow skew slice distribution: "
                    + type_distribution
                    + ". Choose from "
                    "uniform"
                    ", "
                    "gauss"
                    " or "
                    "user-defined"
                    ""
                )

            if type_distribution == "uniform":
                z_list = np.linspace(-0.5, 0.5, self.Nslices).tolist()

            elif type_distribution == "gauss":
                Npoints = self.Nslices
                if Npoints % 2 == 0:
                    x = np.linspace(-1, 0, int(Npoints))
                    dist = norm.pdf(x, 0, 1)
                    # Rescale so that max = 0.5
                    dist = dist / (1 / np.sqrt(2 * np.pi) - dist[0]) * 0.5
                    dist_list = (dist - dist[-1]).tolist()
                    z_list = [z for (i, z) in enumerate(dist_list) if i % 2 == 0]
                    z_list = z_list + [-z for z in reversed(z_list)]
                else:
                    x = np.linspace(-1, 0, int((Npoints + 1) / 2))
                    dist = norm.pdf(x, 0, 1)
                    # Rescale so that max = 0.5
                    dist = dist / (1 / np.sqrt(2 * np.pi) - dist[0]) * 0.5
                    z_list = (dist - dist[-1]).tolist()
                    z_list = z_list[:-1] + [-z for z in reversed(z_list)]

            elif type_distribution == "user-defined":
                if self.z_list is None:
                    raise InputError(
                        "Missing z_list for skew user-defined slice distribution"
                    )
                for z in self.z_list:
                    if z < -0.5 or z > 0.5:
                        raise InputError(
                            "In skew model with user-defined distribution: z_list should be distributed between -0.5 and 0.5"
                        )
                z_list = self.z_list

        return z_list

    # Inlined from Methods.Simulation.SliceModel.plot
    def plot(
        self,
        skew_axis=None,
        fig=None,
        ax=None,
        lam_name="",
        is_show_fig=False,
        save_path=None,
        win_title=None,
    ):
        """Plots skew angle

        Parameters
        ----------
        self : Skew
            a Skew object

        """

        angle_list, z_list = self.comp_pattern()

        plot_2D(
            [z_list],
            [[a * 180 / np.pi for a in angle_list]],
            xlabel="Axial direction [m]",
            ylabel=lam_name + " skew angle [°]",
            type_plot="curve_point",
            fig=fig,
            ax=ax,
            is_show_fig=is_show_fig,
            save_path=save_path,
            win_title=win_title,
            **dict_2D,
        )

    class InputError(Exception):
        """Raised when the input data are incomplete or incorrect"""


InputError = SliceModel.InputError
