# -*- coding: utf-8 -*-
# File generated according to Generator/ClassesRef/Machine/LamSlotMag.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Machine/LamSlotMag
"""

from os import linesep
from sys import getsizeof
from logging import getLogger
from pyleecan.Classes._check import set_array, check_var, raise_
from pyleecan.Functions.get_logger import get_logger
from pyleecan.Functions.save import save
from pyleecan.Functions.load import load_init_dict
from pyleecan.Functions.Load.import_class import import_class
from copy import deepcopy
from pyleecan.Classes.LamSlotM import LamSlotM

# Import all class method
# Try/catch to remove unnecessary dependencies in unused method
import numpy as np
from pyleecan.Classes.LamSlot import LamSlot
from pyleecan.Functions.labels import (
    update_RTS_index,
    BOUNDARY_PROP_LAB,
    COND_BOUNDARY_PROP_LAB,
    MAG_LAB,
    YSMR_LAB,
    YSML_LAB,
    LAM_LAB,
    YOKE_LAB,
    decode_label,
)
from pyleecan.Methods.Machine.LamSlotMag import LMC_SlotTooLong


from pyleecan.Classes._check import InitUnKnowClassError


class LamSlotMag(LamSlotM):
    """Lamination with Slot for Magnets"""

    VERSION = 1

    # cf Methods.Machine.LamSlotMag.build_geometry
    def build_geometry(
        self, is_magnet=True, sym=1, alpha=0, delta=0, is_circular_radius=False
    ):
        """Build the geometry of the LamSlotMag

        Parameters
        ----------
        self : LamSlotMag
            LamSlotMag object
        is_magnet : bool
            If True build the magnet surfaces
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

        st = self.get_label()

        assert (self.slot.Zs % sym) == 0, (
            "ERROR, Wrong symmetry for "
            + st
            + " "
            + str(self.slot.Zs)
            + " slots and sym="
            + str(sym)
        )
        # getting the LamSlot surface
        surf_list = LamSlot.build_geometry(
            self,
            sym=sym,
            alpha=alpha,
            delta=delta,
            is_circular_radius=is_circular_radius,
        )

        Zs = self.slot.Zs
        slot_pitch = 2 * np.pi / Zs

        # Add the magnet surface(s)
        if is_magnet and self.magnet is not None:
            # Get the active surface to copy rotate
            Nrad, Ntan = self.get_dim_active()
            mag_layer_surf = self.slot.build_geometry_active(
                Nrad=Nrad,
                Ntan=Ntan,
                alpha=alpha,
                delta=delta,
            )

            # for each magnet to draw
            mag_surf_list = list()
            for ii in range(Zs // sym):
                for surf in mag_layer_surf:
                    mag_surf = surf.copy()
                    # changing the slot reference number
                    mag_surf.label = update_RTS_index(
                        label=surf.label, S_id=ii, surf_type_label=MAG_LAB
                    )
                    mag_surf.rotate(ii * slot_pitch)
                    mag_surf_list.append(mag_surf)
            # Update the magnets BC (if magnet side matches sym lines ex: SlotM18)
            if self.slot.is_full_pitch_active() and sym > 1:
                for surf in mag_surf_list:
                    label_dict = decode_label(surf.label)
                    # Set BC on Right side / Ox
                    if label_dict["S_id"] == 0:
                        # Find the lines to add the BC
                        for line in surf.get_lines():
                            if (
                                line.prop_dict is not None
                                and COND_BOUNDARY_PROP_LAB in line.prop_dict
                                and line.prop_dict[COND_BOUNDARY_PROP_LAB] == YSMR_LAB
                            ):
                                line.prop_dict.update(
                                    {
                                        BOUNDARY_PROP_LAB: st
                                        + "_"
                                        + YSMR_LAB
                                        + "-"
                                        + str(label_dict["R_id"])
                                    }
                                )
                    # Set BC on Left side / last active surface
                    if label_dict["S_id"] == Zs // sym - 1:
                        # Find the lines to add the BC
                        for line in surf.get_lines():
                            if (
                                line.prop_dict is not None
                                and COND_BOUNDARY_PROP_LAB in line.prop_dict
                                and line.prop_dict[COND_BOUNDARY_PROP_LAB] == YSML_LAB
                            ):
                                line.prop_dict.update(
                                    {
                                        BOUNDARY_PROP_LAB: st
                                        + "_"
                                        + YSML_LAB
                                        + "-"
                                        + str(label_dict["R_id"])
                                    }
                                )
            # Update Magnets BC when no lamination
            if self.Rint == self.Rext and self.Rint != 0:
                label_yoke = self.get_label() + "_" + LAM_LAB + YOKE_LAB
                for surf in mag_surf_list:
                    label_dict = decode_label(surf.label)
                    if label_dict["R_id"] == 0:
                        for line in surf.get_lines():
                            if (
                                line.prop_dict is not None
                                and COND_BOUNDARY_PROP_LAB in line.prop_dict
                                and line.prop_dict[COND_BOUNDARY_PROP_LAB] == YOKE_LAB
                            ):
                                line.prop_dict.update({BOUNDARY_PROP_LAB: label_yoke})

            # Shift to have a tooth center on Ox
            for surf in mag_surf_list:
                surf.rotate(np.pi / Zs)
            surf_list.extend(mag_surf_list)

        return surf_list

    # cf Methods.Machine.LamSlotMag.check
    def check(self):
        """Check that the Lamination object is correct

        Parameters
        ----------
        self : LamSlotMag
            A LamSlotMag object

        Returns
        -------
        None

        Raises
        _______
        LMC_SlotTooLong
            The Slot is too long for the lamination (HYoke <0)
        """
        super(type(self), self).check()

        self.slot.check()

        if self.comp_height_yoke() < 0:
            raise LMC_SlotTooLong(
                "The Slot is too long for the lamination " "(HYoke <0)"
            )

    # cf Methods.Machine.LamSlotMag.comp_masses
    def comp_masses(self):
        """Compute the Lamination masses (Mlam, Mmag)

        Parameters
        ----------
        self : LamSlotMag
            A LamSlotMag object

        Returns
        -------
        M_dict: dict
            Lamination mass dictionary (Mtot, Mlam, Mmag) [kg]

        """

        M_dict = LamSlot.comp_masses(self)
        p = self.get_pole_pair_number()

        Mmag = (
            2
            * p
            * (
                self.slot.comp_surface_active()
                * self.magnet.Nseg
                * self.magnet.Lmag
                * self.magnet.mat_type.struct.rho
            )
        )

        M_dict["Mmag"] = Mmag
        M_dict["Mtot"] += Mmag

        return M_dict

    # cf Methods.Machine.LamSlotMag.comp_surfaces
    def comp_surfaces(self):
        """Compute the Lamination surfaces (Slam, Svent, Sslot, Smag)

        Parameters
        ----------
        self : LamSlotMag
            A LamSlotMag object

        Returns
        -------
        S_dict: dict
            Lamination surface dictionary (Slam, Svent, Sslot, Smag) [m**2]

        """

        S_dict = LamSlot.comp_surfaces(self)
        Smag = self.slot.comp_surface_active()

        S_dict["Smag"] = Smag

        return S_dict

    # cf Methods.Machine.LamSlotMag.comp_volumes
    def comp_volumes(self):
        """Compute the Lamination volumes (Vlam, Vvent, Vslot, Vmag)

        Parameters
        ----------
        self : LamSlotMag
            A LamSlotMag object

        Returns
        -------
        V_dict: dict
            Lamination surface dictionary (Vlam, Vvent, Vslot, Vmag) [m**3]

        """

        V_dict = LamSlot.comp_volumes(self)
        Vmag = self.slot.comp_surface_active() * self.magnet.Lmag

        V_dict["Vmag"] = Vmag

        return V_dict

    # cf Methods.Machine.LamSlotMag.get_all_mag_obj
    def get_all_mag_obj(self):
        """Return all the magnet object for all the layers

        Parameters
        ----------
        self : LamSlotMag
            A LamSlotMag object

        Returns
        -------
        mag_list : [Magnet]
            List of magnet object to define
        """

        mag_list = list()
        if self.mur_lin_matrix is None and self.Brm20_matrix is None:
            return [self.magnet]
        elif self.mur_lin_matrix is not None:
            _, index_unique = np.unique(self.mur_lin_matrix, return_index=True)
            for ii, flat_index in enumerate(index_unique):
                mag_list.append(self.magnet.copy())
                mag_list[-1].mat_type.name = "Magnet_" + str(ii + 1)
                mag_list[-1].mat_type.mag.mur_lin = self.mur_lin_matrix.flat[flat_index]
                # Assume that if a magnet has a different mur_lin, it has a different Brm20
                # So unique is applied only on mur (no cross unique check)
                if self.Brm20_matrix is not None:
                    mag_list[-1].mat_type.mag.Brm20 = self.Brm20_matrix.flat[flat_index]
        else:  # Only change Brm20
            Brm20_val = np.unique(self.Brm20_matrix)
            for ii, Brm20 in enumerate(Brm20_val):
                mag_list.append(self.magnet.copy())
                mag_list[-1].mat_type.mag.Brm20 = Brm20
                mag_list[-1].mat_type.name = "Magnet_" + str(ii + 1)
                name_index += 1

        return mag_list

    # cf Methods.Machine.LamSlotMag.get_magnet_by_label
    def get_magnet_by_label(self, label=None, label_dict=None):
        """Return the magnet corresponding to the label

        Parameters
        ----------
        self : LamSlotMag
            A LamSlotMag object
        label : str
            A surface id (ex Rotor-0_Magnet_R0-T0-S0)
        label_dict : dict
            Split dict of the label (to avoid decoding twice)

        Returns
        -------
        mag : Magnet
            The corresponding magnet object
        """

        # Usual case, all magnets are the same
        if self.mur_lin_matrix is None and self.Brm20_matrix is None:
            return self.magnet

        # Decode the magnet label
        if label_dict is None and label is None:
            raise Exception("label_dict and label can't be both at None")
        if label_dict is None:
            label_dict = decode_label(label)

        # Find the correct magnet to return
        mag_list = self.get_all_mag_obj()
        if self.mur_lin_matrix is not None:
            mur = self.mur_lin_matrix[
                label_dict["R_id"], label_dict["T_id"], label_dict["S_id"]
            ]
            mur_list = [mag.mat_type.mag.mur_lin for mag in mag_list]
            return mag_list[mur_list.index(mur)]
        elif self.Brm20_matrix is not None:
            Brm20 = self.Brm20_matrix[
                label_dict["R_id"], label_dict["T_id"], label_dict["S_id"]
            ]
            Brm20_list = [mag.mat_type.mag.Brm20 for mag in mag_list]
            return mag_list[Brm20_list.index(Brm20)]

    # cf Methods.Machine.LamSlotMag.set_Lmag
    def set_Lmag(self, value):
        """Set the Length of the magnet

        Parameters
        ----------
        self : LamSlotMag
            A LamSlotMag object
        value : float
            Value to set [m]
        """

        self.magnet.Lmag = value

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
        magnet=-1,
        mur_lin_matrix=None,
        Brm20_matrix=None,
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
            if "magnet" in list(init_dict.keys()):
                magnet = init_dict["magnet"]
            if "mur_lin_matrix" in list(init_dict.keys()):
                mur_lin_matrix = init_dict["mur_lin_matrix"]
            if "Brm20_matrix" in list(init_dict.keys()):
                Brm20_matrix = init_dict["Brm20_matrix"]
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
        self.magnet = magnet
        # Call LamSlotM init
        super(LamSlotMag, self).__init__(
            mur_lin_matrix=mur_lin_matrix,
            Brm20_matrix=Brm20_matrix,
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
        # The class is frozen (in LamSlotM init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        LamSlotMag_str = ""
        # Get the properties inherited from LamSlotM
        LamSlotMag_str += super(LamSlotMag, self).__str__()
        if self.magnet is not None:
            tmp = self.magnet.__str__().replace(linesep, linesep + "\t").rstrip("\t")
            LamSlotMag_str += "magnet = " + tmp
        else:
            LamSlotMag_str += "magnet = None" + linesep + linesep
        return LamSlotMag_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from LamSlotM
        if not super(LamSlotMag, self).__eq__(other):
            return False
        if other.magnet != self.magnet:
            return False
        return True

    def compare(self, other, name="self", ignore_list=None, is_add_value=False):
        """Compare two objects and return list of differences"""

        if ignore_list is None:
            ignore_list = list()
        if type(other) != type(self):
            return ["type(" + name + ")"]
        diff_list = list()

        # Check the properties inherited from LamSlotM
        diff_list.extend(
            super(LamSlotMag, self).compare(
                other, name=name, ignore_list=ignore_list, is_add_value=is_add_value
            )
        )
        if (other.magnet is None and self.magnet is not None) or (
            other.magnet is not None and self.magnet is None
        ):
            diff_list.append(name + ".magnet None mismatch")
        elif self.magnet is not None:
            diff_list.extend(
                self.magnet.compare(
                    other.magnet,
                    name=name + ".magnet",
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

        # Get size of the properties inherited from LamSlotM
        S += super(LamSlotMag, self).__sizeof__()
        S += getsizeof(self.magnet)
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

        # Get the properties inherited from LamSlotM
        LamSlotMag_dict = super(LamSlotMag, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs
        )
        if self.magnet is None:
            LamSlotMag_dict["magnet"] = None
        else:
            LamSlotMag_dict["magnet"] = self.magnet.as_dict(
                type_handle_ndarray=type_handle_ndarray,
                keep_function=keep_function,
                **kwargs
            )
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        LamSlotMag_dict["__class__"] = "LamSlotMag"
        return LamSlotMag_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        if self.magnet is None:
            magnet_val = None
        else:
            magnet_val = self.magnet.copy()
        if self.mur_lin_matrix is None:
            mur_lin_matrix_val = None
        else:
            mur_lin_matrix_val = self.mur_lin_matrix.copy()
        if self.Brm20_matrix is None:
            Brm20_matrix_val = None
        else:
            Brm20_matrix_val = self.Brm20_matrix.copy()
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
            magnet=magnet_val,
            mur_lin_matrix=mur_lin_matrix_val,
            Brm20_matrix=Brm20_matrix_val,
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

        if self.magnet is not None:
            self.magnet._set_None()
        # Set to None the properties inherited from LamSlotM
        super(LamSlotMag, self)._set_None()

    def _get_magnet(self):
        """getter of magnet"""
        return self._magnet

    def _set_magnet(self, value):
        """setter of magnet"""
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
                "pyleecan.Classes", value.get("__class__"), "magnet"
            )
            value = class_obj(init_dict=value)
        elif type(value) is int and value == -1:  # Default constructor
            Magnet = import_class("pyleecan.Classes", "Magnet", "magnet")
            value = Magnet()
        check_var("magnet", value, "Magnet")
        self._magnet = value

        if self._magnet is not None:
            self._magnet.parent = self

    magnet = property(
        fget=_get_magnet,
        fset=_set_magnet,
        doc="""Magnet of the lamination

        :Type: Magnet
        """,
    )
