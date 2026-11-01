# File generated according to Generator/ClassesRef/Loss/LossModelWindagePyrhonen.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Loss/LossModelWindagePyrhonen"""

import numpy as np

from pyleecan.Classes.LossModel import LossModel
from pyleecan.Functions.get_logger import get_logger
from pyleecan.Functions.load import load_init_dict
from pyleecan.Functions.save import save


class LossModelWindagePyrhonen(LossModel):
    """Windage loss model"""

    VERSION = 1

    # cf Methods.Loss.LossModelWindagePyrhonen.comp_loss
    def comp_loss(self):
        """Calculate Windage losses
        Equation from "Design of Rotating Electrical Machines", Second Edition, Pyrhönen, Jokinen, Hrabovcovà p528

        Parameters
        ----------
        self: LossModelWindagePyrhonen
            a LossModelWindagePyrhonen object

        Returns
        -------
        Pjoule_density : ndarray
            loss density function of frequency and elements [W/m3]
        freqs: ndarray
            frequency vector [Hz]
        """

        if self.parent.parent is None:
            raise ValueError("Cannot calculate losses if simu is not in an Output")
        else:
            output = self.parent.parent.parent

        if output.elec is None:
            raise ValueError("Cannot calculate losses if OutElec is None")

        if self.parent.is_get_meshsolution and output.mag is None:
            raise ValueError("Cannot calculate losses if OutMag is None")

        machine = output.simu.machine

        OP = output.elec.OP
        felec = OP.get_felec()

        Dr = machine.rotor.Rext * 2
        L = machine.rotor.L1
        p = machine.get_pole_pair_number()
        rho = 1.225  # air density
        k = 1
        omega = 2 * np.pi / p * felec
        delta = machine.comp_length_airgap_active()
        mu = 18.5e-6  # Dynamic viscosity of air
        # Couette Reynolds number
        Re_delta = rho * omega * Dr * delta / (2 * mu)
        # ------------------------------------------ Warning ---------------------------------------------
        # As C_M depends on Re_delta, which depends on the frequency, the coefficient that will be stored
        # in the coeff_dict below depends on frequency. So the coefficient may change with frequency and should be
        # computed again. But to build the coeff_dict, the assumption that C_M will not change must be made.
        # ------------------------------------------------------------------------------------------------
        if Re_delta < 64:
            C_M = 10 * (2 * delta / Dr) ** 0.3 / Re_delta
        elif Re_delta < 5e2:
            C_M = 2 * (2 * delta / Dr) ** 0.3 / Re_delta**0.6
        elif Re_delta < 1e4:
            C_M = 1.03 * (2 * delta / Dr) ** 0.3 / Re_delta**0.5
        else:
            C_M = 0.065 * (2 * delta / Dr) ** 0.3 / Re_delta**0.2

        P1 = 1 / 32 * k * C_M * np.pi * rho * omega**3 * Dr**4 * L

        Dri = machine.rotor.Rint

        # tip Reynolds number
        Re_r = rho * omega * Dr**2 / (4 * mu)

        if Re_r < 3e5:
            C_M = 3.87 / Re_r**0.5
        else:
            C_M = 0.146 / Re_r**0.2

        P2 = 1 / 64 * C_M * rho * omega**3 * (Dr**5 - Dri**5)

        Ploss = P1 + P2

        power = 3

        coeff = Ploss / felec**power

        per_a = output.geo.per_a
        if output.geo.is_antiper_a:
            per_a *= 2

        # Get surface elements for windings
        ms = output.mag.meshsolution
        Se = ms.mesh.get_element_area()[ms.group["rotor core"]]

        # Constant component and twice the electrical frequency have same joule density values
        freqs = np.array([felec])
        P_density = np.zeros((freqs.size, Se.size))
        P_density[0, :] = Ploss / (per_a * L * np.sum(Se))

        self.coeff_dict = {str(power): coeff}

        return P_density, freqs

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
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
            if "name" in list(init_dict.keys()):
                name = init_dict["name"]
            if "group" in list(init_dict.keys()):
                group = init_dict["group"]
            if "is_show_fig" in list(init_dict.keys()):
                is_show_fig = init_dict["is_show_fig"]
            if "coeff_dict" in list(init_dict.keys()):
                coeff_dict = init_dict["coeff_dict"]
        # Set the properties (value check and convertion are done in setter)
        # Call LossModel init
        super(LossModelWindagePyrhonen, self).__init__(
            name=name, group=group, is_show_fig=is_show_fig, coeff_dict=coeff_dict
        )
        # The class is frozen (in LossModel init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        LossModelWindagePyrhonen_str = ""
        # Get the properties inherited from LossModel
        LossModelWindagePyrhonen_str += super(LossModelWindagePyrhonen, self).__str__()
        return LossModelWindagePyrhonen_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from LossModel
        if not super(LossModelWindagePyrhonen, self).__eq__(other):
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
            super(LossModelWindagePyrhonen, self).compare(
                other, name=name, ignore_list=ignore_list, is_add_value=is_add_value
            )
        )
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object

        # Get size of the properties inherited from LossModel
        S += super(LossModelWindagePyrhonen, self).__sizeof__()
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
        LossModelWindagePyrhonen_dict = super(LossModelWindagePyrhonen, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs
        )
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        LossModelWindagePyrhonen_dict["__class__"] = "LossModelWindagePyrhonen"
        return LossModelWindagePyrhonen_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        name_val = self.name
        group_val = self.group
        is_show_fig_val = self.is_show_fig
        if self.coeff_dict is None:
            coeff_dict_val = None
        else:
            coeff_dict_val = self.coeff_dict.copy()
        # Creates new object of the same type with the copied properties
        obj_copy = type(self)(
            name=name_val,
            group=group_val,
            is_show_fig=is_show_fig_val,
            coeff_dict=coeff_dict_val,
        )
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        # Set to None the properties inherited from LossModel
        super(LossModelWindagePyrhonen, self)._set_None()
