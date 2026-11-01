# File generated according to Generator/ClassesRef/Loss/LossModelWinding.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Loss/LossModelWinding"""

from os import linesep
from sys import getsizeof

import numpy as np

from pyleecan.Classes.LossModel import LossModel
from pyleecan.Classes._check import check_var
from pyleecan.Functions.get_logger import get_logger
from pyleecan.Functions.load import load_init_dict
from pyleecan.Functions.save import save


class LossModelWinding(LossModel):
    """Winding loss model"""

    VERSION = 1

    # cf Methods.Loss.LossModelWinding.comp_coeff
    def comp_coeff(self, T_op=20, T_ref=20):
        """Compute the skin effect factor on resistance for the conductors from "Design of Rotating Electrical Machines", J. Pyrhonen, second edition
        All parameters are defined p.270 / 271
        In this method, the returned value is the one from the reference divided by the frequency, as the effect of
        frequency will be taken into account in the coeff_dict

        Parameters
        ----------
        self : LossModelWinding
            a LossModelWinding object
        T_op: float
            Conductor operational temperature [degC]
        T_ref: float
            Conductor reference temperature [degC]

        Returns
        ----------
        kr_skin : float
            skin effect coeff for resistance at given frequency and temperature
        """

        conductor = self.parent.parent.machine.stator.winding.conductor

        # Compute slot average width
        slot = conductor.parent.parent.slot
        b = slot.comp_width()

        # Get number of turns in series per coil
        zt = conductor.parent.Ntcoil

        # check if wires are round or rectangular
        is_round_wire = conductor.is_round_wire()

        # conductor height
        hc0 = conductor.comp_height_wire()
        # conductor width
        bc0 = conductor.comp_width_wire()
        # Number of circumferential adjacent wires
        za = conductor.comp_nb_circumferential_wire()
        # Number of radial adjacent wires
        zp = conductor.comp_nb_radial_wire()
        # Equivalent height of conductor
        hc = zp * hc0

        # Electrical conductivity accounting for temperature increase
        sigma = conductor.cond_mat.elec.get_conductivity(T_op=T_op, T_ref=T_ref)

        # Magnetic permeability
        mu0 = 4 * np.pi * 1e-7
        if conductor.cond_mat.mag is None or conductor.cond_mat.mag.mur_lin is None:
            mur = 1
        else:
            mur = conductor.cond_mat.mag.mur_lin

        # reduced conductor height Eq(5.24) p.270 divided by the frequency + adding relative permeatibility
        ksi = hc * np.sqrt(np.pi * mu0 * mur * sigma * za * bc0 / b)

        if not isinstance(ksi, float):
            # Avoid numerical error with 0
            ksi[ksi == 0] = 1e-4

        # average resistance factor
        if is_round_wire:
            # Use round wire approximation Eq(5.30) p.271
            # --> kr_skin = 1 + 0.59 * ((zt ** 2 - 0.2) / 9) * ksi ** 4
            k = 0.59 * ((zt**2 - 0.2) / 9) * ksi**4
        else:
            # Use rectangular wire approximation Eq(5.29) p.271
            # --> kr_skin = 1 + (zt ** 2 - 0.2) / 9 * ksi ** 4
            k = (zt**2 - 0.2) / 9 * ksi**4

        return k

    # cf Methods.Loss.LossModelWinding.comp_loss
    def comp_loss(self):
        """Calculate joule losses in stator windings

        Parameters
        ----------
        self: LossModelWinding
            a LossModelWinding object

        Returns
        -------
        Pjoule_density : ndarray
            Joule loss density function of frequency and elements [W/m3]
        freqs: ndarray
            frequency vector [Hz]
        """

        if self.parent.parent is None:
            raise ValueError(
                "Cannot calculate joule losses if simu is not in an Output"
            )
        else:
            output = self.parent.parent.parent

        if output.elec is None:
            raise ValueError("Cannot calculate joule losses if OutElec is None")

        if self.parent.is_get_meshsolution and output.mag is None:
            raise ValueError("Cannot calculate joule losses if OutMag is None")

        machine = output.simu.machine

        OP = output.elec.OP
        felec = OP.get_felec()

        lam = machine.stator
        T_op = self.parent.Tsta

        Rs = lam.comp_resistance_wind(T=T_op)
        qs = lam.winding.qs

        if self.type_skin_effect > 0:
            # Account for skin effect
            k = self.comp_coeff(
                T_op=T_op,
            )
        else:
            k = 0

        # Calculate overall joule losses
        Id_Iq = OP.get_Id_Iq()
        coeff = qs * Rs * (Id_Iq["Id"] ** 2 + Id_Iq["Iq"] ** 2)
        Pjoule = coeff * (1 + k * felec**2)

        per_a = output.geo.per_a
        if output.geo.is_antiper_a:
            per_a *= 2

        Lst = lam.L1

        # Get surface elements for windings
        ms = output.mag.meshsolution
        Se = ms.mesh.get_element_area()[ms.group[self.group]]

        # Constant component and twice the electrical frequency have same joule density values
        freqs = np.array([felec])
        Pjoule_density = np.zeros((freqs.size, Se.size))
        Pjoule_density[0, :] = Pjoule / (per_a * Lst * np.sum(Se))

        A = coeff * k
        B = coeff
        self.coeff_dict = {"2": A, "0": B}

        return Pjoule_density, freqs

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
        type_skin_effect=1,
        name="",
        group="",
        is_show_fig=False,
        coeff_dict=None,
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
            if "type_skin_effect" in list(init_dict.keys()):
                type_skin_effect = init_dict["type_skin_effect"]
            if "name" in list(init_dict.keys()):
                name = init_dict["name"]
            if "group" in list(init_dict.keys()):
                group = init_dict["group"]
            if "is_show_fig" in list(init_dict.keys()):
                is_show_fig = init_dict["is_show_fig"]
            if "coeff_dict" in list(init_dict.keys()):
                coeff_dict = init_dict["coeff_dict"]
        # Set the properties (value check and convertion are done in setter)
        self.type_skin_effect = type_skin_effect
        # Call LossModel init
        super(LossModelWinding, self).__init__(
            name=name, group=group, is_show_fig=is_show_fig, coeff_dict=coeff_dict
        )
        # The class is frozen (in LossModel init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        LossModelWinding_str = ""
        # Get the properties inherited from LossModel
        LossModelWinding_str += super(LossModelWinding, self).__str__()
        LossModelWinding_str += (
            "type_skin_effect = " + str(self.type_skin_effect) + linesep
        )
        return LossModelWinding_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from LossModel
        if not super(LossModelWinding, self).__eq__(other):
            return False
        if other.type_skin_effect != self.type_skin_effect:
            return False
        return True

    def compare(self, other, name="self", ignore_list=None, is_add_value=False):
        """Compare two objects and return list of differences"""

        if ignore_list is None:
            ignore_list = list()
        if type(other) != type(self):
            return ["type(" + name + ")"]
        diff_list = list()

        # Check the properties inherited from LossModel
        diff_list.extend(
            super(LossModelWinding, self).compare(
                other, name=name, ignore_list=ignore_list, is_add_value=is_add_value
            )
        )
        if other._type_skin_effect != self._type_skin_effect:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._type_skin_effect)
                    + ", other="
                    + str(other._type_skin_effect)
                    + ")"
                )
                diff_list.append(name + ".type_skin_effect" + val_str)
            else:
                diff_list.append(name + ".type_skin_effect")
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object

        # Get size of the properties inherited from LossModel
        S += super(LossModelWinding, self).__sizeof__()
        S += getsizeof(self.type_skin_effect)
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

        # Get the properties inherited from LossModel
        LossModelWinding_dict = super(LossModelWinding, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs
        )
        LossModelWinding_dict["type_skin_effect"] = self.type_skin_effect
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        LossModelWinding_dict["__class__"] = "LossModelWinding"
        return LossModelWinding_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        type_skin_effect_val = self.type_skin_effect
        name_val = self.name
        group_val = self.group
        is_show_fig_val = self.is_show_fig
        if self.coeff_dict is None:
            coeff_dict_val = None
        else:
            coeff_dict_val = self.coeff_dict.copy()
        # Creates new object of the same type with the copied properties
        obj_copy = type(self)(
            type_skin_effect=type_skin_effect_val,
            name=name_val,
            group=group_val,
            is_show_fig=is_show_fig_val,
            coeff_dict=coeff_dict_val,
        )
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        self.type_skin_effect = None
        # Set to None the properties inherited from LossModel
        super(LossModelWinding, self)._set_None()

    def _get_type_skin_effect(self):
        """getter of type_skin_effect"""
        return self._type_skin_effect

    def _set_type_skin_effect(self, value):
        """setter of type_skin_effect"""
        check_var("type_skin_effect", value, "int")
        self._type_skin_effect = value

    type_skin_effect = property(
        fget=_get_type_skin_effect,
        fset=_set_type_skin_effect,
        doc="""0 to ignore skin effect, 1 to consider it

        :Type: int
        """,
    )
