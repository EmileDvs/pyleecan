# -*- coding: utf-8 -*-
# File generated according to Generator/ClassesRef/Machine/CondType13.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Machine/CondType13
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
from pyleecan.Classes.Conductor import Conductor

# Import all class method
# Try/catch to remove unnecessary dependencies in unused method
from pyleecan.definitions import config_dict

import numpy as np
from pyleecan.Classes._check import InitUnKnowClassError


class CondType13(Conductor):
    """parallel stranded conductor consisting of at least a single round wire"""

    VERSION = 1
    COND_COLOR = config_dict["PLOT"]["COLOR_DICT"]["PHASE_COLORS"][0].copy()
    INS_COLOR = config_dict["PLOT"]["COLOR_DICT"]["PHASE_COLORS"][1].copy()

    # cf Methods.Machine.CondType13.comp_height
    def comp_height(self):
        """Compute the height of the conductor

        Parameters
        ----------
        self : CondType13
            A CondType13 object

        Returns
        -------
        H: float
            Height of the conductor [m]

        """

        return (2 * self.Wins_wire + self.Wwire) * self.Nwppc_rad

    # cf Methods.Machine.CondType13.comp_height_wire
    def comp_height_wire(self):
        """Return wire diameter

        Parameters
        ----------
        self : CondType13
            A CondType13 object

        Returns
        -------
        H: float
            Diameter of the wire [m]

        """

        return self.Wwire

    # cf Methods.Machine.CondType13.comp_nb_circumferential_wire
    def comp_nb_circumferential_wire(self):
        """Return number of adjacent wires in circumferential direction

        Parameters
        ----------
        self : CondType13
            A CondType13 object

        Returns
        -------
        Nwppc_tan: int
            Number of adjacent wires in circumferential direction

        """

        return self.Nwppc_tan

    # cf Methods.Machine.CondType13.comp_nb_radial_wire
    def comp_nb_radial_wire(self):
        """Return number of adjacent wires in radial direction

        Parameters
        ----------
        self : CondType13
            A CondType13 object

        Returns
        -------
        Nwppc_tan: int
            Number of adjacent wires in radial direction

        """

        return self.Nwppc_rad

    # cf Methods.Machine.CondType13.comp_surface
    def comp_surface(self):
        """Compute the surface of the conductor

        Parameters
        ----------
        self : CondType13
            A CondType13 object

        Returns
        -------
        S: float
            Surface of the conductor (with insulation) [m**2]

        """

        S = self.comp_height() * self.comp_width()

        return S

    # cf Methods.Machine.CondType13.comp_surface_active
    def comp_surface_active(self):
        """Compute the active surface of the conductor

        Parameters
        ----------
        self : CondType13
            A CondType13 object

        Returns
        -------
        Sact: float
            Surface without insulation [m**2]

        """

        Sact = self.Wwire * self.Wwire * self.Nwppc_tan * self.Nwppc_rad

        return Sact

    # cf Methods.Machine.CondType13.comp_width
    def comp_width(self):
        """Compute the width of the conductor

        Parameters
        ----------
        self : CondType13
            A CondType13 object

        Returns
        -------
        W: float
            Width of the conductor [m]

        """

        return (2 * self.Wins_wire + self.Wwire) * self.Nwppc_tan

    # cf Methods.Machine.CondType13.comp_width_wire
    def comp_width_wire(self):
        """Return wire diameter

        Parameters
        ----------
        self : CondType13
            A CondType13 object

        Returns
        -------
        H: float
            Diameter of the wire [m]

        """

        return self.Wwire

    # cf Methods.Machine.CondType13.is_round_wire
    def is_round_wire(self):
        """Return if wire is round

        Parameters
        ----------
        self : CondType13
            A CondType13 object

        Returns
        -------
        is_round_wire: bool
            is_round_wire is always True since wire is round

        """

        return True

    # cf Methods.Machine.CondType13.plot
    def plot(self, is_show_fig=True, fig=None, ax=None):
        """Plot a Conductor in a matplotlib fig

        Parameters
        ----------
        self : CondType13
            A CondType13 object
        is_show_fig : bool
            To call show at the end of the method
        fig : Matplotlib.figure.Figure
            existing figure to use if None create a new one
        ax : Matplotlib.axes.Axes object
            Axis on which to plot the data

        Returns
        -------
        None
        """

        # TODO

        pass

    # cf Methods.Machine.CondType13.plot_schematics
    def plot_schematics(
        self,
        is_default=False,
        is_add_schematics=True,
        is_add_main_line=True,
        save_path=None,
        is_show_fig=True,
        fig=None,
        ax=None,
    ):
        """Plot the schematics of the slot

        Parameters
        ----------
        self : CondType13
            A CondType13 object
        is_default : bool
            True: plot default schematics, else use current slot values
        is_add_schematics : bool
            True to display the schematics information (W0, H0...)
        is_add_main_line : bool
            True to display "main lines" (slot opening and 0x axis)
        save_path : str
            full path including folder, name and extension of the file to save if save_path is not None
        is_show_fig : bool
            To call show at the end of the method
        fig : Matplotlib.figure.Figure
            existing figure to use if None create a new one
        ax : Matplotlib.axes.Axes object
            Axis on which to plot the data
        """

        # TODO

        pass

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
        Wwire=0.015,
        Wins_cond=0.015,
        Nwppc_rad=1,
        Nwppc_tan=1,
        Wins_wire=0,
        Kwoh=0.5,
        cond_mat=-1,
        ins_mat=-1,
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
            if "Wwire" in list(init_dict.keys()):
                Wwire = init_dict["Wwire"]
            if "Wins_cond" in list(init_dict.keys()):
                Wins_cond = init_dict["Wins_cond"]
            if "Nwppc_rad" in list(init_dict.keys()):
                Nwppc_rad = init_dict["Nwppc_rad"]
            if "Nwppc_tan" in list(init_dict.keys()):
                Nwppc_tan = init_dict["Nwppc_tan"]
            if "Wins_wire" in list(init_dict.keys()):
                Wins_wire = init_dict["Wins_wire"]
            if "Kwoh" in list(init_dict.keys()):
                Kwoh = init_dict["Kwoh"]
            if "cond_mat" in list(init_dict.keys()):
                cond_mat = init_dict["cond_mat"]
            if "ins_mat" in list(init_dict.keys()):
                ins_mat = init_dict["ins_mat"]
        # Set the properties (value check and convertion are done in setter)
        self.Wwire = Wwire
        self.Wins_cond = Wins_cond
        self.Nwppc_rad = Nwppc_rad
        self.Nwppc_tan = Nwppc_tan
        self.Wins_wire = Wins_wire
        self.Kwoh = Kwoh
        # Call Conductor init
        super(CondType13, self).__init__(cond_mat=cond_mat, ins_mat=ins_mat)
        # The class is frozen (in Conductor init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        CondType13_str = ""
        # Get the properties inherited from Conductor
        CondType13_str += super(CondType13, self).__str__()
        CondType13_str += "Wwire = " + str(self.Wwire) + linesep
        CondType13_str += "Wins_cond = " + str(self.Wins_cond) + linesep
        CondType13_str += "Nwppc_rad = " + str(self.Nwppc_rad) + linesep
        CondType13_str += "Nwppc_tan = " + str(self.Nwppc_tan) + linesep
        CondType13_str += "Wins_wire = " + str(self.Wins_wire) + linesep
        CondType13_str += "Kwoh = " + str(self.Kwoh) + linesep
        return CondType13_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from Conductor
        if not super(CondType13, self).__eq__(other):
            return False
        if other.Wwire != self.Wwire:
            return False
        if other.Wins_cond != self.Wins_cond:
            return False
        if other.Nwppc_rad != self.Nwppc_rad:
            return False
        if other.Nwppc_tan != self.Nwppc_tan:
            return False
        if other.Wins_wire != self.Wins_wire:
            return False
        if other.Kwoh != self.Kwoh:
            return False
        return True

    def compare(self, other, name="self", ignore_list=None, is_add_value=False):
        """Compare two objects and return list of differences"""

        if ignore_list is None:
            ignore_list = list()
        if type(other) != type(self):
            return ["type(" + name + ")"]
        diff_list = list()

        # Check the properties inherited from Conductor
        diff_list.extend(
            super(CondType13, self).compare(
                other, name=name, ignore_list=ignore_list, is_add_value=is_add_value
            )
        )
        if (
            other._Wwire is not None
            and self._Wwire is not None
            and np.isnan(other._Wwire)
            and np.isnan(self._Wwire)
        ):
            pass
        elif other._Wwire != self._Wwire:
            if is_add_value:
                val_str = (
                    " (self=" + str(self._Wwire) + ", other=" + str(other._Wwire) + ")"
                )
                diff_list.append(name + ".Wwire" + val_str)
            else:
                diff_list.append(name + ".Wwire")
        if (
            other._Wins_cond is not None
            and self._Wins_cond is not None
            and np.isnan(other._Wins_cond)
            and np.isnan(self._Wins_cond)
        ):
            pass
        elif other._Wins_cond != self._Wins_cond:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._Wins_cond)
                    + ", other="
                    + str(other._Wins_cond)
                    + ")"
                )
                diff_list.append(name + ".Wins_cond" + val_str)
            else:
                diff_list.append(name + ".Wins_cond")
        if other._Nwppc_rad != self._Nwppc_rad:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._Nwppc_rad)
                    + ", other="
                    + str(other._Nwppc_rad)
                    + ")"
                )
                diff_list.append(name + ".Nwppc_rad" + val_str)
            else:
                diff_list.append(name + ".Nwppc_rad")
        if other._Nwppc_tan != self._Nwppc_tan:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._Nwppc_tan)
                    + ", other="
                    + str(other._Nwppc_tan)
                    + ")"
                )
                diff_list.append(name + ".Nwppc_tan" + val_str)
            else:
                diff_list.append(name + ".Nwppc_tan")
        if (
            other._Wins_wire is not None
            and self._Wins_wire is not None
            and np.isnan(other._Wins_wire)
            and np.isnan(self._Wins_wire)
        ):
            pass
        elif other._Wins_wire != self._Wins_wire:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._Wins_wire)
                    + ", other="
                    + str(other._Wins_wire)
                    + ")"
                )
                diff_list.append(name + ".Wins_wire" + val_str)
            else:
                diff_list.append(name + ".Wins_wire")
        if (
            other._Kwoh is not None
            and self._Kwoh is not None
            and np.isnan(other._Kwoh)
            and np.isnan(self._Kwoh)
        ):
            pass
        elif other._Kwoh != self._Kwoh:
            if is_add_value:
                val_str = (
                    " (self=" + str(self._Kwoh) + ", other=" + str(other._Kwoh) + ")"
                )
                diff_list.append(name + ".Kwoh" + val_str)
            else:
                diff_list.append(name + ".Kwoh")
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object

        # Get size of the properties inherited from Conductor
        S += super(CondType13, self).__sizeof__()
        S += getsizeof(self.Wwire)
        S += getsizeof(self.Wins_cond)
        S += getsizeof(self.Nwppc_rad)
        S += getsizeof(self.Nwppc_tan)
        S += getsizeof(self.Wins_wire)
        S += getsizeof(self.Kwoh)
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

        # Get the properties inherited from Conductor
        CondType13_dict = super(CondType13, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs
        )
        CondType13_dict["Wwire"] = self.Wwire
        CondType13_dict["Wins_cond"] = self.Wins_cond
        CondType13_dict["Nwppc_rad"] = self.Nwppc_rad
        CondType13_dict["Nwppc_tan"] = self.Nwppc_tan
        CondType13_dict["Wins_wire"] = self.Wins_wire
        CondType13_dict["Kwoh"] = self.Kwoh
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        CondType13_dict["__class__"] = "CondType13"
        return CondType13_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        Wwire_val = self.Wwire
        Wins_cond_val = self.Wins_cond
        Nwppc_rad_val = self.Nwppc_rad
        Nwppc_tan_val = self.Nwppc_tan
        Wins_wire_val = self.Wins_wire
        Kwoh_val = self.Kwoh
        if self.cond_mat is None:
            cond_mat_val = None
        else:
            cond_mat_val = self.cond_mat.copy()
        if self.ins_mat is None:
            ins_mat_val = None
        else:
            ins_mat_val = self.ins_mat.copy()
        # Creates new object of the same type with the copied properties
        obj_copy = type(self)(
            Wwire=Wwire_val,
            Wins_cond=Wins_cond_val,
            Nwppc_rad=Nwppc_rad_val,
            Nwppc_tan=Nwppc_tan_val,
            Wins_wire=Wins_wire_val,
            Kwoh=Kwoh_val,
            cond_mat=cond_mat_val,
            ins_mat=ins_mat_val,
        )
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        self.Wwire = None
        self.Wins_cond = None
        self.Nwppc_rad = None
        self.Nwppc_tan = None
        self.Wins_wire = None
        self.Kwoh = None
        # Set to None the properties inherited from Conductor
        super(CondType13, self)._set_None()

    def _get_Wwire(self):
        """getter of Wwire"""
        return self._Wwire

    def _set_Wwire(self, value):
        """setter of Wwire"""
        check_var("Wwire", value, "float", Vmin=0)
        self._Wwire = value

    Wwire = property(
        fget=_get_Wwire,
        fset=_set_Wwire,
        doc="""cf schematics, single wire diameter without insulation [m]

        :Type: float
        :min: 0
        """,
    )

    def _get_Wins_cond(self):
        """getter of Wins_cond"""
        return self._Wins_cond

    def _set_Wins_cond(self, value):
        """setter of Wins_cond"""
        check_var("Wins_cond", value, "float", Vmin=0)
        self._Wins_cond = value

    Wins_cond = property(
        fget=_get_Wins_cond,
        fset=_set_Wins_cond,
        doc="""(advanced) cf schematics, winding coil insulation diameter [m]

        :Type: float
        :min: 0
        """,
    )

    def _get_Nwppc_rad(self):
        """getter of Nwppc_rad"""
        return self._Nwppc_rad

    def _set_Nwppc_rad(self, value):
        """setter of Nwppc_rad"""
        check_var("Nwppc_rad", value, "int", Vmin=1)
        self._Nwppc_rad = value

    Nwppc_rad = property(
        fget=_get_Nwppc_rad,
        fset=_set_Nwppc_rad,
        doc="""cf schematics, stator winding number of preformed wires (strands) in parallel per coil along radial (vertical) direction

        :Type: int
        :min: 1
        """,
    )

    def _get_Nwppc_tan(self):
        """getter of Nwppc_tan"""
        return self._Nwppc_tan

    def _set_Nwppc_tan(self, value):
        """setter of Nwppc_tan"""
        check_var("Nwppc_tan", value, "int", Vmin=1)
        self._Nwppc_tan = value

    Nwppc_tan = property(
        fget=_get_Nwppc_tan,
        fset=_set_Nwppc_tan,
        doc="""cf schematics, stator winding number of preformed wires (strands) in parallel per coil along tangential (horizontal) direction

        :Type: int
        :min: 1
        """,
    )

    def _get_Wins_wire(self):
        """getter of Wins_wire"""
        return self._Wins_wire

    def _set_Wins_wire(self, value):
        """setter of Wins_wire"""
        check_var("Wins_wire", value, "float", Vmin=0)
        self._Wins_wire = value

    Wins_wire = property(
        fget=_get_Wins_wire,
        fset=_set_Wins_wire,
        doc="""(advanced) cf schematics, winding strand insulation thickness [m]

        :Type: float
        :min: 0
        """,
    )

    def _get_Kwoh(self):
        """getter of Kwoh"""
        return self._Kwoh

    def _set_Kwoh(self, value):
        """setter of Kwoh"""
        check_var("Kwoh", value, "float", Vmin=0)
        self._Kwoh = value

    Kwoh = property(
        fget=_get_Kwoh,
        fset=_set_Kwoh,
        doc="""winding overhang factor which describes the fact that random round wire end-windings can be more or less compressed (0.5 for small motors, 0.8 for large motors) - can be used to tune the average turn length (relevant if type_cond==1)

        :Type: float
        :min: 0
        """,
    )
