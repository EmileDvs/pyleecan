# -*- coding: utf-8 -*-
# File generated according to Generator/ClassesRef/Machine/LamSquirrelCage.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Machine/LamSquirrelCage
"""

# Inline fallback report:
# These methods remain imported because their source or imports cannot be safely moved into this class.
# - check: module uses a wildcard import whose names cannot be resolved safely
# - plot_side: import name 'SCR_COLOR' refers to different sources (pyleecan.Methods.Machine.LamSquirrelCage.plot.SCR_COLOR and pyleecan.Methods.Machine.LamSquirrelCage.plot_side.SCR_COLOR)

from os import linesep
from sys import getsizeof
from logging import getLogger
from pyleecan.Classes._check import check_var, raise_
from pyleecan.Functions.get_logger import get_logger
from pyleecan.Functions.save import save
from pyleecan.Functions.load import load_init_dict
from pyleecan.Functions.Load.import_class import import_class
from copy import deepcopy
from pyleecan.Classes.LamSlotWind import LamSlotWind

# Import all class method
# Try/catch to remove unnecessary dependencies in unused method
from pyleecan.Methods.Machine.LamSquirrelCage.check import check
from pyleecan.Methods.Machine.LamSquirrelCage.plot_side import plot_side
from pyleecan.Functions.labels import WIND_LAB, BAR_LAB
from pyleecan.Classes.LamSlotWind import LamSlotWind
from numpy import pi, sin
from pyleecan.Classes.LamSlot import LamSlot
from pyleecan.Functions.load import import_class
from pyleecan.Methods.Machine.LamSquirrelCage.plot import SCR_COLOR
from matplotlib.patches import Patch, Wedge
from pyleecan.Functions.init_fig import init_fig
import matplotlib.pyplot as plt
from pyleecan.Classes.SlotW22 import SlotW22
from pyleecan.Classes.Segment import Segment
from pyleecan.Functions.Plot import (
    ARROW_COLOR,
    ARROW_WIDTH,
    MAIN_LINE_COLOR,
    MAIN_LINE_STYLE,
    MAIN_LINE_WIDTH,
    SC_FONT_SIZE,
    plot_quote,
)

from numpy import isnan
from pyleecan.Classes._check import InitUnKnowClassError


class LamSquirrelCage(LamSlotWind):
    """squirrel cages lamination"""

    VERSION = 1

    # cf Methods.Machine.LamSquirrelCage.build_geometry
    def build_geometry(self, sym=1, alpha=0, delta=0, is_circular_radius=False):
        """Build geometry of the LamSquirrelCage

        Parameters
        ----------
        self :
            LamSquirrelCage Object
        sym : int
            Symmetry factor (1= full machine, 2= half of the machine...)
        alpha : float
            Angle for rotation [rad]
        delta : complex
            Complex value for translation
        is_circular_radius : bool
            True to add surfaces to "close" the Lamination radii

        Returns
        -------
        surf_list: list
            list of surfaces

        """
        surf_list = LamSlotWind.build_geometry(
            self,
            sym=sym,
            is_circular_radius=is_circular_radius,
            alpha=alpha,
            delta=delta,
        )

        # Adapt the label
        for surf in surf_list:
            if WIND_LAB in surf.label:
                surf.label = surf.label.replace(WIND_LAB, BAR_LAB)

        return surf_list

    # cf Methods.Machine.LamSquirrelCage.check
    check = check

    # cf Methods.Machine.LamSquirrelCage.comp_angle_d_axis
    def comp_angle_d_axis(self):
        """Compute the angle between the X axis and the first d+ axis
        By convention a "Tooth" is centered on the X axis

        Parameters
        ----------
        self : LamSquirrelCage
            A LamSquirrelCage object

        Returns
        -------
        d_angle : float
            angle between the X axis and the first d+ axis
        """

        return 0

    # cf Methods.Machine.LamSquirrelCage.comp_length_ring
    def comp_length_ring(self):
        """Computation of the squirrel cage end-ring average perimeter (circumferential length)

        Parameters
        ----------
        self : LamSquirrelCage
            A LamSquirrelCage object

        Returns
        -------
        Lring: float
            Length of the ring [m]

        """

        # calculation of the average radius of the center of the end-ring (distance to z-axis of the electrical machine)
        Rmw = self.slot.comp_radius_mid_active()

        return 2 * pi * Rmw

    # cf Methods.Machine.LamSquirrelCage.comp_masses
    def comp_masses(self):
        """Compute the Lamination masses

        Parameters
        ----------
        self : LamSquirrelCage
            A LamSquirrelCage object

        Returns
        -------
        M_dict: dict
            Lamination mass dictionary (Mtot, Mlam, Mwind, Mring) [kg]
        """

        if self.is_stator:
            lam_name = "Stator"
        else:
            lam_name = "Rotor"
        M_dict = LamSlot.comp_masses(self)

        if self.winding is not None:
            # Check
            if self.winding.conductor.cond_mat.struct.rho is None:
                mat_name = str(self.winding.conductor.cond_mat.name)
                raise Exception(
                    "Error: The "
                    + lam_name
                    + " winding conductor material ("
                    + mat_name
                    + ") is not fully defined. Please set struct.rho"
                )
            # Compute
            L_dict = self.comp_lengths_winding()
            Mwind = (
                self.winding.conductor.comp_surface_active()
                * self.get_Zs()
                * self.winding.conductor.cond_mat.struct.rho
                * L_dict["Lwht"]
            )
        else:
            Mwind = 0

        # Adding Short circuit ring
        # Check
        if self.ring_mat.struct.rho is None:
            mat_name = str(self.ring_mat.name)
            raise Exception(
                "Error: The "
                + lam_name
                + " Short circuit ring material ("
                + mat_name
                + ") is not fully defined. Please set struct.rho"
            )
        Sring = self.comp_surface_ring()
        Lring = self.comp_length_ring()
        Mring = Sring * Lring * self.ring_mat.struct.rho

        M_dict["Mtot"] += Mwind + Mring
        M_dict["Mwind"] = Mwind + Mring
        M_dict["Mring"] = Mring

        return M_dict

    # cf Methods.Machine.LamSquirrelCage.comp_number_phase_eq
    def comp_number_phase_eq(self):
        """Compute the equivalent number of phase

        Parameters
        ----------
        self : LamSquirrelCage
            A LamSquirrelCage object

        Returns
        -------
        qb: float
            Zs/p
        """

        return self.slot.Zs / float(self.winding.p)

    # cf Methods.Machine.LamSquirrelCage.comp_periodicity_spatial
    def comp_periodicity_spatial(self):
        """Compute the periodicity factor of the lamination

        Parameters
        ----------
        self : LamSquirrelCage
            A LamSquirrelCage object

        Returns
        -------
        per_a : int
            Number of spatial periodicities of the lamination
        is_antiper_a : bool
            True if an spatial anti-periodicity is possible after the periodicities
        """

        # Reuse method from Lamination instead of LamSlotWind since winding periodicity is given by lamination periodicity
        Lamination = import_class("pyleecan.Classes", "Lamination")

        per_a, is_antiper_a = Lamination.comp_periodicity_spatial(self)

        return per_a, is_antiper_a

    # cf Methods.Machine.LamSquirrelCage.comp_resistance_wind
    def comp_resistance_wind(self, T=20):
        """Computation of the equivalent rotor resistance per phase of a cage winding with 'qs' number of phases

        Parameters
        ----------
        self : LamSquirrelCage
            A LamSquirrelCage object
        T : float
            mean winding temperature [°C], default value is 20°C

        Returns
        -------
        Rrot: float
            resistance of the rotor [Ohm]
        """
        # calculate resistance ring at T degC
        rho = self.ring_mat.elec.get_resistivity(T_op=T, T_ref=20)

        Sring = self.comp_surface_ring()
        lring = self.comp_length_ring()
        Zr = self.get_Zs()
        P = self.get_pole_pair_number()
        # total ring resistance (not yet divided by Zr to take average resistance seen by one bar)
        Rring = rho * lring / Sring

        # calculate resistance rod at T degC
        rho = self.winding.conductor.cond_mat.elec.get_resistivity(T_op=T, T_ref=20)

        # active surface inside slot
        Srod = self.winding.conductor.comp_surface_active()
        # total bar length inside lamination + outside lamination before end ring (#TODO Lewout should be 0 for molded cage, #TODO comp_length() should account for skew shape)
        lrod = self.comp_length() + 2 * self.winding.Lewout
        # bar resistance
        Rrod = rho * lrod / Srod

        # average physical resistance per rotor bar (not yet transfered on stator side, per stator phase)
        Rtot = Rrod + Rring / Zr / (2 * sin(pi * P / Zr) ** 2)

        return Rtot

    # cf Methods.Machine.LamSquirrelCage.comp_surface_ring
    def comp_surface_ring(self):
        """Computation of the ring cross-section surface area

        Parameters
        ----------
        self : LamSquirrelCage
            A LamSquirrelCage object

        Returns
        -------
        Lring: float
            Surface area of the cross-section of the ring [m^2]

        """
        Hscr = self.Hscr
        Lscr = self.Lscr

        return Lscr * Hscr

    # cf Methods.Machine.LamSquirrelCage.get_name_phase
    def get_name_phase(self):
        """Return the name of the winding phases

        Parameters
        ----------
        self : LamSquirrelCage
            A LamSquirrelCage object

        Returns
        -------
        name_phase: list
            Empty list

        """
        if (
            not hasattr(self, "winding")
            or self.winding is None
            # or self.winding.conductor is None
        ):
            return list()
        qs = 3 if self.winding.qs is None else self.winding.qs

        return ["Bar " + str(ii + 1) for ii in range(qs)]

    # cf Methods.Machine.LamSquirrelCage.plot
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
        is_show_fig=True,
        is_winding_connection=False,
    ):
        """Plot the Lamination in a matplotlib fig

        Parameters
        ----------
        self : LamSquirrelCage
            A LamSquirrelCage object
        fig : Matplotlib.figure.Figure
            existing figure to use if None create a new one
        ax : Matplotlib.axes.Axes object
            Axis on which to plot the data
        is_lam_only : bool
            True to plot only the lamination (remove the bare)
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
        is_show_fig : bool
            To call show at the end of the method
        is_winding_connection : bool
            True to display winding connections (not used)

        Returns
        -------
        fig : Matplotlib.figure.Figure
            Figure containing the plot
        ax : Matplotlib.axes.Axes object
            Axis containing the plot
        """

        # Lamination and ventilation ducts patches
        (fig, ax, patch_leg, label_leg) = init_fig(fig=fig, ax=ax, shape="rectangle")

        # Plot the lamination
        LamSlotWind.plot(
            self,
            fig=fig,
            ax=ax,
            is_lam_only=is_lam_only,
            sym=sym,
            alpha=alpha,
            delta=delta,
            is_edge_only=is_edge_only,
            is_show_fig=is_show_fig,
        )

        # init figure again to get updated label_leg and patch_leg
        (fig, ax, patch_leg, label_leg) = init_fig(fig, ax=ax)

        # setup the patch of the short circuit ring if needed
        patches = list()
        if not is_lam_only:
            try:
                Rmw = self.slot.comp_radius_mid_active()
                patches.append(
                    Wedge(
                        (0, 0),
                        Rmw + self.Hscr / 2.0,
                        0,
                        360 / sym,
                        width=self.Hscr,
                        color=SCR_COLOR,
                    )
                )  # Full ring
            except:
                pass

        # Display the result
        ax.set_xlabel("(m)")
        ax.set_ylabel("(m)")
        ax.set_title("Squirrel Cage Rotor")

        # Axis Setup
        ax.axis("equal")
        Lim = self.Rext * 1.5
        ax.set_xlim(-Lim, Lim)
        if sym == 1:
            ax.set_ylim(-Lim, Lim)
        else:
            ax.set_ylim(-Lim * 0.3, Lim)

        if not is_lam_only:
            # Add the short ciruit ring to the fig
            for patch in patches:
                ax.add_patch(patch)
            if "Short Circuit Ring" not in label_leg:
                patch_leg.append(Patch(color=SCR_COLOR))
                label_leg.append("Short Circuit Ring")

            ax.legend(patch_leg, label_leg)
        if is_show_fig:
            fig.show()
        return fig, ax

    # cf Methods.Machine.LamSquirrelCage.plot_schematics_scr
    def plot_schematics_scr(
        self,
        is_default=False,
        is_add_schematics=True,
        is_add_main_line=True,
        save_path=None,
        is_show_fig=True,
        fig=None,
        ax=None,
    ):
        """Plot the schematics of the short circuit ring

        Parameters
        ----------
        self : LamSquirrelCage
            A LamSquirrelCage object
        is_default : bool
            True: plot default schematics, else use current lamination values
        is_add_schematics : bool
            True to display the schematics information (Hscr, Lscr...)
        is_add_main_line : bool
            True to display "main lines" (dotted lines and Z axis)
        save_path : str
            full path including folder, name and extension of the file to save if save_path is not None
        is_show_fig : bool
            To call show at the end of the method
        fig : Matplotlib.figure.Figure
            existing figure to use if None create a new one
        ax : Matplotlib.axes.Axes object
            Axis on which to plot the data

        Returns
        -------
        fig : Matplotlib.figure.Figure
            Figure containing the plot
        ax : Matplotlib.axes.Axes object
            Axis containing the plot
        """

        # Use some default parameter
        if is_default:
            lam = type(self)(
                is_stator=False,
                is_internal=True,
                Rint=0,
                Rext=0.25,
                L1=1,
                Hscr=0.15,
                Lscr=0.1,
            )
            lam.slot = SlotW22(Zs=12, H0=0.02, H2=0.05)
            lam.winding.Lewout = 0.1
            lam.plot_schematics_scr(
                is_default=False,
                is_add_schematics=is_add_schematics,
                is_add_main_line=is_add_main_line,
                save_path=save_path,
                is_show_fig=is_show_fig,
                fig=fig,
                ax=ax,
            )
        else:
            # Getting the main plot
            fig, ax = self.plot_side(is_show_fig=False, fig=fig, ax=ax)
            Lt = self.comp_length()
            Hs = self.slot.comp_height()
            Ha = self.slot.comp_height_active()
            Ho = Hs - Ha
            Le = self.winding.Lewout
            Lscr = self.Lscr
            Hscr = self.Hscr

            # Adding schematics
            if is_add_schematics:
                # Rext
                line = Segment(Lt / 2 - Lt / 5, Lt / 2 - Lt / 5 + 1j * self.Rext)
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="Rext",
                    offset_label=-Le * 1.05,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # Lewout
                Zbar1 = Lt / 2 + 1j * (self.Rext - Hs + Ha)
                Zbar2 = Lt / 2 + Le + 1j * (self.Rext - Hs + Ha)
                Zlim1 = Zbar1 + 1j * Hs
                Zlim2 = Zbar2 + 1j * Hs
                plot_quote(
                    Zbar1,
                    Zlim1,
                    Zlim2,
                    Zbar2,
                    offset_label=1j * Le * 0.4 - Le * 0.7,
                    fig=fig,
                    ax=ax,
                    label="Lewout",
                )
                # Lscr
                ZL1 = Lt / 2 + Le + 1j * (self.Rext - Hs + Ha / 2 + Hscr / 2)
                ZL2 = Lt / 2 + Le + Lscr + 1j * (self.Rext - Hs + Ha / 2 + Hscr / 2)
                Zlim1 = ZL1 + 1j * Hs
                Zlim2 = ZL2 + 1j * Hs
                plot_quote(
                    ZL1,
                    Zlim1,
                    Zlim2,
                    ZL2,
                    offset_label=1j * Le * 0.4 - Le * 0.3,
                    fig=fig,
                    ax=ax,
                    label="Lscr",
                )
                # Hscr
                line = Segment(ZL2, ZL2 - 1j * Hscr)
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="Hscr",
                    offset_label=Le * 0.3,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )

            if is_add_main_line:
                # Ox axis
                line = Segment(0, Lt + Le + Lscr)
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                # Hscr lines
                line = Segment(ZL1 - 1j * Hscr, ZL2 - 1j * Hscr)
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                line = Segment(ZL1.conjugate() + 1j * Hscr, ZL2.conjugate() + 1j * Hscr)
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )

            ax.axis("equal")
            ax.set_xlim(Lt / 4, (Lt / 2 + Le + Lscr) * 1.1)
            # ax.set_ylim(-self.Rext, self.Rext)
            manager = plt.get_current_fig_manager()
            if manager is not None:
                manager.set_window_title(type(self).__name__ + " Schematics")
            ax.set_title("")
            ax.get_legend().remove()
            ax.set_axis_off()

            # Save / Show
            if save_path is not None:
                fig.savefig(save_path)
                plt.close(fig=fig)

            if is_show_fig:
                fig.show()
            return fig, ax

    # cf Methods.Machine.LamSquirrelCage.plot_side
    plot_side = plot_side
    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
        Hscr=0.03,
        Lscr=0.015,
        ring_mat=-1,
        Ksfill=None,
        winding=-1,
        slot=-1,
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
            if "Hscr" in list(init_dict.keys()):
                Hscr = init_dict["Hscr"]
            if "Lscr" in list(init_dict.keys()):
                Lscr = init_dict["Lscr"]
            if "ring_mat" in list(init_dict.keys()):
                ring_mat = init_dict["ring_mat"]
            if "Ksfill" in list(init_dict.keys()):
                Ksfill = init_dict["Ksfill"]
            if "winding" in list(init_dict.keys()):
                winding = init_dict["winding"]
            if "slot" in list(init_dict.keys()):
                slot = init_dict["slot"]
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
        self.Hscr = Hscr
        self.Lscr = Lscr
        self.ring_mat = ring_mat
        # Call LamSlotWind init
        super(LamSquirrelCage, self).__init__(
            Ksfill=Ksfill,
            winding=winding,
            slot=slot,
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
        # The class is frozen (in LamSlotWind init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        LamSquirrelCage_str = ""
        # Get the properties inherited from LamSlotWind
        LamSquirrelCage_str += super(LamSquirrelCage, self).__str__()
        LamSquirrelCage_str += "Hscr = " + str(self.Hscr) + linesep
        LamSquirrelCage_str += "Lscr = " + str(self.Lscr) + linesep
        if self.ring_mat is not None:
            tmp = self.ring_mat.__str__().replace(linesep, linesep + "\t").rstrip("\t")
            LamSquirrelCage_str += "ring_mat = " + tmp
        else:
            LamSquirrelCage_str += "ring_mat = None" + linesep + linesep
        return LamSquirrelCage_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from LamSlotWind
        if not super(LamSquirrelCage, self).__eq__(other):
            return False
        if other.Hscr != self.Hscr:
            return False
        if other.Lscr != self.Lscr:
            return False
        if other.ring_mat != self.ring_mat:
            return False
        return True

    def compare(self, other, name="self", ignore_list=None, is_add_value=False):
        """Compare two objects and return list of differences"""

        if ignore_list is None:
            ignore_list = list()
        if type(other) != type(self):
            return ["type(" + name + ")"]
        diff_list = list()

        # Check the properties inherited from LamSlotWind
        diff_list.extend(
            super(LamSquirrelCage, self).compare(
                other, name=name, ignore_list=ignore_list, is_add_value=is_add_value
            )
        )
        if (
            other._Hscr is not None
            and self._Hscr is not None
            and isnan(other._Hscr)
            and isnan(self._Hscr)
        ):
            pass
        elif other._Hscr != self._Hscr:
            if is_add_value:
                val_str = (
                    " (self=" + str(self._Hscr) + ", other=" + str(other._Hscr) + ")"
                )
                diff_list.append(name + ".Hscr" + val_str)
            else:
                diff_list.append(name + ".Hscr")
        if (
            other._Lscr is not None
            and self._Lscr is not None
            and isnan(other._Lscr)
            and isnan(self._Lscr)
        ):
            pass
        elif other._Lscr != self._Lscr:
            if is_add_value:
                val_str = (
                    " (self=" + str(self._Lscr) + ", other=" + str(other._Lscr) + ")"
                )
                diff_list.append(name + ".Lscr" + val_str)
            else:
                diff_list.append(name + ".Lscr")
        if (other.ring_mat is None and self.ring_mat is not None) or (
            other.ring_mat is not None and self.ring_mat is None
        ):
            diff_list.append(name + ".ring_mat None mismatch")
        elif self.ring_mat is not None:
            diff_list.extend(
                self.ring_mat.compare(
                    other.ring_mat,
                    name=name + ".ring_mat",
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

        # Get size of the properties inherited from LamSlotWind
        S += super(LamSquirrelCage, self).__sizeof__()
        S += getsizeof(self.Hscr)
        S += getsizeof(self.Lscr)
        S += getsizeof(self.ring_mat)
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

        # Get the properties inherited from LamSlotWind
        LamSquirrelCage_dict = super(LamSquirrelCage, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs
        )
        LamSquirrelCage_dict["Hscr"] = self.Hscr
        LamSquirrelCage_dict["Lscr"] = self.Lscr
        if self.ring_mat is None:
            LamSquirrelCage_dict["ring_mat"] = None
        else:
            LamSquirrelCage_dict["ring_mat"] = self.ring_mat.as_dict(
                type_handle_ndarray=type_handle_ndarray,
                keep_function=keep_function,
                **kwargs
            )
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        LamSquirrelCage_dict["__class__"] = "LamSquirrelCage"
        return LamSquirrelCage_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        Hscr_val = self.Hscr
        Lscr_val = self.Lscr
        if self.ring_mat is None:
            ring_mat_val = None
        else:
            ring_mat_val = self.ring_mat.copy()
        Ksfill_val = self.Ksfill
        if self.winding is None:
            winding_val = None
        else:
            winding_val = self.winding.copy()
        if self.slot is None:
            slot_val = None
        else:
            slot_val = self.slot.copy()
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
            Hscr=Hscr_val,
            Lscr=Lscr_val,
            ring_mat=ring_mat_val,
            Ksfill=Ksfill_val,
            winding=winding_val,
            slot=slot_val,
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

        self.Hscr = None
        self.Lscr = None
        if self.ring_mat is not None:
            self.ring_mat._set_None()
        # Set to None the properties inherited from LamSlotWind
        super(LamSquirrelCage, self)._set_None()

    def _get_Hscr(self):
        """getter of Hscr"""
        return self._Hscr

    def _set_Hscr(self, value):
        """setter of Hscr"""
        check_var("Hscr", value, "float", Vmin=0)
        self._Hscr = value

    Hscr = property(
        fget=_get_Hscr,
        fset=_set_Hscr,
        doc="""short circuit ring section radial height [m]

        :Type: float
        :min: 0
        """,
    )

    def _get_Lscr(self):
        """getter of Lscr"""
        return self._Lscr

    def _set_Lscr(self, value):
        """setter of Lscr"""
        check_var("Lscr", value, "float", Vmin=0)
        self._Lscr = value

    Lscr = property(
        fget=_get_Lscr,
        fset=_set_Lscr,
        doc="""short circuit ring section axial length

        :Type: float
        :min: 0
        """,
    )

    def _get_ring_mat(self):
        """getter of ring_mat"""
        return self._ring_mat

    def _set_ring_mat(self, value):
        """setter of ring_mat"""
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
                "pyleecan.Classes", value.get("__class__"), "ring_mat"
            )
            value = class_obj(init_dict=value)
        elif type(value) is int and value == -1:  # Default constructor
            Material = import_class("pyleecan.Classes", "Material", "ring_mat")
            value = Material()
        check_var("ring_mat", value, "Material")
        self._ring_mat = value

        if self._ring_mat is not None:
            self._ring_mat.parent = self

    ring_mat = property(
        fget=_get_ring_mat,
        fset=_set_ring_mat,
        doc="""Material of the Rotor short circuit ring

        :Type: Material
        """,
    )
