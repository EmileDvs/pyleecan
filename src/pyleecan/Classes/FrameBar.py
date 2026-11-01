# File generated according to Generator/ClassesRef/Machine/FrameBar.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Machine/FrameBar"""

from copy import deepcopy
from os import linesep
from sys import getsizeof

import numpy as np
from pyleecan.Classes.Segment import Segment
from pyleecan.Classes.SurfLine import SurfLine

from pyleecan.Classes._check import check_var
from pyleecan.Classes.Arc1 import Arc1
from pyleecan.Classes.Arc2 import Arc2
from pyleecan.Classes.Frame import Frame
from pyleecan.Functions.get_logger import get_logger
from pyleecan.Functions.load import load_init_dict
from pyleecan.Functions.save import save


class FrameBar(Frame):
    """machine frame with polar structural bars between frame and outer lamination"""

    VERSION = 1

    # cf Methods.Machine.FrameBar.build_geometry
    def build_geometry(self, sym=1, alpha=0, delta=0):
        """Build the geometry of the Frame with structural Bars

        Parameters
        ----------
        self : FrameBar
            FrameBar Object
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

        # Build Frame Geometry
        surf_list_frame = Frame.build_geometry(self, sym, alpha, delta)
        # Build Bar Geometry
        surf_list_bar = self.build_geometry_bar(sym, alpha, delta)

        surf_list = surf_list_frame + surf_list_bar
        return surf_list

    # cf Methods.Machine.FrameBar.build_geometry_bar
    def build_geometry_bar(self, sym=1, alpha=0, delta=0):
        """Build the geometry of the structural bars

        Parameters
        ----------
        self : FrameBar
            FrameBar Object
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
        h_gap = self.comp_height_gap()
        if h_gap > 0:
            lam_outer = self.parent.get_lam_list()[-1]
            ###Rectangular Shape
            # #Define Points
            # Z0 = lam_outer.Rext
            # Z1 = Z0 + self.wbar * 1j / 2.0
            # Z2 = Z1 + h_gap
            # Z3 = Z2 - self.wbar * 1j
            # Z4 = Z0 - self.wbar * 1j / 2.0
            # #Define Lines
            # curve_list = list()
            # curve_list.append(Segment(Z1, Z2))
            # curve_list.append(Segment(Z2, Z3))
            # curve_list.append(Segment(Z3, Z4))
            # curve_list.append(Segment(Z4, Z1))

            ###Circular Shape
            # Define Points
            Z0 = lam_outer.Rext
            rot_angle = np.arcsin(self.wbar / 2.0 / Z0)
            Z1 = Z0 * np.exp(rot_angle * -1j)
            Z2 = (Z0 + h_gap) * np.exp(rot_angle * -1j)
            Z3 = (Z0 + h_gap) * np.exp(rot_angle * 1j)
            Z4 = Z0 * np.exp(rot_angle * 1j)
            # Define Lines
            curve_list = list()
            curve_list.append(Segment(Z1, Z2))
            curve_list.append(Arc1(Z2, Z3, self.Rint))
            curve_list.append(Segment(Z3, Z4))
            curve_list.append(Arc2(Z4, 0, angle=-rot_angle))
            # Define Surface
            surf_bar = SurfLine(
                line_list=curve_list,
                label="Bar",
                point_ref=self.Rext - h_gap / 2,
            )
            # Rotate surface so bars are evenly distributed
            surf_list.append(deepcopy(surf_bar))
            bar_angle = 2 * np.pi / self.Nbar
            for i in range(1, self.Nbar):
                surf_bar.rotate(bar_angle)
                surf_list.append(deepcopy(surf_bar))

        # Apply the transformations
        for surf in surf_list:
            surf.rotate(alpha)
            surf.translate(delta)

        return surf_list

    # cf Methods.Machine.FrameBar.comp_height_gap
    def comp_height_gap(self):
        """Computation of the Height of the gap between the Frame and Outer Lamination

        Parameters
        ----------
        self : FrameBar
            A FrameBar object

        Returns
        -------
        Hgap: float
            Height of the Gap [m]

        """
        lam_outer = self.parent.get_lam_list()[-1]

        return self.Rint - lam_outer.Rext

    # cf Methods.Machine.FrameBar.comp_surface
    def comp_surface(self):
        """Compute the surface of the Frame including the structural bars

        Parameters
        ----------
        self : FrameBar
            A FrameBar object

        Returns
        -------
        Sfra: float
            Surface of the Frame [m**2]

        """

        # Outer Frame Surface
        S_ext = (self.Rext**2) * np.pi
        S_int = (self.Rint**2) * np.pi
        S_outer = S_ext - S_int

        # Bar Surface
        S_bar = self.comp_surface_bar()

        return S_outer + S_bar

    # cf Methods.Machine.FrameBar.comp_surface_bar
    def comp_surface_bar(self):
        """Compute the surface of the structural Bars

        Parameters
        ----------
        self : FrameBar
            A FrameBar object

        Returns
        -------
        Sbar: float
            Surface of the structural Bars [m**2]

        """
        # #Calculation for rectangular shape
        # n_bar = self._get_Nbar()
        # w_bar = self._get_wbar()
        # h_gap = self.comp_height_gap()
        # Sbar = n_bar * w_bar * h_gap

        # Calculation for circular shape
        r_out = self._get_Rint()
        h_gap = self.comp_height_gap()
        r_in = r_out - h_gap
        rot_angle = 2 * np.arcsin(self.wbar / 2.0 / r_in)
        Sbar = self.Nbar * np.pi * (r_out**2 - r_in**2) * rot_angle / (2 * np.pi)

        return Sbar

    # cf Methods.Machine.FrameBar.comp_surface_gap
    def comp_surface_gap(self):
        """Compute the surface of the Gap between the Frame and outer Lamination

        Parameters
        ----------
        self : FrameBar
            A FrameBar object

        Returns
        -------
        Sgap: float
            Surface of the Gap [m**2]

        """

        # Surface of the external disk
        S_ext = (self.Rext**2) * np.pi
        # Surface of the internal disk
        S_int = (self.Rint**2) * np.pi
        # Surface of the bars
        S_bar = self.comp_surface_bar()

        Sgap = S_ext - S_int - S_bar

        return Sgap

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
        Nbar=8,
        wbar=0.01,
        Lfra=0.35,
        Rint=0.2,
        Rext=0.2,
        mat_type=-1,
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
            if "Nbar" in list(init_dict.keys()):
                Nbar = init_dict["Nbar"]
            if "wbar" in list(init_dict.keys()):
                wbar = init_dict["wbar"]
            if "Lfra" in list(init_dict.keys()):
                Lfra = init_dict["Lfra"]
            if "Rint" in list(init_dict.keys()):
                Rint = init_dict["Rint"]
            if "Rext" in list(init_dict.keys()):
                Rext = init_dict["Rext"]
            if "mat_type" in list(init_dict.keys()):
                mat_type = init_dict["mat_type"]
        # Set the properties (value check and convertion are done in setter)
        self.Nbar = Nbar
        self.wbar = wbar
        # Call Frame init
        super(FrameBar, self).__init__(
            Lfra=Lfra, Rint=Rint, Rext=Rext, mat_type=mat_type
        )
        # The class is frozen (in Frame init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        FrameBar_str = ""
        # Get the properties inherited from Frame
        FrameBar_str += super(FrameBar, self).__str__()
        FrameBar_str += "Nbar = " + str(self.Nbar) + linesep
        FrameBar_str += "wbar = " + str(self.wbar) + linesep
        return FrameBar_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from Frame
        if not super(FrameBar, self).__eq__(other):
            return False
        if other.Nbar != self.Nbar:
            return False
        if other.wbar != self.wbar:
            return False
        return True

    def compare(self, other, name="self", ignore_list=None, is_add_value=False):
        """Compare two objects and return list of differences"""

        if ignore_list is None:
            ignore_list = list()
        if type(other) != type(self):
            return ["type(" + name + ")"]
        diff_list = list()

        # Check the properties inherited from Frame
        diff_list.extend(
            super(FrameBar, self).compare(
                other, name=name, ignore_list=ignore_list, is_add_value=is_add_value
            )
        )
        if other._Nbar != self._Nbar:
            if is_add_value:
                val_str = (
                    " (self=" + str(self._Nbar) + ", other=" + str(other._Nbar) + ")"
                )
                diff_list.append(name + ".Nbar" + val_str)
            else:
                diff_list.append(name + ".Nbar")
        if (
            other._wbar is not None
            and self._wbar is not None
            and np.isnan(other._wbar)
            and np.isnan(self._wbar)
        ):
            pass
        elif other._wbar != self._wbar:
            if is_add_value:
                val_str = (
                    " (self=" + str(self._wbar) + ", other=" + str(other._wbar) + ")"
                )
                diff_list.append(name + ".wbar" + val_str)
            else:
                diff_list.append(name + ".wbar")
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object

        # Get size of the properties inherited from Frame
        S += super(FrameBar, self).__sizeof__()
        S += getsizeof(self.Nbar)
        S += getsizeof(self.wbar)
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

        # Get the properties inherited from Frame
        FrameBar_dict = super(FrameBar, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs
        )
        FrameBar_dict["Nbar"] = self.Nbar
        FrameBar_dict["wbar"] = self.wbar
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        FrameBar_dict["__class__"] = "FrameBar"
        return FrameBar_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        Nbar_val = self.Nbar
        wbar_val = self.wbar
        Lfra_val = self.Lfra
        Rint_val = self.Rint
        Rext_val = self.Rext
        if self.mat_type is None:
            mat_type_val = None
        else:
            mat_type_val = self.mat_type.copy()
        # Creates new object of the same type with the copied properties
        obj_copy = type(self)(
            Nbar=Nbar_val,
            wbar=wbar_val,
            Lfra=Lfra_val,
            Rint=Rint_val,
            Rext=Rext_val,
            mat_type=mat_type_val,
        )
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        self.Nbar = None
        self.wbar = None
        # Set to None the properties inherited from Frame
        super(FrameBar, self)._set_None()

    def _get_Nbar(self):
        """getter of Nbar"""
        return self._Nbar

    def _set_Nbar(self, value):
        """setter of Nbar"""
        check_var("Nbar", value, "int", Vmin=1)
        self._Nbar = value

    Nbar = property(
        fget=_get_Nbar,
        fset=_set_Nbar,
        doc="""Number of bars

        :Type: int
        :min: 1
        """,
    )

    def _get_wbar(self):
        """getter of wbar"""
        return self._wbar

    def _set_wbar(self, value):
        """setter of wbar"""
        check_var("wbar", value, "float", Vmin=0)
        self._wbar = value

    wbar = property(
        fget=_get_wbar,
        fset=_set_wbar,
        doc="""Width of bars

        :Type: float
        :min: 0
        """,
    )
