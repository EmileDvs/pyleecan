# -*- coding: utf-8 -*-
# File generated according to Generator/ClassesRef/Material/ModelBH.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Material/ModelBH
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
from numpy import array
import numpy as np
from scipy.optimize import curve_fit

from numpy import isnan
from pyleecan.Classes._check import InitUnKnowClassError


class ModelBH(FrozenClass):
    """Abstract class for BH curve model"""

    VERSION = 1

    # cf Methods.Material.ModelBH.fit_model
    def fit_model(self, BH):
        """
        Fit the BH model parameters based on input B(H) curve of the material, and perform extrapolation.

        Parameters
        ----------
        self : ModelBH
            a ModelBH object
        BH: numpy.ndarray
            B(H) input values
        Bmax: float
            Maximum B value required
        Hmax: float
            Maximum H value required

        Returns
        -------
        new_BH: numpy.ndarray
            B(H) values (two colums matrix: H and B(H))

        """
        Bmax = self.Bmax
        Hmax = self.Hmax

        H = BH[:, 0]
        B = BH[:, 1]

        # Find the optimum parameter for curve fitting
        popt, _ = curve_fit(self.BH_func, H, B, p0=array([self.param1, self.param2]))

        param1 = popt[0]
        param2 = popt[1]

        self.param1 = param1
        self.param2 = param2

        # Idea to use scipy to find Hmax corresponding to Bmax
        # def Langevin_root(H):
        #     B = Bs * (np.cosh(H / a) / np.sinh(H / a) - a / H)
        #     return B - self.Bmax_extrapolate

        # x1 = BH[-1, 0]*(2 - BH[-2, 0]/BH[-1, 0])
        # x0 = BH[-1, 0]
        # Hmax = root_scalar(Langevin_root, x0=x0, x1=x1)

        # Hmax is defined from Bmax if it exists
        if Bmax is not None:
            delta = H[-1] * 0.01
            Hmax = H[-1]
            iteration = 0
            new_B = B[-1]
            while new_B < Bmax and iteration < 1000:
                Hmax += delta
                iteration += 1
                new_B = self.BH_func(Hmax, param1, param2)

        # Either imposed from method call or calculated from Bmax
        if Hmax is not None:
            added_H = np.linspace(H[-1], Hmax, iteration)
            new_H = np.hstack((H, added_H))
            new_B = self.BH_func(new_H, param1, param2)

            new_BH = np.zeros((len(new_H), 2))
            new_BH[:, 0] = new_H
            new_BH[:, 1] = new_B

        # Last special case: the BH curve is recalculated from the initial H values (then it is not an extrapolation, but a smoothing of the data based on the analytical model)
        else:
            new_B = self.BH_func(H, Bs, a)

        return new_BH

    # cf Methods.Material.ModelBH.get_BH
    def get_BH(self):
        """
        Return the B(H) curve of the material (by default do nothing).

        Parameters
        ----------
        self : ModelBH
            a ModelBH object

        Returns
        -------
        BH: numpy.ndarray
            B(H) values (two colums matrix: H and B(H))

        """

        return None

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(self, Bmax=2.31, Hmax=None, delta=100, init_dict=None, init_str=None):
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
            if "Bmax" in list(init_dict.keys()):
                Bmax = init_dict["Bmax"]
            if "Hmax" in list(init_dict.keys()):
                Hmax = init_dict["Hmax"]
            if "delta" in list(init_dict.keys()):
                delta = init_dict["delta"]
        # Set the properties (value check and convertion are done in setter)
        self.parent = None
        self.Bmax = Bmax
        self.Hmax = Hmax
        self.delta = delta

        # The class is frozen, for now it's impossible to add new properties
        self._freeze()

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        ModelBH_str = ""
        if self.parent is None:
            ModelBH_str += "parent = None " + linesep
        else:
            ModelBH_str += "parent = " + str(type(self.parent)) + " object" + linesep
        ModelBH_str += "Bmax = " + str(self.Bmax) + linesep
        ModelBH_str += "Hmax = " + str(self.Hmax) + linesep
        ModelBH_str += "delta = " + str(self.delta) + linesep
        return ModelBH_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False
        if other.Bmax != self.Bmax:
            return False
        if other.Hmax != self.Hmax:
            return False
        if other.delta != self.delta:
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
            other._Bmax is not None
            and self._Bmax is not None
            and isnan(other._Bmax)
            and isnan(self._Bmax)
        ):
            pass
        elif other._Bmax != self._Bmax:
            if is_add_value:
                val_str = (
                    " (self=" + str(self._Bmax) + ", other=" + str(other._Bmax) + ")"
                )
                diff_list.append(name + ".Bmax" + val_str)
            else:
                diff_list.append(name + ".Bmax")
        if (
            other._Hmax is not None
            and self._Hmax is not None
            and isnan(other._Hmax)
            and isnan(self._Hmax)
        ):
            pass
        elif other._Hmax != self._Hmax:
            if is_add_value:
                val_str = (
                    " (self=" + str(self._Hmax) + ", other=" + str(other._Hmax) + ")"
                )
                diff_list.append(name + ".Hmax" + val_str)
            else:
                diff_list.append(name + ".Hmax")
        if (
            other._delta is not None
            and self._delta is not None
            and isnan(other._delta)
            and isnan(self._delta)
        ):
            pass
        elif other._delta != self._delta:
            if is_add_value:
                val_str = (
                    " (self=" + str(self._delta) + ", other=" + str(other._delta) + ")"
                )
                diff_list.append(name + ".delta" + val_str)
            else:
                diff_list.append(name + ".delta")
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object
        S += getsizeof(self.Bmax)
        S += getsizeof(self.Hmax)
        S += getsizeof(self.delta)
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

        ModelBH_dict = dict()
        ModelBH_dict["Bmax"] = self.Bmax
        ModelBH_dict["Hmax"] = self.Hmax
        ModelBH_dict["delta"] = self.delta
        # The class name is added to the dict for deserialisation purpose
        ModelBH_dict["__class__"] = "ModelBH"
        return ModelBH_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        Bmax_val = self.Bmax
        Hmax_val = self.Hmax
        delta_val = self.delta
        # Creates new object of the same type with the copied properties
        obj_copy = type(self)(Bmax=Bmax_val, Hmax=Hmax_val, delta=delta_val)
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        self.Bmax = None
        self.Hmax = None
        self.delta = None

    def _get_Bmax(self):
        """getter of Bmax"""
        return self._Bmax

    def _set_Bmax(self, value):
        """setter of Bmax"""
        check_var("Bmax", value, "float")
        self._Bmax = value

    Bmax = property(
        fget=_get_Bmax,
        fset=_set_Bmax,
        doc="""Max value of B for extrapolation

        :Type: float
        """,
    )

    def _get_Hmax(self):
        """getter of Hmax"""
        return self._Hmax

    def _set_Hmax(self, value):
        """setter of Hmax"""
        check_var("Hmax", value, "float")
        self._Hmax = value

    Hmax = property(
        fget=_get_Hmax,
        fset=_set_Hmax,
        doc="""Max value of H for extrapolation

        :Type: float
        """,
    )

    def _get_delta(self):
        """getter of delta"""
        return self._delta

    def _set_delta(self, value):
        """setter of delta"""
        check_var("delta", value, "float")
        self._delta = value

    delta = property(
        fget=_get_delta,
        fset=_set_delta,
        doc="""Step value for H

        :Type: float
        """,
    )
