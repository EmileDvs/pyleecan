# File generated according to Generator/ClassesRef/Machine/LamSlotMultiWind.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Machine/LamSlotMultiWind"""

from os import linesep
from sys import getsizeof

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch
from pyleecan.Classes.WindingSC import WindingSC

from pyleecan.Classes._check import check_var
from pyleecan.Classes.LamSlot import LamSlot
from pyleecan.Classes.LamSlotMulti import LamSlotMulti
from pyleecan.definitions import config_dict
from pyleecan.Functions.get_logger import get_logger
from pyleecan.Functions.init_fig import init_fig
from pyleecan.Functions.labels import BAR_LAB, WIND_LAB, decode_label
from pyleecan.Functions.load import load_init_dict
from pyleecan.Functions.Load.import_class import import_class
from pyleecan.Functions.Plot.get_color_legend_from_surface import (
    get_color_legend_from_surface,
)
from pyleecan.Functions.save import save
from pyleecan.Functions.Winding.comp_cond_function import comp_cond_function
from pyleecan.Functions.Winding.find_wind_phase_color import find_wind_phase_color
from pyleecan.Functions.Winding.gen_phase_list import gen_name


class LamSlotMultiWind(LamSlotMulti):
    """Lamination with list of Slot filled with winding"""

    VERSION = 1
    PHASE_COLORS = config_dict["PLOT"]["COLOR_DICT"]["PHASE_COLORS"]

    # cf Methods.Machine.LamSlotMultiWind.build_geometry
    def build_geometry(self, sym=1, alpha=0, delta=0, is_circular_radius=False):
        """Build the geometry of the LamSlotMulti with winding in slots

        Parameters
        ----------
        self : LamSlotMultiWind
            A LamSlotMultiWind object
        alpha : float
            Angle for rotation [rad]
        delta : complex
            Complex value for translation
        is_circular_radius : bool
            True to add surfaces to "close" the Lamination radii

        Returns
        -------
        surf_list : list
            list of surfaces needed to draw the lamination

        """

        # getting the Lamination surface
        surf_lam = LamSlot.build_geometry(
            self,
            sym=sym,
            alpha=alpha,
            delta=delta,
            is_circular_radius=is_circular_radius,
        )

        # getting the winding surface
        surf_list = list()
        if self.slot_list is not None and self.slot_list[0].Zs != 0:
            if self.is_stator:
                st = "Stator"
            else:
                st = "Rotor"
            # getting angle between Slot
            angle = self.alpha
            # getting Nrad and Ntan
            if self.winding is None or self.winding.conductor is None:
                Nrad, Ntan = 1, 1
                surf_Wind = list()
            else:
                try:
                    Nrad, Ntan = self.winding.get_dim_wind()
                except Exception:
                    Nrad, Ntan = 1, 1

                for ii in range(int(len(angle) / sym)):  # for each slot
                    # get the winding surface
                    surf_Wind = self.slot_list[ii].build_geometry_active(
                        Nrad=Nrad,
                        Ntan=Ntan,
                        alpha=alpha,
                        delta=delta,
                    )

                    # for each part of the winding surface in the slot
                    for surf in surf_Wind:
                        new_surf = type(surf)(init_dict=surf.as_dict())
                        # changing the slot reference number
                        new_surf.label = surf.label[:-1] + str(ii)
                        new_surf.rotate(angle[ii])
                        surf_list.append(new_surf)

        surf_list = surf_lam + surf_list

        return surf_list

    # cf Methods.Machine.LamSlotMultiWind.comp_angle_d_axis
    def comp_angle_d_axis(self, is_plot=False):
        """Compute the angle between the X axis and the first d+ axis
        By convention a "Tooth" is centered on the X axis

        Parameters
        ----------
        self : LamSlotWind
            A LamSlotWind object
        is_plot : bool
            True to plot d axis position regarding unit mmf

        Returns
        -------
        d_angle : float
            angle between the X axis and the first d+ axis
        """

        # Call method of LamSlotWind
        LamSlotWind = import_class("pyleecan.Classes", "LamSlotWind")

        d_angle = LamSlotWind.comp_angle_d_axis(self, is_plot=is_plot)

        return d_angle

    # cf Methods.Machine.LamSlotMultiWind.comp_mmf_dir
    def comp_mmf_dir(self, current_dir=None, phase_dir=None, is_plot=False):
        """Compute the rotation direction of the fundamental magnetomotive force induced by the winding

        Parameters
        ----------
        self : LamSlotMultiWind
            A LamSlotMultiWind object
        felec : float
            Stator current frequency to consider
        current_dir: int
            Stator current rotation direction +/-1
        phase_dir: int
            Stator winding phasor rotation direction +/-1
        is_plot: bool
            True to plot fft2 of stator MMF

        Returns
        -------
        mmf_dir : int
            -1 or +1
        """

        # Call method of LamSlotWind
        LamSlotWind = import_class("pyleecan.Classes", "LamSlotWind")

        rot_dir = LamSlotWind.comp_mmf_dir(self, current_dir, phase_dir, is_plot)

        return rot_dir

    # cf Methods.Machine.LamSlotMultiWind.comp_mmf_unit
    def comp_mmf_unit(self, Na, Nt, felec=1, current_dir=None, phase_dir=None):
        """Compute the winding Unit magnetomotive force

        Parameters
        ----------
        self : LamSlotMultiWind
            an LamSlotMultiWind object
        Na : int
            Space discretization for offline computation (otherwise use out.elec.angle)
        Nt : int
            Time discretization for offline computation (otherwise use out.elec.time)
        felec : float
            Stator current frequency to consider
        current_dir: int
            Stator current rotation direction +/-1
        phase_dir: int
            Stator winding phasor rotation direction +/-1

        Returns
        -------
        MMF_U : DataND
            Unit magnetomotive force (Na,Nt)
        WF : DataND
            Winding functions (qs,Na)

        """

        # Call method of LamSlotWind
        LamSlotWind = import_class("pyleecan.Classes", "LamSlotWind")

        MMF_U, WF = LamSlotWind.comp_mmf_unit(
            self,
            Na=Na,
            Nt=Nt,
            felec=felec,
            current_dir=current_dir,
            phase_dir=phase_dir,
        )

        return MMF_U, WF

    # cf Methods.Machine.LamSlotMultiWind.comp_wind_function
    def comp_wind_function(self, angle=None, Na=2048, alpha_mmf0=0, per_a=1):
        """Computation of the winding function for the lamination.
        By convention a tooth is centered on the X axis

        Parameters
        ----------
        self : LamSlotMultiWind
            A LamSlotMultiWind object
        angle : ndarray
            Space discretization to compute the winding functions
        Na : int
            Number of angular points for the winding function (not used if angle is set)
        alpha_mmf0 : float
            Angle to shift the winding function (Default value = 0)
        per_a : int
            Spatial periodicity factor

        Returns
        -------
        wf: ndarray
            Winding function Matrix (qs,Na)
        """

        # Space discretization
        if angle is None:
            angle = np.linspace(0, np.pi * 2 / per_a, Na, endpoint=False)
        else:
            Na = angle.size

        qs = self.winding.qs  # number of phases
        # Number of point on rad and tan direction
        Nrad, Ntan = self.winding.get_dim_wind()
        Zs = self.get_Zs()  # Number of slot
        Zs0 = int(Zs / per_a)

        if self.sym_dict_enforced is not None:
            slot_list = self.slot_list[0:Zs0]
        else:
            slot_list = self.slot_list

        wind_mat = self.winding.get_connection_mat(Zs)
        # sum wind_mat along Nlay_rad axis
        wind_mat = np.sum(wind_mat, axis=0)

        # angle of the center of the slots
        # By convention a tooth is centered on the X axis
        alpha_slot = self.alpha[:Zs0]

        if alpha_mmf0 != 0:
            angle = (angle - alpha_mmf0) % (2 * np.pi)

        wf = np.zeros((qs, Na))
        for ii, slot in enumerate(slot_list):
            slot_angle = slot.comp_angle_active_eq()
            slot_opening = slot.comp_angle_opening()
            for n in range(Ntan):
                # [Na, Zs]
                alpha_lay = np.linspace(
                    -slot_angle / 2, slot_angle / 2, Ntan + 1, endpoint=False
                )[1:]
                Xalpha_slot, Xangle = np.meshgrid(alpha_slot[ii] + alpha_lay[n], angle)

                Xwind = np.zeros((1, Zs0, qs))
                Xwind[0, :, :] = wind_mat[n, 0:Zs0, :]
                # Extended winding matrix [Na, Zs, qs]
                Xwind = np.repeat(Xwind, Na, axis=0)
                # Single winding function in every slot and angle for nth layer [Na, Zs]
                Xwf = -0.5 * comp_cond_function(Xalpha_slot, slot_opening, Xangle)

                for q in range(qs):
                    wf[q, :] += np.sum(Xwind[n, ii, q] * Xwf, axis=1)

        if per_a > 1:
            wf = wf - np.mean(wf, axis=1)[:, None]

        return wf

    # cf Methods.Machine.LamSlotMultiWind.get_pole_pair_number
    def get_pole_pair_number(self):
        """Return the number of pair of pole of the Lamination

        Parameters
        ----------
        self : LamSlotMultiWind
            A LamSlotMultiWind object

        Returns
        -------
        p: int
            Number of pair of pole

        """

        if self.winding is not None:
            return self.winding.p
        else:
            return None

    # cf Methods.Machine.LamSlotMultiWind.plot
    def plot(
        self,
        fig=None,
        ax=None,
        is_lam_only=False,
        sym=1,
        alpha=0,
        delta=0,
        is_edge_only=False,
        edgecolor=None,
        is_add_arrow=False,
        is_display=True,
        is_add_sign=False,
        is_show_fig=True,
        save_path=None,
        win_title=None,
        is_winding_connection=False,
        *,
        PLUS_HATCH="++",
        MINUS_HATCH="..",
    ):
        """Plot the Lamination with empty Slots in a matplotlib fig

        Parameters
        ----------
        self : LamSlotMulti
            A LamSlotMulti object
        fig : Matplotlib.figure.Figure
            existing figure to use if None create a new one
        ax : Matplotlib.axes.Axes object
            Axis on which to plot the data
        is_lam_only: bool
            True to plot only the lamination
        sym : int
            Symmetry factor (1= full machine, 2= half of the machine...)
        alpha : float
            Angle for rotation [rad]
        delta : complex
            Complex value for translation
        is_edge_only: bool
            To plot transparent Patches
        edgecolor:
            Color of the edges if is_edge_only=True
        is_display : bool
            False to return the patches
        is_show_fig : bool
            To call show at the end of the method
        is_winding_connection : bool
            True to display winding connections (not used)

        Returns
        -------
        patches : list
            List of Patches
        fig : Matplotlib.figure.Figure
            Figure containing the plot
        ax : Matplotlib.axes.Axes object
            Axis containing the plot
        """

        (fig, ax, patch_leg, label_leg) = init_fig(fig=fig, ax=ax, shape="rectangle")

        # getting the number of phases and winding connection matrix
        if self.winding is not None:
            if isinstance(self.winding, WindingSC):  # plot only one phase for WindingSC
                wind_mat = None
                qs = 1
            else:
                try:
                    wind_mat = self.winding.get_connection_mat(self.get_Zs())
                    qs = self.winding.qs
                except:
                    wind_mat = None
                    qs = 1
        else:
            wind_mat = None
            qs = 1

        # Get the LamSlot surface(s)
        surf_list = self.build_geometry(sym=sym, alpha=alpha, delta=delta)
        patches = list()
        for surf in surf_list:
            label_dict = decode_label(surf.label)
            if (
                WIND_LAB in label_dict["surf_type"]
                or BAR_LAB in label_dict["surf_type"]
            ):
                if not is_lam_only:
                    color, sign = find_wind_phase_color(
                        wind_mat=wind_mat, label=surf.label
                    )
                    if sign == "+" and is_add_sign:
                        hatch = PLUS_HATCH
                    elif sign == "-" and is_add_sign:
                        hatch = MINUS_HATCH
                    else:
                        hatch = None
                    patches.extend(
                        surf.get_patches(
                            color=color,
                            is_edge_only=is_edge_only,
                            hatch=hatch,
                            edgecolor=edgecolor,
                        )
                    )
            else:
                color, legend = get_color_legend_from_surface(surf, is_lam_only)

                if color is not None:
                    patches.extend(
                        surf.get_patches(
                            color=color,
                            is_edge_only=is_edge_only,
                            edgecolor=edgecolor,
                        )
                    )
                if not is_edge_only and legend is not None and legend not in label_leg:
                    label_leg.append(legend)
                    patch_leg.append(Patch(color=color))

        # Display the result
        if is_display:
            (fig, ax, patch_leg, label_leg) = init_fig(fig)
            ax.set_xlabel("(m)")
            ax.set_ylabel("(m)")
            for patch in patches:
                ax.add_patch(patch)

            # Axis Setup
            ax.axis("equal")

            # Window title
            if self.is_stator:
                prefix = "Stator "
            else:
                prefix = "Rotor "
            if (
                win_title is None
                and self.parent is not None
                and self.parent.name not in [None, ""]
            ):
                win_title = self.parent.name + " " + prefix[:-1]
            elif win_title is None:
                win_title = prefix[:-1]
            manager = plt.get_current_fig_manager()
            if manager is not None:
                manager.set_window_title(win_title)

            # The Lamination is centered in the figure
            Lim = self.Rext * 1.5
            ax.set_xlim(-Lim, Lim)
            ax.set_ylim(-Lim, Lim)

            # Add the legend
            if not is_edge_only:
                if self.is_stator and "Stator" not in label_leg:
                    ax.set_title("Stator with empty slot")
                elif not self.is_stator and "Rotor" not in label_leg:
                    ax.set_title("Rotor with Winding")
                # Add the winding legend only if needed
                if not is_lam_only:
                    if self.winding is not None:
                        phase_name = [
                            prefix + n for n in gen_name(qs, is_add_phase=True)
                        ]
                        for ii in range(qs):
                            if not phase_name[ii] in label_leg and not is_add_sign:
                                # Avoid adding twice the same label
                                index = ii % len(self.PHASE_COLORS)
                                patch_leg.append(Patch(color=self.PHASE_COLORS[index]))
                                label_leg.append(phase_name[ii])
                            if not "Phase +" in label_leg and is_add_sign:
                                # Avoid adding twice the same label
                                index = ii % len(self.PHASE_COLORS)
                                patch_leg.append(
                                    Patch(
                                        color=self.PHASE_COLORS[index], hatch=PLUS_HATCH
                                    )
                                )
                                label_leg.append(phase_name[ii] + " +")
                            if not "Phase -" in label_leg and is_add_sign:
                                # Avoid adding twice the same label
                                index = ii % len(self.PHASE_COLORS)
                                patch_leg.append(
                                    Patch(
                                        color=self.PHASE_COLORS[index],
                                        hatch=MINUS_HATCH,
                                    )
                                )
                                label_leg.append(phase_name[ii] + " -")
                ax.legend(patch_leg, label_leg)

            if save_path is not None:
                fig.savefig(save_path)
                plt.close(fig=fig)
            if is_show_fig:
                fig.show()
            return fig, ax
        else:
            return patches

    # cf Methods.Machine.LamSlotMultiWind.plot_mmf_unit
    def plot_mmf_unit(self, r_max=100, fig=None, save_path=None, is_show_fig=True):
        """Plot the winding unit mmf as a function of space
        Parameters
        ----------

        self : LamSlotMultiWind
            an LamSlotMultiWind object
        Na : int
            Space discretization
        fig : Matplotlib.figure.Figure
            existing figure to use if None create a new one
        is_show_fig : bool
            To call show at the end of the method
        """

        # Call method of LamSlotWind
        LamSlotWind = import_class("pyleecan.Classes", "LamSlotWind")

        LamSlotWind.plot_mmf_unit(
            self, r_max=r_max, fig=fig, save_path=save_path, is_show_fig=is_show_fig
        )

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
        Ksfill=None,
        winding=-1,
        slot_list=-1,
        alpha=None,
        sym_dict_enforced=None,
        L1=0.35,
        mat_type=-1,
        Nrvd=0,
        Wrvd=0,
        Kf1=0.95,
        is_internal=True,
        Rint=0,
        Rext=1,
        is_stator=True,
        axial_vent=-1,
        notch=-1,
        skew=None,
        bore=None,
        yoke=None,
        init_dict=None,
        init_str=None,
    ):
        """Constructor of the class. Can be use in three ways :
        - __init__ (arg1 = 1, arg3 = 5) every parameters have name and default values
            for pyleecan type, -1 will call the default constructor
        - __init__ (init_dict = d) d must be a dictionary with property names as keys
        - __init__ (init_str = s) s must be a string
        s is the file path to load

        ndarray or list can be given for Vector and Matrix
        object or dict can be given for pyleecan Object"""

        if init_str is not None:  # Load from a file
            init_dict = load_init_dict(init_str)[1]
        if init_dict is not None:  # Initialisation by dict
            assert type(init_dict) is dict
            # Overwrite default value with init_dict content
            if "Ksfill" in list(init_dict.keys()):
                Ksfill = init_dict["Ksfill"]
            if "winding" in list(init_dict.keys()):
                winding = init_dict["winding"]
            if "slot_list" in list(init_dict.keys()):
                slot_list = init_dict["slot_list"]
            if "alpha" in list(init_dict.keys()):
                alpha = init_dict["alpha"]
            if "sym_dict_enforced" in list(init_dict.keys()):
                sym_dict_enforced = init_dict["sym_dict_enforced"]
            if "L1" in list(init_dict.keys()):
                L1 = init_dict["L1"]
            if "mat_type" in list(init_dict.keys()):
                mat_type = init_dict["mat_type"]
            if "Nrvd" in list(init_dict.keys()):
                Nrvd = init_dict["Nrvd"]
            if "Wrvd" in list(init_dict.keys()):
                Wrvd = init_dict["Wrvd"]
            if "Kf1" in list(init_dict.keys()):
                Kf1 = init_dict["Kf1"]
            if "is_internal" in list(init_dict.keys()):
                is_internal = init_dict["is_internal"]
            if "Rint" in list(init_dict.keys()):
                Rint = init_dict["Rint"]
            if "Rext" in list(init_dict.keys()):
                Rext = init_dict["Rext"]
            if "is_stator" in list(init_dict.keys()):
                is_stator = init_dict["is_stator"]
            if "axial_vent" in list(init_dict.keys()):
                axial_vent = init_dict["axial_vent"]
            if "notch" in list(init_dict.keys()):
                notch = init_dict["notch"]
            if "skew" in list(init_dict.keys()):
                skew = init_dict["skew"]
            if "bore" in list(init_dict.keys()):
                bore = init_dict["bore"]
            if "yoke" in list(init_dict.keys()):
                yoke = init_dict["yoke"]
        # Set the properties (value check and convertion are done in setter)
        self.Ksfill = Ksfill
        self.winding = winding
        # Call LamSlotMulti init
        super(LamSlotMultiWind, self).__init__(
            slot_list=slot_list,
            alpha=alpha,
            sym_dict_enforced=sym_dict_enforced,
            L1=L1,
            mat_type=mat_type,
            Nrvd=Nrvd,
            Wrvd=Wrvd,
            Kf1=Kf1,
            is_internal=is_internal,
            Rint=Rint,
            Rext=Rext,
            is_stator=is_stator,
            axial_vent=axial_vent,
            notch=notch,
            skew=skew,
            bore=bore,
            yoke=yoke,
        )
        # The class is frozen (in LamSlotMulti init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        LamSlotMultiWind_str = ""
        # Get the properties inherited from LamSlotMulti
        LamSlotMultiWind_str += super(LamSlotMultiWind, self).__str__()
        LamSlotMultiWind_str += "Ksfill = " + str(self.Ksfill) + linesep
        if self.winding is not None:
            tmp = self.winding.__str__().replace(linesep, linesep + "\t").rstrip("\t")
            LamSlotMultiWind_str += "winding = " + tmp
        else:
            LamSlotMultiWind_str += "winding = None" + linesep + linesep
        return LamSlotMultiWind_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from LamSlotMulti
        if not super(LamSlotMultiWind, self).__eq__(other):
            return False
        if other.Ksfill != self.Ksfill:
            return False
        if other.winding != self.winding:
            return False
        return True

    def compare(self, other, name="self", ignore_list=None, is_add_value=False):
        """Compare two objects and return list of differences"""

        if ignore_list is None:
            ignore_list = list()
        if type(other) != type(self):
            return ["type(" + name + ")"]
        diff_list = list()

        # Check the properties inherited from LamSlotMulti
        diff_list.extend(
            super(LamSlotMultiWind, self).compare(
                other, name=name, ignore_list=ignore_list, is_add_value=is_add_value
            )
        )
        if (
            other._Ksfill is not None
            and self._Ksfill is not None
            and np.isnan(other._Ksfill)
            and np.isnan(self._Ksfill)
        ):
            pass
        elif other._Ksfill != self._Ksfill:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._Ksfill)
                    + ", other="
                    + str(other._Ksfill)
                    + ")"
                )
                diff_list.append(name + ".Ksfill" + val_str)
            else:
                diff_list.append(name + ".Ksfill")
        if (other.winding is None and self.winding is not None) or (
            other.winding is not None and self.winding is None
        ):
            diff_list.append(name + ".winding None mismatch")
        elif self.winding is not None:
            diff_list.extend(
                self.winding.compare(
                    other.winding,
                    name=name + ".winding",
                    ignore_list=ignore_list,
                    is_add_value=is_add_value,
                )
            )
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object

        # Get size of the properties inherited from LamSlotMulti
        S += super(LamSlotMultiWind, self).__sizeof__()
        S += getsizeof(self.Ksfill)
        S += getsizeof(self.winding)
        return S

    def as_dict(self, type_handle_ndarray=0, keep_function=False, **kwargs):
        """
        Convert this object in a json serializable dict (can be use in __init__).
        type_handle_ndarray: int
            How to handle ndarray (0: tolist, 1: copy, 2: nothing)
        keep_function : bool
            True to keep the function object, else return str
        Optional keyword input parameter is for internal use only
        and may prevent json serializability.
        """

        # Get the properties inherited from LamSlotMulti
        LamSlotMultiWind_dict = super(LamSlotMultiWind, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs,
        )
        LamSlotMultiWind_dict["Ksfill"] = self.Ksfill
        if self.winding is None:
            LamSlotMultiWind_dict["winding"] = None
        else:
            LamSlotMultiWind_dict["winding"] = self.winding.as_dict(
                type_handle_ndarray=type_handle_ndarray,
                keep_function=keep_function,
                **kwargs,
            )
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        LamSlotMultiWind_dict["__class__"] = "LamSlotMultiWind"
        return LamSlotMultiWind_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        Ksfill_val = self.Ksfill
        if self.winding is None:
            winding_val = None
        else:
            winding_val = self.winding.copy()
        if self.slot_list is None:
            slot_list_val = None
        else:
            slot_list_val = list()
            for obj in self.slot_list:
                slot_list_val.append(obj.copy())
        if self.alpha is None:
            alpha_val = None
        else:
            alpha_val = self.alpha.copy()
        if self.sym_dict_enforced is None:
            sym_dict_enforced_val = None
        else:
            sym_dict_enforced_val = self.sym_dict_enforced.copy()
        L1_val = self.L1
        if self.mat_type is None:
            mat_type_val = None
        else:
            mat_type_val = self.mat_type.copy()
        Nrvd_val = self.Nrvd
        Wrvd_val = self.Wrvd
        Kf1_val = self.Kf1
        is_internal_val = self.is_internal
        Rint_val = self.Rint
        Rext_val = self.Rext
        is_stator_val = self.is_stator
        if self.axial_vent is None:
            axial_vent_val = None
        else:
            axial_vent_val = list()
            for obj in self.axial_vent:
                axial_vent_val.append(obj.copy())
        if self.notch is None:
            notch_val = None
        else:
            notch_val = list()
            for obj in self.notch:
                notch_val.append(obj.copy())
        if self.skew is None:
            skew_val = None
        else:
            skew_val = self.skew.copy()
        if self.bore is None:
            bore_val = None
        else:
            bore_val = self.bore.copy()
        if self.yoke is None:
            yoke_val = None
        else:
            yoke_val = self.yoke.copy()
        # Creates new object of the same type with the copied properties
        obj_copy = type(self)(
            Ksfill=Ksfill_val,
            winding=winding_val,
            slot_list=slot_list_val,
            alpha=alpha_val,
            sym_dict_enforced=sym_dict_enforced_val,
            L1=L1_val,
            mat_type=mat_type_val,
            Nrvd=Nrvd_val,
            Wrvd=Wrvd_val,
            Kf1=Kf1_val,
            is_internal=is_internal_val,
            Rint=Rint_val,
            Rext=Rext_val,
            is_stator=is_stator_val,
            axial_vent=axial_vent_val,
            notch=notch_val,
            skew=skew_val,
            bore=bore_val,
            yoke=yoke_val,
        )
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        self.Ksfill = None
        if self.winding is not None:
            self.winding._set_None()
        # Set to None the properties inherited from LamSlotMulti
        super(LamSlotMultiWind, self)._set_None()

    def _get_Ksfill(self):
        """getter of Ksfill"""
        return self._Ksfill

    def _set_Ksfill(self, value):
        """setter of Ksfill"""
        check_var("Ksfill", value, "float", Vmin=0, Vmax=1)
        self._Ksfill = value

    Ksfill = property(
        fget=_get_Ksfill,
        fset=_set_Ksfill,
        doc="""Imposed Slot Fill factor (if None, will be computed according to the winding and the slot)

        :Type: float
        :min: 0
        :max: 1
        """,
    )

    def _get_winding(self):
        """getter of winding"""
        return self._winding

    def _set_winding(self, value):
        """setter of winding"""
        if isinstance(value, str):  # Load from file
            try:
                value = load_init_dict(value)[1]
            except Exception as e:
                self.get_logger().error(
                    "Error while loading " + value + ", setting None instead"
                )
                value = None
        if isinstance(value, dict) and "__class__" in value:
            class_obj = import_class(
                "pyleecan.Classes", value.get("__class__"), "winding"
            )
            value = class_obj(init_dict=value)
        elif type(value) is int and value == -1:  # Default constructor
            Winding = import_class("pyleecan.Classes", "Winding", "winding")
            value = Winding()
        check_var("winding", value, "Winding")
        self._winding = value

        if self._winding is not None:
            self._winding.parent = self

    winding = property(
        fget=_get_winding,
        fset=_set_winding,
        doc="""Lamination's Winding

        :Type: Winding
        """,
    )
