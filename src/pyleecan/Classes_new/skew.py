# Experimental dataclass generated from Generator/ClassesRef/Machine/Skew.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass, field
from typing import Any, Callable

import numpy as np

from ..Functions.load import import_class
from ..Functions.Plot import dict_2D
from ..Functions.SciDataTool.Plot.plot_2D import plot_2D
from ._pyleecan_class import PyleecanClass
from .lamination import Lamination

TYPE_SKEW_LIST = ["linear", "vshape", "zig-zag", "user-defined", "function"]


@dataclass(eq=False)
class Skew(PyleecanClass):
    """Class for the skew (rotor or stator)

    Attributes
    ----------
    type_skew : str or None
        Type of skew ("linear", "vshape", "function", "user-defined")
        Default: None
    rate : float
        Skew rate expressed in terms of slot pitch (stator slot pitch for SCIM, rotor slot pitch for PMSM)
        Default: 1
    is_step : bool
        True to define skew as steps
        Default: True
    function : function or None
        Function which describes skew pattern
        Default: None
    angle_list : list or None
        List of skew angles
        Unit: rad; Default: []
    z_list : list or None
        List of z axis positions for which skew angles are given
        Unit: m; Default: []
    Nstep : int or None
        Number of steps if step skew
        Default: None; Minimum: 2
    angle_overall : float or None
        Overall skewing angle
        Unit: rad; Default: None; Minimum: 0
    """

    type_skew: str | None = None
    """Type of skew ("linear", "vshape", "function", "user-defined")"""
    rate: float = 1
    """Skew rate expressed in terms of slot pitch (stator slot pitch for SCIM, rotor slot pitch for PMSM)"""
    is_step: bool = True
    """True to define skew as steps"""
    function: Callable[..., Any] | None = None
    """Function which describes skew pattern"""
    angle_list: list[Any] | None = field(default_factory=list)
    """List of skew angles"""
    z_list: list[Any] | None = field(default_factory=list)
    """List of z axis positions for which skew angles are given"""
    Nstep: int | None = None
    """Number of steps if step skew"""
    angle_overall: float | None = None
    """Overall skewing angle"""

    def __post_init__(self):
        super().__post_init__()

    def _assert_parent_type(self, parent):
        if parent is not None and not isinstance(parent, (Lamination,)):
            raise TypeError(
                "Skew parent must be an instance of Lamination, or None; "
                + f"got {type(parent).__name__}"
            )

    # Inlined from Methods.Machine.Skew.comp_angle
    def comp_angle(self):
        """Compute skew angles and positions
        Parameters
        ----------
        self : Skew
            a Skew object
        """

        logger = self.get_logger()

        if self.parent is None:
            raise Exception(
                "ERROR: The Skew object must be in a Lamination object to run"
            )

        L = self.parent.comp_length()
        rate = self.rate
        angle_overall = self.angle_overall
        is_step = self.is_step
        type_skew = self.type_skew
        Nstep = self.Nstep
        z_list = self.z_list
        angle_list = self.angle_list

        if "PMSM" in self.parent.parent.get_machine_type():
            Z = self.parent.parent.stator.get_Zs()
        else:
            Z = self.parent.parent.rotor.get_Zs()

        sp = 2 * np.pi / Z

        if rate is None and angle_overall is None:
            # Set rate value by default
            logger.info("Skew rate is " + str(rate) + ", setting it to 1 by default")
            rate = 1

        elif angle_overall is None:
            # Calculate overall angle from skew rate
            angle_overall = rate * sp

        elif rate is None:
            # Calculate skew rate from overall angle
            rate = angle_overall / sp

        elif abs(angle_overall - rate * sp) > 1e-4:
            raise Exception(
                "Input skew rate and angle_overall does not fulfill constraint: angle_overall=rate*slot_pitch"
            )

        # Continuous skew
        if is_step:
            if type_skew in TYPE_SKEW_LIST and type_skew != "user-defined":
                if Nstep in [None, 0, 1]:
                    raise Exception(
                        "Number of steps= "
                        + str(Nstep)
                        + " must be defined and > 1 for stepped skew of type: "
                        + str(type_skew)
                    )

                z_list = np.linspace(-0.5, 0.5, Nstep + 1)

                if type_skew == "linear" or Nstep == 2:
                    angle_list = np.linspace(
                        -angle_overall / 2, angle_overall / 2, Nstep
                    )

                elif type_skew == "vshape":
                    Nhalf = int(np.floor((Nstep + 1) / 2))

                    angles_half = np.linspace(-angle_overall, 0, Nhalf)

                    if Nstep % 2 == 0:
                        angle_list = np.concatenate((angles_half, np.flip(angles_half)))
                    else:
                        angle_list = np.concatenate(
                            (angles_half[:-1], np.flip(angles_half))
                        )

                elif type_skew == "zig-zag":
                    angle_list = 0.5 * angle_overall * (-1) ** np.arange(Nstep)

                elif type_skew == "function":
                    if self.function is None:
                        raise Exception(
                            "Function must be defined if type_skew == function"
                        )
                    try:
                        angle_list = self.function(np.array(z_list))
                    except Exception:
                        raise Exception("Error in skew function definition")

                # Put average skew angle to zero
                angle_list = list(np.array(angle_list) - np.mean(angle_list))

            elif type_skew == "user-defined":
                if angle_list is None:
                    raise Exception(
                        "angle_list not provided for user-defined stepped skew"
                    )

                Nstep = len(angle_list)

                if z_list is None:
                    # Init as linear skew type
                    z_list = np.linspace(-0.5, 0.5, Nstep + 1)

                else:
                    if len(angle_list) != len(z_list) - 1:
                        raise Exception(
                            "angle_list must have one element less than z_list for user-defined stepped skew"
                        )

                    if z_list[0] != -0.5:
                        raise Exception(
                            "First coordinate in z_list must be -0.5 (x L) for user-defined stepped skew"
                        )

                    if 0.5 in z_list:
                        raise Exception(
                            "0.5 (x L) must not be in z_list for user-defined stepped skew"
                        )

            else:
                raise Exception("Unknown stepped-skew type: " + self.type_skew)

        else:
            if type_skew == "linear":
                Nstep = 2
                z_list = np.linspace(-0.5, 0.5, Nstep)
                angle_list = [z * angle_overall for z in z_list]

            else:
                raise Exception("Only linear skew is available for continuous skew")

        # Store z_list in absolute value
        z_list = [z * L for z in z_list]

        self.rate = rate
        self.angle_overall = angle_overall
        self.Nstep = Nstep
        self.angle_list = angle_list
        self.z_list = z_list

    # Inlined from Methods.Machine.Skew.comp_pattern
    def comp_pattern(self, is_reverse_z=False, is_reverse_angle=False):
        """Compute skew pattern by duplicating points in case of stepped skew

        Parameters
        ----------
        self : Skew
            a Skew object
        is_reverse_z : bool
            True to reverse slice position
        is_reverse_angle : bool
            True to reverse slice angle

        Returns
        -------
        angle_list : list
            list of skew angles
        z_list : list
            list of slice positions

        """

        if self.angle_list is None or self.z_list is None:
            self.comp_angle()

        is_step = self.is_step
        z_list = self.z_list
        angle_list = self.angle_list

        if is_step:
            # Duplicate points at z_start and z_end of each segment
            angle_list_new = [angle_list[0]]
            z_list_new = []
            for i, z in enumerate(z_list[:-1]):
                # Duplicate z_start and z_end
                z_list_new += [z, z_list[i + 1]]
                if i < len(angle_list) - 1:
                    # If it is not the last segment
                    # Assign skew angle value at z_start and z_end
                    angle_list_new += [angle_list[i], angle_list[i + 1]]
                elif i < len(angle_list):
                    # If it is the last segment
                    # Only assign skew angle value to last point
                    angle_list_new.append(angle_list[i])

        else:
            # Return points as they are
            angle_list_new = angle_list
            z_list_new = z_list

        if is_reverse_z:
            angle_list_new = list(reversed(angle_list_new))

        if is_reverse_angle:
            angle_list_new = [-a for a in angle_list_new]

        return angle_list_new, z_list_new

    # Inlined from Methods.Machine.Skew.plot
    def plot(
        self,
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

        legend_list = ["Skew pattern"]
        y_list = [[a * 180 / np.pi for a in angle_list]]
        linestyle_list = ["solid"]

        LamSlotM = import_class("pyleecan.Classes", "LamSlotM")
        LamH = import_class("pyleecan.Classes", "LamH")

        if isinstance(self.parent, (LamSlotM, LamH)):
            legend_list.append("Rotor d-axis")
            y_list.append([0 for z in z_list])
            linestyle_list.append("dashed")

        plot_2D(
            [z_list],
            y_list,
            xlabel="Axial direction from Non Drive End to Drive End [m]",
            ylabel=lam_name + " skew angle [°]",
            type_plot="curve_point",
            fig=fig,
            ax=ax,
            is_show_fig=is_show_fig,
            save_path=save_path,
            win_title=win_title,
            legend_list=legend_list,
            linestyle_list=linestyle_list,
            **dict_2D,
        )
