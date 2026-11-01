# File generated according to Generator/ClassesRef/Machine/LamSquirrelCageMag.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Machine/LamSquirrelCageMag"""

from os import linesep
from sys import getsizeof

import numpy as np

from pyleecan.Classes.LamSlotWind import LamSlotWind
from pyleecan.Classes.LamSquirrelCage import LamSquirrelCage
from pyleecan.Classes._check import check_var

from pyleecan.Functions.Load.import_class import import_class
from pyleecan.Functions.get_logger import get_logger
from pyleecan.Functions.init_fig import init_fig
from pyleecan.Functions.labels import update_RTS_index
from pyleecan.Functions.load import load_init_dict
from pyleecan.Functions.save import save


class LamSquirrelCageMag(LamSquirrelCage):
    """Rotor lamination for LSPM"""

    VERSION = 1

    # cf Methods.Machine.LamSquirrelCageMag.build_geometry
    def build_geometry(self, sym=1, alpha=0, delta=0, is_circular_radius=False):
        """Build geometry of the LamSquirrelCage

        Parameters
        ----------
        self : LamSquirrelCageMag
            A LamSquirrelCageMag Object
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

        # Lamination label
        if self.is_stator:
            label = "Lamination_Stator"
        else:
            label = "Lamination_Rotor"

        surf_list = LamSquirrelCage.build_geometry(
            self,
            sym=sym,
            is_circular_radius=is_circular_radius,
            alpha=alpha,
            delta=delta,
        )

        # Holes surface(s)
        for hole in self.get_hole_list():
            Zh = hole.Zh
            assert (Zh % sym) == 0, (
                "ERROR, Wrong symmetry for "
                + label
                + " "
                + str(Zh)
                + " holes and sym="
                + str(sym)
            )  # For now only
            angle = 2 * np.pi / Zh
            # Create the first hole surface(s)
            surf_hole = hole.build_geometry(alpha=np.pi / Zh)

            hole_surf_list = list()
            # Copy the hole for Zh / sym
            for ii in range(Zh // sym):
                for surf in surf_hole:
                    new_surf = type(surf)(init_dict=surf.as_dict())
                    new_surf.label = update_RTS_index(label=new_surf.label, S_id=ii)
                    new_surf.rotate(ii * angle)
                    hole_surf_list.append(new_surf)

        # Apply the transformations
        for surf in hole_surf_list:
            surf.rotate(alpha)
            surf.translate(delta)

        surf_list.extend(hole_surf_list)
        return surf_list

    # cf Methods.Machine.LamSquirrelCageMag.check
    def check(self):
        """Check that the Lamination object is correct

        Parameters
        ----------
        self : LamSquirrelCageMag
            A LamSquirrelCageMag object

        Returns
        -------
        None

        Raises
        _______
        SCC_NotARotor
            A LamSquirrelCage Lamination can't be a stator
        SCC_WrongCond
            A LamSquirrelCage's conductor must be a type 2_1
        """

        LamSquirrelCage.check(self)

        # Check p
        p = self.winding.p
        assert len(self.hole) > 1
        for hole in self.hole:
            assert hole.Zh / 2 == p

    # cf Methods.Machine.LamSquirrelCageMag.comp_surfaces
    def comp_surfaces(self):
        """Compute the Lamination surfaces

        Parameters
        ----------
        self : LamSquirrelCageMag
            A LamSquirrelCageMag object

        Returns
        -------
        S_dict: dict
            Lamination surface dictionary (Slam, Svent, Smag, Shole) [m**2]

        """

        S_dict = LamSlotWind.comp_surfaces(self)

        # hole surface
        Shole = 0
        Smag = 0
        for hole in self.hole:
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

    # cf Methods.Machine.LamSquirrelCageMag.get_hole_list
    def get_hole_list(self):
        """Return the list of all the holes

        Parameters
        ----------
        self : LamSquirrelCageMag
            A LamSquirrelCageMag object

        Returns
        -------
        hole_list : [Hole]
            List of all the holes
        """
        if self.hole is None:
            self.hole = list()
        return self.hole

    # cf Methods.Machine.LamSquirrelCageMag.get_pole_pair_number
    def get_pole_pair_number(self):
        """Return the number of pair of pole of the Lamination

        Parameters
        ----------
        self : LamSlot
            A LamSlot object

        Returns
        -------
        p: int
            Number of pair of pole

        """

        p = self.winding.p

        for hole in self.hole:
            assert hole.Zh / 2 == p

        return p

    # cf Methods.Machine.LamSquirrelCageMag.plot
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

        # Plot the lamination (LamSquirrelCage)
        super(type(self), self).plot(
            fig=fig,
            is_lam_only=is_lam_only,
            sym=sym,
            alpha=alpha,
            delta=delta,
            is_edge_only=is_edge_only,
            is_show_fig=is_show_fig,
        )

        # Display the result
        ax.set_xlabel("(m)")
        ax.set_ylabel("(m)")
        ax.set_title("Squirrel Cage Rotor with Magnets")

        # Axis Setup
        ax.axis("equal")
        Lim = self.Rext * 1.5
        ax.set_xlim(-Lim, Lim)
        if sym == 1:
            ax.set_ylim(-Lim, Lim)
        else:
            ax.set_ylim(-Lim * 0.3, Lim)

        if not is_lam_only:
            ax.legend(patch_leg, label_leg)
        if is_show_fig:
            fig.show()
        return fig, ax

    # cf Methods.Machine.LamSquirrelCageMag.set_pole_pair_number
    def set_pole_pair_number(self, p):
        """Set the number of pair of pole of the Lamination

        Parameters
        ----------
        self : LamSquirrelCageMag
            A LamSquirrelCageMag object
        p: int
            Number of pair of pole

        """

        if self.winding is not None:
            self.winding.p = p
        if self.hole is not None:
            for hole in self.hole:
                hole.Zh = 2 * p

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
        hole=-1,
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
            if "hole" in list(init_dict.keys()):
                hole = init_dict["hole"]
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
        self.hole = hole
        # Call LamSquirrelCage init
        super(LamSquirrelCageMag, self).__init__(
            Hscr=Hscr,
            Lscr=Lscr,
            ring_mat=ring_mat,
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
        # The class is frozen (in LamSquirrelCage init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        LamSquirrelCageMag_str = ""
        # Get the properties inherited from LamSquirrelCage
        LamSquirrelCageMag_str += super(LamSquirrelCageMag, self).__str__()
        if len(self.hole) == 0:
            LamSquirrelCageMag_str += "hole = []" + linesep
        for ii in range(len(self.hole)):
            tmp = self.hole[ii].__str__().replace(linesep, linesep + "\t") + linesep
            LamSquirrelCageMag_str += (
                "hole[" + str(ii) + "] =" + tmp + linesep + linesep
            )
        return LamSquirrelCageMag_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from LamSquirrelCage
        if not super(LamSquirrelCageMag, self).__eq__(other):
            return False
        if other.hole != self.hole:
            return False
        return True

    def compare(self, other, name="self", ignore_list=None, is_add_value=False):
        """Compare two objects and return list of differences"""

        if ignore_list is None:
            ignore_list = list()
        if type(other) != type(self):
            return ["type(" + name + ")"]
        diff_list = list()

        # Check the properties inherited from LamSquirrelCage
        diff_list.extend(
            super(LamSquirrelCageMag, self).compare(
                other, name=name, ignore_list=ignore_list, is_add_value=is_add_value
            )
        )
        if (other.hole is None and self.hole is not None) or (
            other.hole is not None and self.hole is None
        ):
            diff_list.append(name + ".hole None mismatch")
        elif self.hole is None:
            pass
        elif len(other.hole) != len(self.hole):
            diff_list.append("len(" + name + ".hole)")
        else:
            for ii in range(len(other.hole)):
                diff_list.extend(
                    self.hole[ii].compare(
                        other.hole[ii],
                        name=name + ".hole[" + str(ii) + "]",
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

        # Get size of the properties inherited from LamSquirrelCage
        S += super(LamSquirrelCageMag, self).__sizeof__()
        if self.hole is not None:
            for value in self.hole:
                S += getsizeof(value)
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

        # Get the properties inherited from LamSquirrelCage
        LamSquirrelCageMag_dict = super(LamSquirrelCageMag, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs
        )
        if self.hole is None:
            LamSquirrelCageMag_dict["hole"] = None
        else:
            LamSquirrelCageMag_dict["hole"] = list()
            for obj in self.hole:
                if obj is not None:
                    LamSquirrelCageMag_dict["hole"].append(
                        obj.as_dict(
                            type_handle_ndarray=type_handle_ndarray,
                            keep_function=keep_function,
                            **kwargs
                        )
                    )
                else:
                    LamSquirrelCageMag_dict["hole"].append(None)
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        LamSquirrelCageMag_dict["__class__"] = "LamSquirrelCageMag"
        return LamSquirrelCageMag_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        if self.hole is None:
            hole_val = None
        else:
            hole_val = list()
            for obj in self.hole:
                hole_val.append(obj.copy())
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
            hole=hole_val,
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

        self.hole = None
        # Set to None the properties inherited from LamSquirrelCage
        super(LamSquirrelCageMag, self)._set_None()

    def _get_hole(self):
        """getter of hole"""
        if self._hole is not None:
            for obj in self._hole:
                if obj is not None:
                    obj.parent = self
        return self._hole

    def _set_hole(self, value):
        """setter of hole"""
        if type(value) is list:
            for ii, obj in enumerate(value):
                if isinstance(obj, str):  # Load from file
                    try:
                        obj = load_init_dict(obj)[1]
                    except Exception as e:
                        self.get_logger().error(
                            "Error while loading " + obj + ", setting None instead"
                        )
                        obj = None
                        value[ii] = None
                if type(obj) is dict:
                    class_obj = import_class(
                        "pyleecan.Classes", obj.get("__class__"), "hole"
                    )
                    value[ii] = class_obj(init_dict=obj)
                if value[ii] is not None:
                    value[ii].parent = self
        if value == -1:
            value = list()
        check_var("hole", value, "[Hole]")
        self._hole = value

    hole = property(
        fget=_get_hole,
        fset=_set_hole,
        doc="""lamination Hole

        :Type: [Hole]
        """,
    )
