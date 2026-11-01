# File generated according to Generator/ClassesRef/Machine/Frame.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Machine/Frame"""

from os import linesep
from sys import getsizeof

import numpy as np
from matplotlib.patches import Patch
from pyleecan.Classes.Segment import Segment
from pyleecan.Classes.SurfLine import SurfLine
from pyleecan.Classes.SurfRing import SurfRing

from pyleecan.Classes._check import check_var
from pyleecan.Classes._frozen import FrozenClass
from pyleecan.Classes.Arc1 import Arc1
from pyleecan.Classes.Circle import Circle
from pyleecan.definitions import config_dict
from pyleecan.Functions.get_logger import get_logger
from pyleecan.Functions.init_fig import init_fig
from pyleecan.Functions.load import load_init_dict
from pyleecan.Functions.Load.import_class import import_class
from pyleecan.Functions.save import save


class Frame(FrozenClass):
    """machine frame"""

    VERSION = 1
    FRAME_COLOR = config_dict["PLOT"]["COLOR_DICT"]["FRAME_COLOR"]

    # cf Methods.Machine.Frame.build_geometry
    def build_geometry(self, sym=1, alpha=0, delta=0):
        """Build the geometry of the Frame

        Parameters
        ----------
        self : Frame
            Frame Object
        sym : int
            symmetry factor (1= full machine, 2= half of the machine...)
        alpha : float
            Angle for rotation [rad]
        delta : complex
            Complex value for translation

        Returns
        -------
        surf_list : list
            list of surface

        """
        surf_list = list()
        # If there is a frame...
        if self.comp_height_eq() != 0:
            if sym == 1:  # No symmetry / full frame
                out_surf = Circle(
                    radius=self.Rext,
                    label="Frame_Outter",
                    center=0,
                    point_ref=self.Rint + (self.Rext - self.Rint) / 2,
                )
                in_surf = Circle(
                    radius=self.Rint, label="Frame_Inner", center=0, point_ref=0
                )
                surf_list = [
                    SurfRing(
                        out_surf=out_surf,
                        in_surf=in_surf,
                        label="Frame",
                        point_ref=self.Rint + (self.Rext - self.Rint) / 2,
                    )
                ]
            else:  # Part of the frame
                Z0 = self.Rint
                Z3 = Z0 * np.exp(1j * 2 * np.pi / sym)
                Z1 = self.Rext
                Z2 = Z1 * np.exp(1j * 2 * np.pi / sym)
                curve_list = list()
                curve_list.append(Segment(Z0, Z1))
                curve_list.append(Arc1(Z1, Z2, self.Rext))
                curve_list.append(Segment(Z2, Z3))
                curve_list.append(Arc1(Z3, Z0, -self.Rint, is_trigo_direction=False))
                surf_frame = SurfLine(
                    line_list=curve_list,
                    label="Frame",
                    point_ref=self.Rint + (self.Rext - self.Rint) / 2,
                )
                surf_list.append(surf_frame)

            # Apply the transformations
            for surf in surf_list:
                surf.rotate(alpha)
                surf.translate(delta)

        return surf_list

    # cf Methods.Machine.Frame.comp_height_eq
    def comp_height_eq(self):
        """Computation of the Frame equivalent Height for the mechanical model

        Parameters
        ----------
        self : Frame
            A Frame object

        Returns
        -------
        Hfra: float
            Equivalent Height of the Frame [m]

        """

        return self.Rext - self.Rint

    # cf Methods.Machine.Frame.comp_mass
    def comp_mass(self):
        """Compute the mass of the Frame

        Parameters
        ----------
        self : Frame
            A Frame object

        Returns
        -------
        Mfra: float
            Mass of the Frame [kg]

        """

        Vfra = self.comp_volume()

        # Mass computation
        if Vfra == 0:
            return 0
        else:
            return Vfra * self.mat_type.struct.rho

    # cf Methods.Machine.Frame.comp_surface
    def comp_surface(self):
        """Compute the surface of the Frame

        Parameters
        ----------
        self : Frame
            A Frame object

        Returns
        -------
        Sfra: float
            Surface of the Frame [m**2]

        """

        # Surface of the external disk
        S_ext = (self.Rext**2) * np.pi
        # Surface of the internal disk
        S_int = (self.Rint**2) * np.pi

        return S_ext - S_int

    # cf Methods.Machine.Frame.comp_volume
    def comp_volume(self):
        """Compute the volume of the Frame

        Parameters
        ----------
        self : Frame
            A Frame object

        Returns
        -------
        Vfra: float
            Volume of the Frame [m**3]

        """

        Sfra = self.comp_surface()
        if self.Lfra is None:
            return 0
        else:
            return Sfra * self.Lfra

    # cf Methods.Machine.Frame.get_length
    def get_length(self):
        """Return the length of the Frame

        Parameters
        ----------
        self : Frame
            A Frame object

        Returns
        -------
        length: float
            Length of the frame

        """

        if self.comp_height_eq() > 0:
            return self.Lfra
        else:
            return 0

    # cf Methods.Machine.Frame.plot
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
        """Plot the Frame in a matplotlib fig

        Parameters
        ----------
        self : Frame
            A Frame object
        fig : Matplotlib.figure.Figure
            existing figure to use if None create a new one
        ax : Matplotlib.axes.Axes object
            Axis on which to plot the data
        sym : int
            Symmetry factor (1= plot full machine, 2= half of the machine...)
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

        # plot only if the frame has a height >0
        if self.comp_height_eq() != 0:
            (fig, ax, patch_leg, label_leg) = init_fig(
                fig=fig, ax=ax, shape="rectangle"
            )
            surf_list = self.build_geometry(sym=sym, alpha=alpha, delta=delta)
            patches = list()
            for surf in surf_list:
                patches.extend(
                    surf.get_patches(
                        color=self.FRAME_COLOR,
                        is_edge_only=is_edge_only,
                        edgecolor=edgecolor,
                    )
                )

            ax.set_xlabel("(m)")
            ax.set_ylabel("(m)")
            ax.set_title("Frame")
            for patch in patches:
                ax.add_patch(patch)
            ax.axis("equal")

            # The Lamination is centered in the figure
            Lim = self.Rext * 1.1
            ax.set_xlim(-Lim, Lim, auto=True)
            ax.set_ylim(-Lim, Lim, auto=True)

            if not is_edge_only:
                patch_leg.append(Patch(color=self.FRAME_COLOR))
                label_leg.append("Frame")
                ax.legend(patch_leg, label_leg)
            if is_show_fig:
                fig.show()
            return fig, ax

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self, Lfra=0.35, Rint=0.2, Rext=0.2, mat_type=-1, init_dict=None, init_str=None
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
            if "Lfra" in list(init_dict.keys()):
                Lfra = init_dict["Lfra"]
            if "Rint" in list(init_dict.keys()):
                Rint = init_dict["Rint"]
            if "Rext" in list(init_dict.keys()):
                Rext = init_dict["Rext"]
            if "mat_type" in list(init_dict.keys()):
                mat_type = init_dict["mat_type"]
        # Set the properties (value check and convertion are done in setter)
        self.parent = None
        self.Lfra = Lfra
        self.Rint = Rint
        self.Rext = Rext
        self.mat_type = mat_type

        # The class is frozen, for now it's impossible to add new properties
        self._freeze()

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        Frame_str = ""
        if self.parent is None:
            Frame_str += "parent = None " + linesep
        else:
            Frame_str += "parent = " + str(type(self.parent)) + " object" + linesep
        Frame_str += "Lfra = " + str(self.Lfra) + linesep
        Frame_str += "Rint = " + str(self.Rint) + linesep
        Frame_str += "Rext = " + str(self.Rext) + linesep
        if self.mat_type is not None:
            tmp = self.mat_type.__str__().replace(linesep, linesep + "\t").rstrip("\t")
            Frame_str += "mat_type = " + tmp
        else:
            Frame_str += "mat_type = None" + linesep + linesep
        return Frame_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False
        if other.Lfra != self.Lfra:
            return False
        if other.Rint != self.Rint:
            return False
        if other.Rext != self.Rext:
            return False
        if other.mat_type != self.mat_type:
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
            other._Lfra is not None
            and self._Lfra is not None
            and np.isnan(other._Lfra)
            and np.isnan(self._Lfra)
        ):
            pass
        elif other._Lfra != self._Lfra:
            if is_add_value:
                val_str = (
                    " (self=" + str(self._Lfra) + ", other=" + str(other._Lfra) + ")"
                )
                diff_list.append(name + ".Lfra" + val_str)
            else:
                diff_list.append(name + ".Lfra")
        if (
            other._Rint is not None
            and self._Rint is not None
            and np.isnan(other._Rint)
            and np.isnan(self._Rint)
        ):
            pass
        elif other._Rint != self._Rint:
            if is_add_value:
                val_str = (
                    " (self=" + str(self._Rint) + ", other=" + str(other._Rint) + ")"
                )
                diff_list.append(name + ".Rint" + val_str)
            else:
                diff_list.append(name + ".Rint")
        if (
            other._Rext is not None
            and self._Rext is not None
            and np.isnan(other._Rext)
            and np.isnan(self._Rext)
        ):
            pass
        elif other._Rext != self._Rext:
            if is_add_value:
                val_str = (
                    " (self=" + str(self._Rext) + ", other=" + str(other._Rext) + ")"
                )
                diff_list.append(name + ".Rext" + val_str)
            else:
                diff_list.append(name + ".Rext")
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
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object
        S += getsizeof(self.Lfra)
        S += getsizeof(self.Rint)
        S += getsizeof(self.Rext)
        S += getsizeof(self.mat_type)
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

        Frame_dict = dict()
        Frame_dict["Lfra"] = self.Lfra
        Frame_dict["Rint"] = self.Rint
        Frame_dict["Rext"] = self.Rext
        if self.mat_type is None:
            Frame_dict["mat_type"] = None
        else:
            Frame_dict["mat_type"] = self.mat_type.as_dict(
                type_handle_ndarray=type_handle_ndarray,
                keep_function=keep_function,
                **kwargs
            )
        # The class name is added to the dict for deserialisation purpose
        Frame_dict["__class__"] = "Frame"
        return Frame_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        Lfra_val = self.Lfra
        Rint_val = self.Rint
        Rext_val = self.Rext
        if self.mat_type is None:
            mat_type_val = None
        else:
            mat_type_val = self.mat_type.copy()
        # Creates new object of the same type with the copied properties
        obj_copy = type(self)(
            Lfra=Lfra_val, Rint=Rint_val, Rext=Rext_val, mat_type=mat_type_val
        )
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        self.Lfra = None
        self.Rint = None
        self.Rext = None
        if self.mat_type is not None:
            self.mat_type._set_None()

    def _get_Lfra(self):
        """getter of Lfra"""
        return self._Lfra

    def _set_Lfra(self, value):
        """setter of Lfra"""
        check_var("Lfra", value, "float", Vmin=0)
        self._Lfra = value

    Lfra = property(
        fget=_get_Lfra,
        fset=_set_Lfra,
        doc="""frame length [m]

        :Type: float
        :min: 0
        """,
    )

    def _get_Rint(self):
        """getter of Rint"""
        return self._Rint

    def _set_Rint(self, value):
        """setter of Rint"""
        check_var("Rint", value, "float", Vmin=0)
        self._Rint = value

    Rint = property(
        fget=_get_Rint,
        fset=_set_Rint,
        doc="""frame internal radius

        :Type: float
        :min: 0
        """,
    )

    def _get_Rext(self):
        """getter of Rext"""
        return self._Rext

    def _set_Rext(self, value):
        """setter of Rext"""
        check_var("Rext", value, "float", Vmin=0)
        self._Rext = value

    Rext = property(
        fget=_get_Rext,
        fset=_set_Rext,
        doc="""Frame external radius

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
        doc="""Frame material

        :Type: Material
        """,
    )
