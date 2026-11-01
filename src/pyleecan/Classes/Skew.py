# -*- coding: utf-8 -*-
# File generated according to Generator/ClassesRef/Machine/Skew.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Machine/Skew
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
from pyleecan.Classes._frozen import FrozenClass

# Import all class method
# Try/catch to remove unnecessary dependencies in unused method
import numpy as np
from pyleecan.Methods.Machine.Skew import TYPE_SKEW_LIST
from pyleecan.Functions.load import import_class
from pyleecan.Functions.Plot import dict_2D
from pyleecan.Functions.SciDataTool.Plot.plot_2D import plot_2D

from ntpath import basename
from os.path import isfile
from pyleecan.Classes._check import CheckTypeError

import random

from pyleecan.Classes._check import InitUnKnowClassError


class Skew(FrozenClass):
    """Class for the skew (rotor or stator)"""

    VERSION = 1

    # cf Methods.Machine.Skew.comp_angle
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

    # cf Methods.Machine.Skew.comp_pattern
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
            z_list_new = list()
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

    # cf Methods.Machine.Skew.plot
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

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
        type_skew=None,
        rate=1,
        is_step=True,
        function=None,
        angle_list=None,
        z_list=None,
        Nstep=None,
        angle_overall=None,
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
            if "type_skew" in list(init_dict.keys()):
                type_skew = init_dict["type_skew"]
            if "rate" in list(init_dict.keys()):
                rate = init_dict["rate"]
            if "is_step" in list(init_dict.keys()):
                is_step = init_dict["is_step"]
            if "function" in list(init_dict.keys()):
                function = init_dict["function"]
            if "angle_list" in list(init_dict.keys()):
                angle_list = init_dict["angle_list"]
            if "z_list" in list(init_dict.keys()):
                z_list = init_dict["z_list"]
            if "Nstep" in list(init_dict.keys()):
                Nstep = init_dict["Nstep"]
            if "angle_overall" in list(init_dict.keys()):
                angle_overall = init_dict["angle_overall"]
        # Set the properties (value check and convertion are done in setter)
        self.parent = None
        self.type_skew = type_skew
        self.rate = rate
        self.is_step = is_step
        self.function = function
        self.angle_list = angle_list
        self.z_list = z_list
        self.Nstep = Nstep
        self.angle_overall = angle_overall

        # The class is frozen, for now it's impossible to add new properties
        self._freeze()

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        Skew_str = ""
        if self.parent is None:
            Skew_str += "parent = None " + linesep
        else:
            Skew_str += "parent = " + str(type(self.parent)) + " object" + linesep
        Skew_str += 'type_skew = "' + str(self.type_skew) + '"' + linesep
        Skew_str += "rate = " + str(self.rate) + linesep
        Skew_str += "is_step = " + str(self.is_step) + linesep
        if self._function_str is not None:
            Skew_str += "function = " + self._function_str + linesep
        elif self._function_func is not None:
            Skew_str += "function = " + str(self._function_func) + linesep
        else:
            Skew_str += "function = None" + linesep + linesep
        Skew_str += (
            "angle_list = "
            + linesep
            + str(self.angle_list).replace(linesep, linesep + "\t")
            + linesep
        )
        Skew_str += (
            "z_list = "
            + linesep
            + str(self.z_list).replace(linesep, linesep + "\t")
            + linesep
        )
        Skew_str += "Nstep = " + str(self.Nstep) + linesep
        Skew_str += "angle_overall = " + str(self.angle_overall) + linesep
        return Skew_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False
        if other.type_skew != self.type_skew:
            return False
        if other.rate != self.rate:
            return False
        if other.is_step != self.is_step:
            return False
        if other._function_str != self._function_str:
            return False
        if other.angle_list != self.angle_list:
            return False
        if other.z_list != self.z_list:
            return False
        if other.Nstep != self.Nstep:
            return False
        if other.angle_overall != self.angle_overall:
            return False
        return True

    def compare(self, other, name="self", ignore_list=None, is_add_value=False):
        """Compare two objects and return list of differences"""

        if ignore_list is None:
            ignore_list = list()
        if type(other) != type(self):
            return ["type(" + name + ")"]
        diff_list = list()
        if other._type_skew != self._type_skew:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._type_skew)
                    + ", other="
                    + str(other._type_skew)
                    + ")"
                )
                diff_list.append(name + ".type_skew" + val_str)
            else:
                diff_list.append(name + ".type_skew")
        if (
            other._rate is not None
            and self._rate is not None
            and np.isnan(other._rate)
            and np.isnan(self._rate)
        ):
            pass
        elif other._rate != self._rate:
            if is_add_value:
                val_str = (
                    " (self=" + str(self._rate) + ", other=" + str(other._rate) + ")"
                )
                diff_list.append(name + ".rate" + val_str)
            else:
                diff_list.append(name + ".rate")
        if other._is_step != self._is_step:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._is_step)
                    + ", other="
                    + str(other._is_step)
                    + ")"
                )
                diff_list.append(name + ".is_step" + val_str)
            else:
                diff_list.append(name + ".is_step")
        if other._function_str != self._function_str:
            diff_list.append(name + ".function")
        if other._angle_list != self._angle_list:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._angle_list)
                    + ", other="
                    + str(other._angle_list)
                    + ")"
                )
                diff_list.append(name + ".angle_list" + val_str)
            else:
                diff_list.append(name + ".angle_list")
        if other._z_list != self._z_list:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._z_list)
                    + ", other="
                    + str(other._z_list)
                    + ")"
                )
                diff_list.append(name + ".z_list" + val_str)
            else:
                diff_list.append(name + ".z_list")
        if other._Nstep != self._Nstep:
            if is_add_value:
                val_str = (
                    " (self=" + str(self._Nstep) + ", other=" + str(other._Nstep) + ")"
                )
                diff_list.append(name + ".Nstep" + val_str)
            else:
                diff_list.append(name + ".Nstep")
        if (
            other._angle_overall is not None
            and self._angle_overall is not None
            and np.isnan(other._angle_overall)
            and np.isnan(self._angle_overall)
        ):
            pass
        elif other._angle_overall != self._angle_overall:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._angle_overall)
                    + ", other="
                    + str(other._angle_overall)
                    + ")"
                )
                diff_list.append(name + ".angle_overall" + val_str)
            else:
                diff_list.append(name + ".angle_overall")
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object
        S += getsizeof(self.type_skew)
        S += getsizeof(self.rate)
        S += getsizeof(self.is_step)
        S += getsizeof(self._function_str)
        if self.angle_list is not None:
            for value in self.angle_list:
                S += getsizeof(value)
        if self.z_list is not None:
            for value in self.z_list:
                S += getsizeof(value)
        S += getsizeof(self.Nstep)
        S += getsizeof(self.angle_overall)
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

        Skew_dict = dict()
        Skew_dict["type_skew"] = self.type_skew
        Skew_dict["rate"] = self.rate
        Skew_dict["is_step"] = self.is_step
        if self._function_str is not None:
            Skew_dict["function"] = self._function_str
        elif keep_function:
            Skew_dict["function"] = self.function
        else:
            Skew_dict["function"] = None
            if self.function is not None:
                self.get_logger().warning(
                    "Skew.as_dict(): "
                    + f"Function {self.function.__name__} is not serializable "
                    + "and will be converted to None."
                )
        Skew_dict["angle_list"] = (
            self.angle_list.copy() if self.angle_list is not None else None
        )
        Skew_dict["z_list"] = self.z_list.copy() if self.z_list is not None else None
        Skew_dict["Nstep"] = self.Nstep
        Skew_dict["angle_overall"] = self.angle_overall
        # The class name is added to the dict for deserialisation purpose
        Skew_dict["__class__"] = "Skew"
        return Skew_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        type_skew_val = self.type_skew
        rate_val = self.rate
        is_step_val = self.is_step
        if self._function_str is not None:
            function_val = self._function_str
        else:
            function_val = self._function_func
        if self.angle_list is None:
            angle_list_val = None
        else:
            angle_list_val = self.angle_list.copy()
        if self.z_list is None:
            z_list_val = None
        else:
            z_list_val = self.z_list.copy()
        Nstep_val = self.Nstep
        angle_overall_val = self.angle_overall
        # Creates new object of the same type with the copied properties
        obj_copy = type(self)(
            type_skew=type_skew_val,
            rate=rate_val,
            is_step=is_step_val,
            function=function_val,
            angle_list=angle_list_val,
            z_list=z_list_val,
            Nstep=Nstep_val,
            angle_overall=angle_overall_val,
        )
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        self.type_skew = None
        self.rate = None
        self.is_step = None
        self.function = None
        self.angle_list = None
        self.z_list = None
        self.Nstep = None
        self.angle_overall = None

    def _get_type_skew(self):
        """getter of type_skew"""
        return self._type_skew

    def _set_type_skew(self, value):
        """setter of type_skew"""
        check_var("type_skew", value, "str")
        self._type_skew = value

    type_skew = property(
        fget=_get_type_skew,
        fset=_set_type_skew,
        doc="""Type of skew ("linear", "vshape", "function", "user-defined")

        :Type: str
        """,
    )

    def _get_rate(self):
        """getter of rate"""
        return self._rate

    def _set_rate(self, value):
        """setter of rate"""
        check_var("rate", value, "float")
        self._rate = value

    rate = property(
        fget=_get_rate,
        fset=_set_rate,
        doc="""Skew rate expressed in terms of slot pitch (stator slot pitch for SCIM, rotor slot pitch for PMSM)

        :Type: float
        """,
    )

    def _get_is_step(self):
        """getter of is_step"""
        return self._is_step

    def _set_is_step(self, value):
        """setter of is_step"""
        check_var("is_step", value, "bool")
        self._is_step = value

    is_step = property(
        fget=_get_is_step,
        fset=_set_is_step,
        doc="""True to define skew as steps

        :Type: bool
        """,
    )

    def _get_function(self):
        """getter of function"""
        return self._function_func

    def _set_function(self, value):
        """setter of function"""
        if value is None:
            self._function_str = None
            self._function_func = None
        elif isinstance(value, str) and "lambda" in value:
            self._function_str = value
            self._function_func = eval(value)
        elif isinstance(value, str) and isfile(value) and value[-3:] == ".py":
            self._function_str = value
            f = open(value, "r")
            exec(f.read(), globals())
            self._function_func = eval(basename(value[:-3]))
        elif callable(value):
            self._function_str = None
            self._function_func = value
        else:
            raise CheckTypeError(
                "For property function Expected function or str (path to python file or lambda), got: "
                + str(type(value))
            )

    function = property(
        fget=_get_function,
        fset=_set_function,
        doc="""Function which describes skew pattern

        :Type: function
        """,
    )

    def _get_angle_list(self):
        """getter of angle_list"""
        return self._angle_list

    def _set_angle_list(self, value):
        """setter of angle_list"""
        if type(value) is int and value == -1:
            value = list()
        check_var("angle_list", value, "list")
        self._angle_list = value

    angle_list = property(
        fget=_get_angle_list,
        fset=_set_angle_list,
        doc="""List of skew angles

        :Type: list
        """,
    )

    def _get_z_list(self):
        """getter of z_list"""
        return self._z_list

    def _set_z_list(self, value):
        """setter of z_list"""
        if type(value) is int and value == -1:
            value = list()
        check_var("z_list", value, "list")
        self._z_list = value

    z_list = property(
        fget=_get_z_list,
        fset=_set_z_list,
        doc="""List of z axis positions for which skew angles are given

        :Type: list
        """,
    )

    def _get_Nstep(self):
        """getter of Nstep"""
        return self._Nstep

    def _set_Nstep(self, value):
        """setter of Nstep"""
        check_var("Nstep", value, "int", Vmin=2)
        self._Nstep = value

    Nstep = property(
        fget=_get_Nstep,
        fset=_set_Nstep,
        doc="""Number of steps if step skew

        :Type: int
        :min: 2
        """,
    )

    def _get_angle_overall(self):
        """getter of angle_overall"""
        return self._angle_overall

    def _set_angle_overall(self, value):
        """setter of angle_overall"""
        check_var("angle_overall", value, "float", Vmin=0)
        self._angle_overall = value

    angle_overall = property(
        fget=_get_angle_overall,
        fset=_set_angle_overall,
        doc="""Overall skewing angle

        :Type: float
        :min: 0
        """,
    )
