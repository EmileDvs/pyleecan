# -*- coding: utf-8 -*-
# File generated according to Generator/ClassesRef/Slot/HoleMag.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Slot/HoleMag
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
from pyleecan.Classes.Hole import Hole

# Import all class method
# Try/catch to remove unnecessary dependencies in unused method

import numpy as np
from pyleecan.Classes._check import InitUnKnowClassError


class HoleMag(Hole):
    """Hole with magnets for lamination (abstract)"""

    VERSION = 1

    # cf Methods.Slot.HoleMag.comp_mass_magnet_id
    def comp_mass_magnet_id(self, index):
        """Compute the mass of the hole magnet of the corresponding index

        Parameters
        ----------
        self : HoleMag
            A HoleMag object
        index : int
            Index of the magnet to compute the surface

        Returns
        -------
        Mmag: float
            Mass of the Magnet [m**2]
        """

        mag_list = self.get_magnet_list()
        if mag_list[index] is None:
            return 0
        else:
            if mag_list[index].Lmag is None:
                Lmag = self.parent.L1
            else:
                Lmag = mag_list[index].Lmag
            return self.comp_surface_magnet_id(index) * Lmag

    # cf Methods.Slot.HoleMag.comp_mass_magnets
    def comp_mass_magnets(self):
        """Compute the mass of the hole magnets (some of them may be missing)

        Parameters
        ----------
        self : HoleMag
            A HoleMag object

        Returns
        -------
        Mmag: float
            mass of the magnets [kg]
        """

        M = 0
        mag_list = self.get_magnet_list()
        for ii, mag in enumerate(mag_list):
            if mag is not None:
                Smag = self.comp_surface_magnet_id(ii)
                if mag.Lmag is None:
                    Lmag = self.parent.L1
                else:
                    Lmag = mag.Lmag
                # Check material definition
                if mag.mat_type.struct.rho is None:
                    raise Exception(
                        "Error: For magnet material "
                        + str(mag.mat_type.name)
                        + " struct.rho is not set"
                    )
                M += Smag * Lmag * mag.mat_type.struct.rho

        return M

    # cf Methods.Slot.HoleMag.comp_surface_magnets
    def comp_surface_magnets(self):
        """Compute the surface of all the magnet(s)

        Parameters
        ----------
        self : HoleMag
            A HoleMag object

        Returns
        -------
        Smag: float
            Surface of all the Magnet(s) [m**2]
        """

        mag_list = self.get_magnet_list()
        Smag = 0
        for ii in range(len(mag_list)):
            Smag += self.comp_surface_magnet_id(ii)
        return Smag

    # cf Methods.Slot.HoleMag.comp_volume_magnets
    def comp_volume_magnets(self):
        """Compute the volume of the hole magnets (some of them may be missing)

        Parameters
        ----------
        self : HoleMag
            A HoleMag object

        Returns
        -------
        Vmag: float
            volume of the magnets [m**3]
        """

        V = 0
        mag_list = self.get_magnet_list()
        for ii, mag in enumerate(mag_list):
            if mag is not None:
                Smag = self.comp_surface_magnet_id(ii)
                if mag.Lmag is None:
                    Lmag = self.parent.L1
                else:
                    Lmag = mag.Lmag
                V += Smag * Lmag

        return V

    # cf Methods.Slot.HoleMag.get_magnet_list
    def get_magnet_list(self):
        """Return the list of magnet (including None)

        Parameters
        ----------
        self : HoleMag
            A HoleMag object

        Returns
        -------
        magnet_list : list
            List of Magnet

        """

        magnet_list = list()
        if hasattr(self, "magnet_dict"):
            for value in self.magnet_dict.values():
                magnet_list.append(value)
        else:
            mag_id = 0
            while hasattr(self, "magnet_" + str(mag_id)):
                magnet_list.append(getattr(self, "magnet_" + str(mag_id)))
                mag_id += 1
        return magnet_list

    # cf Methods.Slot.HoleMag.has_magnet
    def has_magnet(self):
        """Return if the Hole has magnet

        Parameters
        ----------
        self : HoleMag
            A HoleMag object

        Returns
        -------
        has_magnet : bool
            True

        """

        return True

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
        Zh=36,
        mat_void=-1,
        magnetization_dict_offset=None,
        Alpha0=0,
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
            if "Zh" in list(init_dict.keys()):
                Zh = init_dict["Zh"]
            if "mat_void" in list(init_dict.keys()):
                mat_void = init_dict["mat_void"]
            if "magnetization_dict_offset" in list(init_dict.keys()):
                magnetization_dict_offset = init_dict["magnetization_dict_offset"]
            if "Alpha0" in list(init_dict.keys()):
                Alpha0 = init_dict["Alpha0"]
        # Set the properties (value check and convertion are done in setter)
        # Call Hole init
        super(HoleMag, self).__init__(
            Zh=Zh,
            mat_void=mat_void,
            magnetization_dict_offset=magnetization_dict_offset,
            Alpha0=Alpha0,
        )
        # The class is frozen (in Hole init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        HoleMag_str = ""
        # Get the properties inherited from Hole
        HoleMag_str += super(HoleMag, self).__str__()
        return HoleMag_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from Hole
        if not super(HoleMag, self).__eq__(other):
            return False
        return True

    def compare(self, other, name="self", ignore_list=None, is_add_value=False):
        """Compare two objects and return list of differences"""

        if ignore_list is None:
            ignore_list = list()
        if type(other) != type(self):
            return ["type(" + name + ")"]
        diff_list = list()

        # Check the properties inherited from Hole
        diff_list.extend(
            super(HoleMag, self).compare(
                other, name=name, ignore_list=ignore_list, is_add_value=is_add_value
            )
        )
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object

        # Get size of the properties inherited from Hole
        S += super(HoleMag, self).__sizeof__()
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

        # Get the properties inherited from Hole
        HoleMag_dict = super(HoleMag, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs
        )
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        HoleMag_dict["__class__"] = "HoleMag"
        return HoleMag_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        Zh_val = self.Zh
        if self.mat_void is None:
            mat_void_val = None
        else:
            mat_void_val = self.mat_void.copy()
        if self.magnetization_dict_offset is None:
            magnetization_dict_offset_val = None
        else:
            magnetization_dict_offset_val = self.magnetization_dict_offset.copy()
        Alpha0_val = self.Alpha0
        # Creates new object of the same type with the copied properties
        obj_copy = type(self)(
            Zh=Zh_val,
            mat_void=mat_void_val,
            magnetization_dict_offset=magnetization_dict_offset_val,
            Alpha0=Alpha0_val,
        )
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        # Set to None the properties inherited from Hole
        super(HoleMag, self)._set_None()
