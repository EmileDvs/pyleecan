# File generated according to Generator/ClassesRef/Machine/Shaft.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Machine/Shaft"""

from os import linesep
from sys import getsizeof

import numpy as np
from matplotlib.patches import Patch
from pyleecan.Classes.Arc1 import Arc1
from pyleecan.Classes.Circle import Circle
from pyleecan.Classes.Segment import Segment
from pyleecan.Classes.SurfLine import SurfLine
from pyleecan.Classes._check import check_var
from pyleecan.Classes._frozen import FrozenClass
from pyleecan.definitions import config_dict
from pyleecan.Functions.Load.import_class import import_class
from pyleecan.Functions.get_logger import get_logger
from pyleecan.Functions.init_fig import init_fig
from pyleecan.Functions.labels import (
    BOUNDARY_PROP_LAB,
    NO_LAM_LAB,
    SHAFTR_LAB,
    SHAFTSL_LAB,
    SHAFTSR_LAB,
    SHAFT_LAB,
)
from pyleecan.Functions.load import load_init_dict
from pyleecan.Functions.save import save


class Shaft(FrozenClass):
    """machine shaft"""

    VERSION = 1
    SHAFT_COLOR = config_dict["PLOT"]["COLOR_DICT"]["SHAFT_COLOR"]

    # cf Methods.Machine.Shaft.build_geometry
    def build_geometry(self, sym=1, alpha=0, delta=0):
        """Build the geometry of the shaft

        Parameters
        ----------
        self : Shaft
            Shaft Object
        sym : int
            Symmetry factor (1= full machine, 2= half of the machine...)
        alpha : float
            Angle for rotation [rad]
        delta : complex
            Complex value for translation

        Returns
        -------
        surf_list : list
            list of surfaces needed to draw the lamination

        """
        surf_list = list()

        if sym == 1:
            surf_list.append(
                Circle(
                    radius=self.Drsh / 2,
                    label=NO_LAM_LAB + "_" + SHAFT_LAB,
                    center=0,
                    point_ref=0,
                )
            )
        else:
            begin = self.Drsh / 2
            end = begin * np.exp(1j * 2 * np.pi / sym)
            surface = SurfLine(
                line_list=[
                    Segment(0, begin, prop_dict={BOUNDARY_PROP_LAB: SHAFTSR_LAB}),
                    Arc1(
                        begin,
                        end,
                        self.Drsh / 2,
                        prop_dict={BOUNDARY_PROP_LAB: SHAFTR_LAB},
                    ),
                    Segment(end, 0, prop_dict={BOUNDARY_PROP_LAB: SHAFTSL_LAB}),
                ],
                label=NO_LAM_LAB + "_" + SHAFT_LAB,
                point_ref=0,
            )

            surf_list.append(surface)
        for surf in surf_list:
            surf.rotate(alpha)
            surf.translate(delta)
        return surf_list

    # cf Methods.Machine.Shaft.comp_mass
    def comp_mass(self):
        """Computation of the Shaft mass

        Parameters
        ----------
        self: Shaft
            A Shaft object
        Returns
        -------
        M_shaft: float
            Mass of the Shaft [kg]

        """
        if self.Lshaft is None:
            return 0
        else:
            return (
                self.Lshaft * np.pi * ((self.Drsh / 2) ** 2) * self.mat_type.struct.rho
            )

    # cf Methods.Machine.Shaft.plot
    def plot(
        self,
        fig=None,
        ax=None,
        sym=1,
        alpha=0,
        delta=0,
        is_edge_only=False,
        edgecolor=None,
        is_show_fig=True,
    ):
        """Plot the Shaft in a matplotlib fig

        Parameters
        ----------
        self : Shaft
            A Shaft object
        fig : Matplotlib.figure.Figure
            existing figure to use if None create a new one
        ax : Matplotlib.axes.Axes object
            Axis on which to plot the data
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

        Returns
        -------
        fig : Matplotlib.figure.Figure
            Figure containing the plot
        ax : Matplotlib.axes.Axes object
            Axis containing the plot
        """

        (fig, ax, patch_leg, label_leg) = init_fig(fig=fig, ax=ax, shape="rectangle")
        # Get the shaft surface(s)
        surf_list = self.build_geometry(sym=sym, alpha=alpha, delta=delta)
        patches = list()
        for surf in surf_list:
            patches.extend(
                surf.get_patches(
                    color=self.SHAFT_COLOR,
                    is_edge_only=is_edge_only,
                    edgecolor=edgecolor,
                )
            )
        ax.set_xlabel("(m)")
        ax.set_ylabel("(m)")
        ax.set_title("Shaft")
        for patch in patches:
            ax.add_patch(patch)
        ax.axis("equal")

        # The Lamination is centered in the figure
        Lim = self.Drsh * 0.6
        ax.set_xlim(-Lim, Lim)
        ax.set_ylim(-Lim, Lim)

        # Add legend
        if not is_edge_only:
            patch_leg.append(Patch(color=self.SHAFT_COLOR))
            label_leg.append("Shaft")

            ax.legend(patch_leg, label_leg)
        if is_show_fig:
            fig.show()
        return fig, ax

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self, Lshaft=0.442, mat_type=-1, Drsh=0.045, init_dict=None, init_str=None
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
            if "Lshaft" in list(init_dict.keys()):
                Lshaft = init_dict["Lshaft"]
            if "mat_type" in list(init_dict.keys()):
                mat_type = init_dict["mat_type"]
            if "Drsh" in list(init_dict.keys()):
                Drsh = init_dict["Drsh"]
        # Set the properties (value check and convertion are done in setter)
        self.parent = None
        self.Lshaft = Lshaft
        self.mat_type = mat_type
        self.Drsh = Drsh

        # The class is frozen, for now it's impossible to add new properties
        self._freeze()

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        Shaft_str = ""
        if self.parent is None:
            Shaft_str += "parent = None " + linesep
        else:
            Shaft_str += "parent = " + str(type(self.parent)) + " object" + linesep
        Shaft_str += "Lshaft = " + str(self.Lshaft) + linesep
        if self.mat_type is not None:
            tmp = self.mat_type.__str__().replace(linesep, linesep + "\t").rstrip("\t")
            Shaft_str += "mat_type = " + tmp
        else:
            Shaft_str += "mat_type = None" + linesep + linesep
        Shaft_str += "Drsh = " + str(self.Drsh) + linesep
        return Shaft_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False
        if other.Lshaft != self.Lshaft:
            return False
        if other.mat_type != self.mat_type:
            return False
        if other.Drsh != self.Drsh:
            return False
        return True

    def compare(self, other, name="self", ignore_list=None, is_add_value=False):
        """Compare two objects and return list of differences"""

        if ignore_list is None:
            ignore_list = list()
        if type(other) != type(self):
            return ["type(" + name + ")"]
        diff_list = list()
        if (
            other._Lshaft is not None
            and self._Lshaft is not None
            and np.isnan(other._Lshaft)
            and np.isnan(self._Lshaft)
        ):
            pass
        elif other._Lshaft != self._Lshaft:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._Lshaft)
                    + ", other="
                    + str(other._Lshaft)
                    + ")"
                )
                diff_list.append(name + ".Lshaft" + val_str)
            else:
                diff_list.append(name + ".Lshaft")
        if (other.mat_type is None and self.mat_type is not None) or (
            other.mat_type is not None and self.mat_type is None
        ):
            diff_list.append(name + ".mat_type None mismatch")
        elif self.mat_type is not None:
            diff_list.extend(
                self.mat_type.compare(
                    other.mat_type,
                    name=name + ".mat_type",
                    ignore_list=ignore_list,
                    is_add_value=is_add_value,
                )
            )
        if (
            other._Drsh is not None
            and self._Drsh is not None
            and np.isnan(other._Drsh)
            and np.isnan(self._Drsh)
        ):
            pass
        elif other._Drsh != self._Drsh:
            if is_add_value:
                val_str = (
                    " (self=" + str(self._Drsh) + ", other=" + str(other._Drsh) + ")"
                )
                diff_list.append(name + ".Drsh" + val_str)
            else:
                diff_list.append(name + ".Drsh")
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object
        S += getsizeof(self.Lshaft)
        S += getsizeof(self.mat_type)
        S += getsizeof(self.Drsh)
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

        Shaft_dict = dict()
        Shaft_dict["Lshaft"] = self.Lshaft
        if self.mat_type is None:
            Shaft_dict["mat_type"] = None
        else:
            Shaft_dict["mat_type"] = self.mat_type.as_dict(
                type_handle_ndarray=type_handle_ndarray,
                keep_function=keep_function,
                **kwargs
            )
        Shaft_dict["Drsh"] = self.Drsh
        # The class name is added to the dict for deserialisation purpose
        Shaft_dict["__class__"] = "Shaft"
        return Shaft_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        Lshaft_val = self.Lshaft
        if self.mat_type is None:
            mat_type_val = None
        else:
            mat_type_val = self.mat_type.copy()
        Drsh_val = self.Drsh
        # Creates new object of the same type with the copied properties
        obj_copy = type(self)(Lshaft=Lshaft_val, mat_type=mat_type_val, Drsh=Drsh_val)
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        self.Lshaft = None
        if self.mat_type is not None:
            self.mat_type._set_None()
        self.Drsh = None

    def _get_Lshaft(self):
        """getter of Lshaft"""
        return self._Lshaft

    def _set_Lshaft(self, value):
        """setter of Lshaft"""
        check_var("Lshaft", value, "float", Vmin=0)
        self._Lshaft = value

    Lshaft = property(
        fget=_get_Lshaft,
        fset=_set_Lshaft,
        doc="""length of the rotor shaft [m] (used for weight & cost estimation only)

        :Type: float
        :min: 0
        """,
    )

    def _get_mat_type(self):
        """getter of mat_type"""
        return self._mat_type

    def _set_mat_type(self, value):
        """setter of mat_type"""
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
                "pyleecan.Classes", value.get("__class__"), "mat_type"
            )
            value = class_obj(init_dict=value)
        elif type(value) is int and value == -1:  # Default constructor
            Material = import_class("pyleecan.Classes", "Material", "mat_type")
            value = Material()
        check_var("mat_type", value, "Material")
        self._mat_type = value

        if self._mat_type is not None:
            self._mat_type.parent = self

    mat_type = property(
        fget=_get_mat_type,
        fset=_set_mat_type,
        doc="""Shaft's Material

        :Type: Material
        """,
    )

    def _get_Drsh(self):
        """getter of Drsh"""
        return self._Drsh

    def _set_Drsh(self, value):
        """setter of Drsh"""
        check_var("Drsh", value, "float", Vmin=0)
        self._Drsh = value

    Drsh = property(
        fget=_get_Drsh,
        fset=_set_Drsh,
        doc="""diameter of the rotor shaft [m], used to estimate bearing diameter for friction losses

        :Type: float
        :min: 0
        """,
    )
