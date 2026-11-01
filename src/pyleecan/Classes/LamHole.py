# -*- coding: utf-8 -*-
# File generated according to Generator/ClassesRef/Machine/LamHole.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Machine/LamHole
"""

from os import linesep
from sys import getsizeof
from logging import getLogger
from pyleecan.Classes._check import check_var, raise_
from pyleecan.Functions.get_logger import get_logger
from pyleecan.Functions.save import save
from pyleecan.Functions.load import load_init_dict
from pyleecan.Functions.Load.import_class import import_class
from copy import deepcopy
from pyleecan.Classes.LamH import LamH

# Import all class method
# Try/catch to remove unnecessary dependencies in unused method
from numpy import exp, pi
from pyleecan.Functions.labels import decode_label, HOLEM_LAB
from pyleecan.Classes.Lamination import Lamination
from pyleecan.Functions.Geometry.transform_hole_surf import transform_hole_surf

from numpy import isnan
from pyleecan.Classes._check import InitUnKnowClassError


class LamHole(LamH):
    """Lamination with Hole with or without magnet or winding"""

    VERSION = 1

    # cf Methods.Machine.LamHole._plot_arrow_mag
    def _plot_arrow_mag(
        self,
        ax=None,
        sym=1,
        alpha=0,
        delta=0,
    ):
        """Plot the magnetization direction as arrow on top of the lamination
        (meant to be called by LamHole.plot)

        Parameters
        ----------
        self : LamHole
            A LamHole object
        ax : Matplotlib.axes.Axes object
            Axis on which to plot the arrow
        sym : int
            Symmetry factor (1= plot full machine, 2= half of the machine...)
        alpha : float
            angle for rotation (Default value = 0) [rad]
        delta : complex
            complex for translation (Default value = 0)
        """

        for hole in self.hole:
            H = hole.comp_height()
            mag_dict = hole.comp_magnetization_dict()
            for magnet_name, mag_dir in mag_dict.items():
                # Get the correct surface
                mag_surf = None
                mag_id = int(magnet_name.split("_")[-1])
                mag = hole.get_magnet_by_id(mag_id)
                if mag is not None:
                    for surf in hole.build_geometry():
                        label_dict = decode_label(surf.label)
                        if (
                            HOLEM_LAB in label_dict["surf_type"]
                            and label_dict["T_id"] == mag_id
                        ):
                            mag_surf = surf
                            break
                    # Create arrow coordinates
                    Zh = hole.Zh
                    for ii in range(int(Zh / sym)):
                        off = pi if ii % 2 == 1 else 0
                        if mag is not None and mag.type_magnetization == 3:
                            off -= pi / 2
                        Z1 = (mag_surf.point_ref + delta) * exp(
                            1j * (ii * 2 * pi / Zh + pi / Zh + alpha)
                        )
                        Z2 = (
                            mag_surf.point_ref
                            + delta
                            + H / 5 * exp(1j * (mag_dir + off))
                        ) * exp(1j * (ii * 2 * pi / Zh + pi / Zh + alpha))
                        ax.annotate(
                            text="",
                            xy=(Z2.real, Z2.imag),
                            xytext=(Z1.real, Z1.imag),
                            arrowprops=dict(arrowstyle="->", linewidth=1, color="b"),
                        )

    # cf Methods.Machine.LamHole.build_geometry
    def build_geometry(self, sym=1, alpha=0, delta=0, is_circular_radius=False):
        """Build the geometry of the LamHole object

        Parameters
        ----------
        self : LamHole
            The LamHole to build in surface
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
        surf_list : list
            list of surfaces needed to draw the lamination

        """

        # getting the Lamination surface
        surf_list = Lamination.build_geometry(
            self,
            sym=sym,
            alpha=alpha,
            delta=delta,
            is_circular_radius=is_circular_radius,
        )

        # Holes surface(s)
        for hole in self.hole:
            # Create the first hole surface(s)
            surf_hole = hole.build_geometry(alpha=pi / hole.Zh)
            surf_list.extend(
                transform_hole_surf(
                    hole_surf_list=surf_hole, Zh=hole.Zh, sym=sym, alpha=0, delta=0
                )
            )

        # Apply the transformations
        for surf in surf_list:
            surf.rotate(alpha)
            surf.translate(delta)

        return surf_list

    # cf Methods.Machine.LamHole.get_hole_list
    def get_hole_list(self):
        """Return the list of all the holes

        Parameters
        ----------
        self : LamHole
            A LamHole object

        Returns
        -------
        hole_list : [Hole]
            List of all the holes
        """
        if self.hole is None:
            self.hole = list()
        return self.hole

    # cf Methods.Machine.LamHole.get_magnet_number
    def get_magnet_number(self, sym=1):
        """Return the number of magnet on the Lamination

        Parameters
        ----------
        self : LamHole
            A LamHole object
        sym : int
            Symmetry factor (1= full machine, 2= half of the machine...)

        Returns
        -------
        N_mag : int
            Number of magnets on the lamination
        """

        # Each hole can have several magnets
        nb_mag_per_hole = 0
        for hole in self.get_hole_list():
            nb_mag_per_hole += len(hole.get_magnet_dict())
        # There are Zs / sym holes of each set
        return int(self.get_Zs() / sym * nb_mag_per_hole)

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
        hole=-1,
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
        # Call LamH init
        super(LamHole, self).__init__(
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
        # The class is frozen (in LamH init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        LamHole_str = ""
        # Get the properties inherited from LamH
        LamHole_str += super(LamHole, self).__str__()
        if len(self.hole) == 0:
            LamHole_str += "hole = []" + linesep
        for ii in range(len(self.hole)):
            tmp = self.hole[ii].__str__().replace(linesep, linesep + "\t") + linesep
            LamHole_str += "hole[" + str(ii) + "] =" + tmp + linesep + linesep
        return LamHole_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from LamH
        if not super(LamHole, self).__eq__(other):
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

        # Check the properties inherited from LamH
        diff_list.extend(
            super(LamHole, self).compare(
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

        # Get size of the properties inherited from LamH
        S += super(LamHole, self).__sizeof__()
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

        # Get the properties inherited from LamH
        LamHole_dict = super(LamHole, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs
        )
        if self.hole is None:
            LamHole_dict["hole"] = None
        else:
            LamHole_dict["hole"] = list()
            for obj in self.hole:
                if obj is not None:
                    LamHole_dict["hole"].append(
                        obj.as_dict(
                            type_handle_ndarray=type_handle_ndarray,
                            keep_function=keep_function,
                            **kwargs
                        )
                    )
                else:
                    LamHole_dict["hole"].append(None)
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        LamHole_dict["__class__"] = "LamHole"
        return LamHole_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        if self.hole is None:
            hole_val = None
        else:
            hole_val = list()
            for obj in self.hole:
                hole_val.append(obj.copy())
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
        # Set to None the properties inherited from LamH
        super(LamHole, self)._set_None()

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
