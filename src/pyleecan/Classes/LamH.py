# File generated according to Generator/ClassesRef/Machine/LamH.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Machine/LamH"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch
from pyleecan.Classes.Hole import Hole
from pyleecan.Classes.Lamination import Lamination
from pyleecan.Functions.Plot.get_color_legend_from_surface import (
    get_color_legend_from_surface,
)
from pyleecan.Functions.get_logger import get_logger
from pyleecan.Functions.init_fig import init_fig
from pyleecan.Functions.load import load_init_dict
from pyleecan.Functions.save import save


class LamH(Lamination):
    """Lamination with Hole (Abstract class)"""

    VERSION = 1

    # cf Methods.Machine.LamH.comp_angle_d_axis
    def comp_angle_d_axis(self):
        """Compute the angle between the X axis and the first d+ axis
        By convention a "Tooth" is centered on the X axis
        By convention the first magnet is +

        Parameters
        ----------
        self : LamH
            A LamH object

        Returns
        -------
        d_angle : float
            angle between the X axis and the first d+ axis
        """

        p = self.get_pole_pair_number()
        if self.has_magnet():
            return np.pi / p / 2
        else:
            return 0

    # cf Methods.Machine.LamH.comp_height_yoke
    def comp_height_yoke(self):
        """Compute the yoke height

        Parameters
        ----------
        self : LamH
            A LamH object

        Returns
        -------
        Hy: float
            yoke height [m]

        """

        if self.is_internal:
            R = self.Rext
        else:
            R = self.Rint

        # The yoke is define the greater cylinder without holes
        for hole in self.get_hole_list():
            (Rmin, Rmax) = hole.comp_radius()
            if self.is_internal:
                R = min(R, Rmin)
            else:
                R = max(R, Rmax)

        if self.is_internal:
            return R - self.Rint
        else:
            return self.Rext - R

    # cf Methods.Machine.LamH.comp_masses
    def comp_masses(self):
        """Compute the Lamination masses

        Parameters
        ----------
        self : LamH
            A LamH object

        Returns
        -------
        M_dict: dict
            Lamination mass dictionary (Mtot, Mlam, Mmag) [kg]

        """

        M_dict = Lamination.comp_masses(self)

        Mmag = 0
        for hole in self.get_hole_list():
            if hole.has_magnet():
                Mmag += hole.Zh * hole.comp_mass_magnets()

        M_dict["Mmag"] = Mmag
        M_dict["Mtot"] += Mmag

        return M_dict

    # cf Methods.Machine.LamH.comp_radius_mid_yoke
    def comp_radius_mid_yoke(self):
        """Compute the Lamination middle of the yoke radius

        Parameters
        ----------
        self : LamH
            A LamH object

        Returns
        -------
        Ry: float
            middle of the yoke radius [m]

        """

        Rmin = self.Rext
        Rmax = self.Rint
        for hole in self.get_hole_list():
            if type(hole) is not Hole:
                (Rmin_hole, Rmax_hole) = hole.comp_radius()
                Rmin = min(Rmin, Rmin_hole)
                Rmax = max(Rmax, Rmax_hole)
        if self.is_internal:
            return (self.Rint + Rmin) / 2
        else:
            return (self.Rext + Rmax) / 2

    # cf Methods.Machine.LamH.comp_surfaces
    def comp_surfaces(self):
        """Compute the Lamination surfaces

        Parameters
        ----------
        self : LamH
            A LamH object

        Returns
        -------
        S_dict: dict
            Lamination surface dictionary (Slam, Svent, Smag, Shole) [m**2]

        """

        S_dict = Lamination.comp_surfaces(self)

        # hole surface
        Shole = 0
        Smag = 0
        for hole in self.get_hole_list():
            Shole += hole.Zh * hole.comp_surface()
            if hole.has_magnet():
                Smag += hole.Zh * hole.comp_surface_magnets()

        Ryoke = self.get_Ryoke()
        Hyoke = self.comp_height_yoke()
        if self.is_internal:
            S_dict["Syoke"] = (
                np.pi * ((Ryoke + Hyoke) ** 2 - Ryoke**2) - S_dict["Svent"]
            )
        else:
            S_dict["Syoke"] = (
                np.pi * (Ryoke**2 - (Ryoke - Hyoke) ** 2) - S_dict["Svent"]
            )

        S_dict["Smag"] = Smag
        S_dict["Shole"] = Shole
        S_dict["Slam"] -= Shole  # the magnet surface in included in the hole one
        S_dict["Steeth"] = S_dict["Slam"] - S_dict["Syoke"]

        return S_dict

    # cf Methods.Machine.LamH.comp_volumes
    def comp_volumes(self):
        """Compute the Lamination volumes

        Parameters
        ----------
        self : LamH
            A LamH object

        Returns
        -------
        V_dict: dict
            Lamination volume dictionary (Vlam, Vvent, Vmag, Vhole) [m**3]

        """

        V_dict = Lamination.comp_volumes(self)
        Lt = self.comp_length()

        Vhole = 0
        Vmag = 0
        for hole in self.get_hole_list():
            Vhole += hole.Zh * hole.comp_surface() * Lt
            if hole.has_magnet():
                Vmag += hole.Zh * hole.comp_volume_magnets()

        V_dict["Vmag"] = Vmag
        V_dict["Vhole"] = Vhole

        return V_dict

    # cf Methods.Machine.LamH.get_pole_pair_number
    def get_pole_pair_number(self):
        """Return the number of pair of pole of the Lamination

        Parameters
        ----------
        self : LamH
            A LamH object

        Returns
        -------
        p: int
            Number of pair of pole

        """

        hole_list = self.get_hole_list()
        if len(hole_list) > 0:
            return hole_list[0].Zh // 2
        else:
            return None

    # cf Methods.Machine.LamH.get_Zs
    def get_Zs(self):
        """Return the number of holes in the lamination

        Parameters
        ----------
        self : LamH
            A LamH object

        Returns
        -------
        p: int
            Number of pair of pole

        """

        return self.get_pole_pair_number() * 2

    # cf Methods.Machine.LamH.has_magnet
    def has_magnet(self):
        """Return if any of the Holes have magnets

        Parameters
        ----------
        self : LamH
            A LamH object

        Returns
        -------
        has_magnet : bool
            True if any of the Holes have magnets
        """

        has_mag = [hole.has_magnet() for hole in self.get_hole_list()]
        return any(has_mag)

    # cf Methods.Machine.LamH.plot
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
        save_path=None,
        win_title=None,
        is_clean_plot=False,
        is_winding_connection=False,
    ):
        """Plot a Lamination with Buried Magnets in a matplotlib fig

        Parameters
        ----------
        self : LamH
            A LamH object
        fig : Matplotlib.figure.Figure
            existing figure to use if None create a new one
        ax : Matplotlib.axes.Axes object
            Axis on which to plot the data
        is_lam_only: bool
            True to plot only the lamination (remove the magnets)
        sym : int
            Symmetry factor (1= plot full machine, 2= half of the machine...)
        alpha : float
            angle for rotation (Default value = 0) [rad]
        delta : complex
            complex for translation (Default value = 0)
        is_edge_only: bool
            To plot transparent Patches
        edgecolor:
            Color of the edges if is_edge_only=True
        is_add_arrow : bool
            To add an arrow for the magnetization
        is_show_fig : bool
            To call show at the end of the method
        save_path : str
            full path including folder, name and extension of the file to save if save_path is not None
        win_title : str
            Window title
        is_clean_plot : bool
            True to remove title, legend, axis (only machine on plot with white background)
        is_winding_connection : bool
            True to display winding connections (not used)

        Returns
        -------
        fig : Matplotlib.figure.Figure
            Figure containing the plot
        ax : Matplotlib.axes.Axes object
            Axis containing the plot
        """

        # Lamination bore
        if self.is_stator:
            lam_name = "Stator"
        else:
            lam_name = "Rotor"

        # List of surface to plot the lamination
        (fig, ax, patch_leg, label_leg) = init_fig(fig=fig, ax=ax, shape="rectangle")

        surf_list = self.build_geometry(sym=sym, alpha=alpha, delta=delta)
        patches = list()

        for surf in surf_list:
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

        ax.set_xlabel("(m)")
        ax.set_ylabel("(m)")

        for patch in patches:
            ax.add_patch(patch)

        # Add Magnetization arrow
        if is_add_arrow:
            self._plot_arrow_mag(ax=ax, sym=sym, alpha=alpha, delta=delta)

        # Axis Setup
        ax.axis("equal")

        # The Lamination is centered in the figure
        Lim = self.Rext * 1.5
        ax.set_xlim(-Lim, Lim)
        ax.set_ylim(-Lim, Lim)

        # Window title
        if (
            win_title is None
            and self.parent is not None
            and self.parent.name not in [None, ""]
        ):
            win_title = self.parent.name + " " + lam_name
        elif win_title is None:
            win_title = lam_name
        manager = plt.get_current_fig_manager()
        if manager is not None:
            manager.set_window_title(win_title)

        # Set legend
        if not is_edge_only:
            ax.set_title(f"{lam_name} with Interior Magnet")
            ax.legend(patch_leg, label_leg)

        # Clean figure
        if is_clean_plot:
            ax.set_axis_off()
            ax.axis("equal")
            if ax.get_legend() is not None:
                ax.get_legend().remove()
            ax.set_title("")

        if is_show_fig:
            fig.show()
        if save_path is not None:
            fig.savefig(save_path)
            plt.close(fig=fig)
        return fig, ax

    # cf Methods.Machine.LamH.set_Lmag
    def set_Lmag(self, value):
        """Set the Length of the magnet

        Parameters
        ----------
        self : LamH
            A LamH object
        value : float
            Value to set [m]
        """

        for hole in self.get_hole_list():
            mag_dict = hole.get_magnet_dict()
            for mag in mag_dict.values():
                mag.Lmag = value

    # cf Methods.Machine.LamH.set_pole_pair_number
    def set_pole_pair_number(self, p):
        """Set the number of pair of pole of the Lamination

        Parameters
        ----------
        self : LamH
            A LamH object
        p: int
            Number of pair of pole

        """

        for hole in self.get_hole_list():
            hole.Zh = 2 * p

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
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
        # Call Lamination init
        super(LamH, self).__init__(
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
        # The class is frozen (in Lamination init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        LamH_str = ""
        # Get the properties inherited from Lamination
        LamH_str += super(LamH, self).__str__()
        return LamH_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from Lamination
        if not super(LamH, self).__eq__(other):
            return False
        return True

    def compare(self, other, name="self", ignore_list=None, is_add_value=False):
        """Compare two objects and return list of differences"""

        if ignore_list is None:
            ignore_list = list()
        if type(other) != type(self):
            return ["type(" + name + ")"]
        diff_list = list()

        # Check the properties inherited from Lamination
        diff_list.extend(
            super(LamH, self).compare(
                other, name=name, ignore_list=ignore_list, is_add_value=is_add_value
            )
        )
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object

        # Get size of the properties inherited from Lamination
        S += super(LamH, self).__sizeof__()
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

        # Get the properties inherited from Lamination
        LamH_dict = super(LamH, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs,
        )
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        LamH_dict["__class__"] = "LamH"
        return LamH_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
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

        # Set to None the properties inherited from Lamination
        super(LamH, self)._set_None()
