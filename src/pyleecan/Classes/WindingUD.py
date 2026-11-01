# -*- coding: utf-8 -*-
# File generated according to Generator/ClassesRef/Machine/WindingUD.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Machine/WindingUD
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
from pyleecan.Classes.Winding import Winding

# Import all class method
# Try/catch to remove unnecessary dependencies in unused method
from pyleecan.Methods.Machine.WindingUD.import_from_csv import (
    COIL_COL,
    RAD_COL,
    TAN_COL,
    ZS_COL,
)
from os.path import isfile
from csv import reader
from numpy import zeros, amax, tile, array, power, mod, arange, sign
from pyleecan.Methods.Machine.WindingUD.init_as_CW1L import WindingT2DefNtError
from pyleecan.Methods.Machine.Winding import WindingError
from pyleecan.Functions.Winding.reverse_wind_mat import reverse_wind_mat
from pyleecan.Functions.Winding.shift_wind_mat import shift_wind_mat
from pyleecan.Methods.Machine.WindingUD.init_as_CW2LR import WindingT5DefMsError
from pyleecan.Methods.Machine.WindingUD.init_as_CW2LT import WindingT1DefMsError
from pyleecan.Methods.Machine.WindingUD.init_as_DWL import WindingDefMsError

from numpy import array, array_equal
from numpy import isnan
from pyleecan.Classes._check import InitUnKnowClassError


class WindingUD(Winding):
    """User defined winding"""

    VERSION = 1
    NAME = "User defined"

    # cf Methods.Machine.WindingUD.import_from_csv
    def import_from_csv(self, file_path=None):
        """Import the winding matrix from a csv file.
        One matrix for each phase
        Column Slot id, Ntcoil, Rad id, Tan id

        Parameters
        ----------
        self : WindingUD
            A: WindingUD object
        file_path : str
            Path to the file to load
        """

        # parse file_path
        if file_path[-4:] != ".csv":
            file_path += ".csv"
        if not isfile(file_path):
            raise FileNotFoundError(file_path + " is not a csv winding file")

        with open(file_path, "r") as csv_file:
            line_list = list(reader(csv_file))
            # Get matrix size
            if "(" in line_list[0][0] and ")" in line_list[0][0]:
                is_header, offset = True, 1
                wind_shape = eval(line_list[0][0])
            else:  # No Header
                is_header, offset = False, 0
                Nrad, Ntan, Zs, qs = -1, -1, -1, 0
                for line in line_list:
                    if len(line) == 0:
                        qs += 1
                    else:
                        Nrad = max(Nrad, int(line[RAD_COL]))
                        Ntan = max(Ntan, int(line[TAN_COL]))
                        Zs = max(Zs, int(line[ZS_COL]))
                wind_shape = (Nrad + 1, Ntan + 1, Zs + 1, qs)

            if self.parent is not None and self.parent.slot is not None:
                assert self.parent.slot.Zs % wind_shape[2] == 0, (
                    "Mismatch between Lamination Zs ("
                    + str(self.parent.slot.Zs)
                    + ") and imported winding Zs ("
                    + str(wind_shape[2])
                    + ")"
                )
            wind_mat = zeros(wind_shape)

            # Load matrix
            qs_id = 0
            if is_header:  # Remove first line
                line_list.pop(0)
            for line in line_list:
                if len(line) == 0 or line[ZS_COL + offset] == "":
                    qs_id += 1
                else:
                    Rad_id = int(float(line[RAD_COL + offset]))
                    Tan_id = int(float(line[TAN_COL + offset]))
                    Zs_id = int(float(line[ZS_COL + offset]))
                    wind_mat[Rad_id, Tan_id, Zs_id, qs_id] = line[COIL_COL + offset]

        # complete partial winding matrix
        if self.parent is not None and self.parent.slot is not None:
            Zs = self.parent.slot.Zs
            if wind_mat.shape[2] < Zs:
                wind_mat = tile(wind_mat, (1, 1, Zs // wind_mat.shape[2], 1))

        # Update property
        self.clean()  # Remove periodicity
        self.wind_mat = wind_mat
        self.Nlayer = wind_shape[0] * wind_shape[1]
        self.qs = wind_shape[3]
        self.Ntcoil = amax(self.wind_mat)

    # cf Methods.Machine.WindingUD.init_as_CW1L
    def init_as_CW1L(self, Zs=None):
        """Compute the Winding Matrix (for winding type 2)
        type 2 : TOOTH WINDING, SINGLE LAYER ALTERNATE TEETH WOUND
        (Nlay_rad=1,Nlay_tan=1)

        Parameters
        ----------
        self : WindingUD
            A: WindingUD object
        Zs : int
            Number of Slot (Integer >0)

        Raises
        ------
        WindingT2DefNtError
            Zs/qs/2 must be an integer

        """
        if Zs is None:
            if self.parent is None:
                raise WindingError(
                    "ERROR: The Winding object must be in a Lamination object."
                )

            if self.parent.slot is None:
                raise WindingError(
                    "ERROR: The Winding object must be in a Lamination object with Slot."
                )

            Zs = self.parent.slot.Zs

        assert Zs > 0, "Zs must be >0"
        assert Zs % 1 == 0, "Zs must be an integer"

        # non overlapping ALTERNATE TEETH WOUND-> single layer
        # cf "2D exact analytical model for surface-mounted permanent-magnet motors
        # with semi-closed slots" -> U motor 10p/18s creates 2p, Zs/2+2p, Zs/2-2p

        qs = self.qs  # Phase Number
        Nt = Zs / float(qs) / 2.0  # Number of teeth by semi phase

        # Ncspc= Zs/(2.0*qs*self.Npcp/nlay)  # number of coils in series per parallel circuit
        # Ntspc = self.Ntcoil * Ncspc #Number of turns in series per phase
        Ntcoil = self.Ntcoil  # number of turns per coils

        if round(Nt) != Nt:  # Nt must be an integer
            raise WindingT2DefNtError(
                "wrong winding definition, cannot wind all "
                "the teeth (Zs/qs/2 is not an integer)!"
            )

        # first strategy - checked with Umbra_08 motor and Umbra_05: the winding
        # direction of each tooth is reversed
        wind_mat = zeros((1, 1, Zs, qs))

        for k in range(0, int(Nt)):  # winding alternatively the teeth
            for q in range(0, qs):
                xenc = q * 4 + k * 2 * qs + array([1, 2])
                wind_mat[0][0][int((xenc[0] - 1) % Zs)][q] = power(-1, xenc[0] + k + 1)
                wind_mat[0][0][int((xenc[1] - 1) % Zs)][q] = power(-1, xenc[1] + k + 1)

        wind_mat *= Ntcoil

        # Set default values
        if self.is_reverse_wind is None:
            self.is_reverse_wind = False
        if self.Nslot_shift_wind is None:
            self.Nslot_shift_wind = 0
        self.Nlayer = 1
        # Apply the transformations
        if self.is_reverse_wind:
            wind_mat = reverse_wind_mat(wind_mat)
        if self.Nslot_shift_wind > 0:
            wind_mat = shift_wind_mat(wind_mat, self.Nslot_shift_wind)

        self.wind_mat = wind_mat
        # Matrix changed, compute again periodicity
        self.per_a = None
        self.is_aper_a = None

    # cf Methods.Machine.WindingUD.init_as_CW2LR
    def init_as_CW2LR(self, Zs=None):
        """Compute the Winding Matrix (for winding type 5) (Nlay_rad=1,Nlay_tan=1)
        type 5 : TOOTH WINDING, DOUBLE LAYER ALL TEETH WOUND, RADIAL SUPERPOSITION

        Parameters
        ----------
        self : WindingUD
            A: WindingUD object
        Zs : int
            Number of Slot (Integer >0)

        Raises
        ------
        WindingT5DefMsError
            You must have 0.25< Zs/2/p/qs <= 0.5

        """
        if Zs is None:
            if self.parent is None:
                raise WindingError(
                    "ERROR: The Winding object must be in a Lamination object."
                )

            if self.parent.slot is None:
                raise WindingError(
                    "ERROR: The Winding object must be in a Lamination object with Slot."
                )

            Zs = self.parent.slot.Zs

        assert Zs > 0, "Zs must be >0"
        assert Zs % 1 == 0, "Zs must be an integer"

        # ex "Effect of Pole and Slot Combination on Noise and Vibration in Permanent
        # Magnet Synchronous Motor" creates highest harmonic at Zs/2+1 and Zs/2-1
        nlay = 2.0
        qs = float(self.qs)
        p = float(self.p)
        Ncgr = Zs / nlay / qs
        ms = Zs / 2.0 / p / qs
        # Ncspc= Zs/(2.0*qs*self.Npcp/nlay)  # number of coils in series per parallel circuit
        # Ntspc = self.Ntcoil * Ncspc #Number of turns in series per phase
        Ntcoil = self.Ntcoil  # Number of turns per coils

        wind_mat = zeros((2, 1, Zs, self.qs))
        # creates highest harmonic at Zs/2+1 and Zs/2-1
        if ms == 0.5:  # then Zs/qs is integer
            # traditional non overlapping all teeth wound winding
            for q in range(0, self.qs):
                for k in range(0, Zs // self.qs):  # number of Ncgr coils
                    xenc = q + array([1, 0]) + k * qs
                    wind_mat[0, 0, int(mod(xenc[0] - 1, Zs)), q] = (
                        +Ntcoil
                    )  # right/top/2
                    wind_mat[1, 0, int(mod(xenc[1] - 1, Zs)), q] = (
                        -Ntcoil
                    )  # left/bottom/1
        elif (
            ms != 0.5 and Ncgr % 1 == 0
        ):  # ms!=0.5 and Ncgr is an integer (ms>0.25 && ms<0.5)
            # new algorithm to reverse the coils
            for q in range(0, self.qs):
                for k in range(0, int((Zs // self.qs) // Ncgr)):  # number of Ncgr coils
                    for l in range(0, int(Ncgr)):
                        id0 = int(mod(q * Ncgr + 0 + k * qs * Ncgr - 1 + l, Zs))
                        id1 = int(mod(q * Ncgr + 1 + k * qs * Ncgr - 1 + l, Zs))
                        # left / bottom / 1
                        wind_mat[1, 0, id0, q] = -((-1) ** (l + q - 1 + k)) * Ntcoil
                        # right / top / 2
                        wind_mat[0, 0, id1, q] = +((-1) ** (l + q - 1 + k)) * Ntcoil

            wind_mat = wind_mat[:, :, ::-1, :]
        else:
            raise WindingT5DefMsError(
                "Winding geometry not handled yet, enter "
                "your own winding matrix with "
                "type_winding=0 and contact EOMYS"
            )

        # Set default values
        if self.is_reverse_wind is None:
            self.is_reverse_wind = False
        if self.Nslot_shift_wind is None:
            self.Nslot_shift_wind = 0
        self.Nlayer = 2
        # Apply the transformations
        if self.is_reverse_wind:
            wind_mat = reverse_wind_mat(wind_mat)
        if self.Nslot_shift_wind > 0:
            wind_mat = shift_wind_mat(wind_mat, self.Nslot_shift_wind)

        self.wind_mat = wind_mat
        # Matrix changed, compute again periodicity
        self.per_a = None
        self.is_aper_a = None

    # cf Methods.Machine.WindingUD.init_as_CW2LT
    def init_as_CW2LT(self, Zs=None):
        """Compute the Winding Matrix (for winding type 1)
        type 1 : TOOTH WINDING, DOUBLE LAYER ALL TEETH WOUND, ORTHORADIAL
        SUPERPOSITION  (Nlay_rad=1,Nlay_tan=2)

        Parameters
        ----------
        self : WindingUD
            A: WindingUD object
        Zs : int
            Number of Slot (Integer >0)

        Raises
        ------
        WindingT1DefMsError
            You must have 0.25< Zs/2/p/qs <= 0.5

        """
        if Zs is None:
            if self.parent is None:
                raise WindingError(
                    "ERROR: The Winding object must be in a Lamination object."
                )

            if self.parent.slot is None:
                raise WindingError(
                    "ERROR: The Winding object must be in a Lamination object with Slot."
                )

            Zs = self.parent.slot.Zs

        assert Zs > 0, "Zs must be >0"
        assert Zs % 1 == 0, "Zs must be an integer"

        # ex "Effect of Pole and Slot Combination on Noise and Vibration in Permanent
        # Magnet Synchronous Motor" creates highest harmonic at Zs/2+1 and Zs/2-1
        nlay = 2.0
        qs = float(self.qs)
        p = float(self.p)
        Ncgr = Zs / nlay / qs
        ms = Zs / 2.0 / p / qs
        # Ncspc= Zs/(2.0*qs*self.Npcp/nlay)  # number of coils in series per parallel circuit
        # Ntspc = self.Ntcoil * Ncspc #Number of turns in series per phase
        Ntcoil = self.Ntcoil  # number of turns per coils

        wind_mat = zeros((1, 2, Zs, int(qs)))
        # creates highest harmonic at Zs/2+1 and Zs/2-1
        if ms == 0.5:  # then Zs/qs is integer
            # traditional non overlapping all teeth wound winding
            for q in range(0, int(qs)):
                for k in range(0, int(Zs / qs)):  # number of Ncgr coils
                    xenc = q + array([1, 0]) + k * qs
                    wind_mat[0, 0, int(mod(xenc[0] - 1, Zs)), q] = (
                        +Ntcoil
                    )  # right/top/2
                    wind_mat[0, 1, int(mod(xenc[1] - 1, Zs)), q] = (
                        -Ntcoil
                    )  # left/bottom/1
        elif ms != 0.5 and Ncgr % 1 == 0:
            # ms!=0.5 and Ncgr is an integer (ms>0.25 && ms<0.5)
            # new algorithm to reverse the coils
            for q in range(0, int(qs)):
                for k in range(0, int(nlay)):  # number of Ncgr coils
                    for l in range(0, int(Ncgr)):
                        id0 = int(mod(q * Ncgr + 0 + k * qs * Ncgr - 1 + l, Zs))
                        id1 = int(mod(q * Ncgr + 1 + k * qs * Ncgr - 1 + l, Zs))
                        # left / bottom / 1
                        wind_mat[0, 1, id0, q] = -((-1) ** (l + q - 1 + k)) * Ntcoil
                        # right / top / 2
                        wind_mat[0, 0, id1, q] = +((-1) ** (l + q - 1 + k)) * Ntcoil

        else:
            raise WindingT1DefMsError(
                "Winding geometry not handled yet. Enter "
                "your own winding matrix with WindingUD"
                " and contact EOMYS"
            )

        # Set default values
        if self.is_reverse_wind is None:
            self.is_reverse_wind = False
        if self.Nslot_shift_wind is None:
            self.Nslot_shift_wind = 0
        self.Nlayer = 2
        # Apply the transformations
        if self.is_reverse_wind:
            wind_mat = reverse_wind_mat(wind_mat)
        if self.Nslot_shift_wind > 0:
            wind_mat = shift_wind_mat(wind_mat, self.Nslot_shift_wind)

        self.wind_mat = wind_mat
        # Matrix changed, compute again periodicity
        self.per_a = None
        self.is_aper_a = None

    # cf Methods.Machine.WindingUD.init_as_DWL
    def init_as_DWL(self, Zs=None, nlay=1):
        """Compute the Winding Matrix (for winding type 3 or 4) (Nlay_rad=1 or 2,Nlay_tan=1)
        type 3 or 4 : DISTRIBUTED SHORTED PITCH INTEGRAL WINDING

        Parameters
        ----------
        self : WindingUD
            A: WindingUD object
        Zs : int
            Number of Slot (Integer >0)
        nlay: int
            Number of layers

        Raises
        ------
        WindingDefMsError
            Zs/2/p/qs must be an integer

        """
        if Zs is None:
            if self.parent is None:
                raise WindingError(
                    "ERROR: The Winding object must be in a Lamination object."
                )

            if self.parent.slot is None:
                raise WindingError(
                    "ERROR: The Winding object must be in a Lamination object with Slot."
                )

            Zs = self.parent.slot.Zs

        assert Zs > 0, "Zs must be >0"
        assert Zs % 1 == 0, "Zs must be an integer"
        assert nlay in [1, 2], "Number of layer must be 1 or 2"

        coil_pitch = self.coil_pitch
        p = self.p
        qs = self.qs
        ms = Zs / 2.0 / float(p) / float(qs)
        tausp = Zs / 2.0 / float(p)
        Ntcoil = self.Ntcoil  # number of turns per coils
        wind_mat = zeros((nlay, 1, Zs, qs))

        if qs == 3:
            phase_order = [1, -3, 2]
        else:
            phase_order = range(1, qs + 1)
        if ms % 1 != 0:  # if ms isn't an integer
            raise WindingDefMsError(
                "wrong winding definition, Zs/2/p/qs must " "be an integer !"
            )
        ms = int(ms)
        tausp = int(tausp)  # if ms is an integer, tausp is

        # shorted pitch Nlay-layered integral overlapping windings
        for nl in range(0, nlay):
            for i in range(0, p):
                for k in range(0, qs):
                    ph = abs(phase_order[k])
                    # cf Gieras p36
                    z = (
                        arange(1, ms + 1)
                        + i * (Zs / p)
                        + k * ms
                        + nl * (coil_pitch - tausp)
                    )

                    sp = ((z - 1) % Zs).astype(int)  # positive pole
                    sm = ((z + Zs / 2 / p - 1) % Zs).astype(int)  # negative pole
                    for s in sp:
                        wind_mat[nl, 0, s, ph - 1] = Ntcoil * sign(
                            phase_order[k]
                        )  # Accumulation for a single slot
                    for s in sm:
                        wind_mat[nl, 0, s, ph - 1] = -Ntcoil * sign(
                            phase_order[k]
                        )  # Accumulation for a single slot

        # Set default values
        if self.is_reverse_wind is None:
            self.is_reverse_wind = False
        if self.Nslot_shift_wind is None:
            self.Nslot_shift_wind = 0
        self.Nlayer = nlay
        # Apply the transformations
        if self.is_reverse_wind:
            wind_mat = reverse_wind_mat(wind_mat)
        if self.Nslot_shift_wind > 0:
            wind_mat = shift_wind_mat(wind_mat, self.Nslot_shift_wind)

        self.wind_mat = wind_mat
        # Matrix changed, compute again periodicity
        self.per_a = None
        self.is_aper_a = None

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
        is_reverse_wind=False,
        Nslot_shift_wind=0,
        qs=3,
        Ntcoil=7,
        Npcp=2,
        type_connection=0,
        p=3,
        Lewout=0.015,
        conductor=-1,
        coil_pitch=1,
        wind_mat=None,
        Nlayer=1,
        per_a=None,
        is_aper_a=None,
        end_winding=-1,
        is_reverse_layer=False,
        is_change_layer=False,
        is_permute_B_C=False,
        dual_tri_phase_shift=None,
        is_wye=True,
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
            if "is_reverse_wind" in list(init_dict.keys()):
                is_reverse_wind = init_dict["is_reverse_wind"]
            if "Nslot_shift_wind" in list(init_dict.keys()):
                Nslot_shift_wind = init_dict["Nslot_shift_wind"]
            if "qs" in list(init_dict.keys()):
                qs = init_dict["qs"]
            if "Ntcoil" in list(init_dict.keys()):
                Ntcoil = init_dict["Ntcoil"]
            if "Npcp" in list(init_dict.keys()):
                Npcp = init_dict["Npcp"]
            if "type_connection" in list(init_dict.keys()):
                type_connection = init_dict["type_connection"]
            if "p" in list(init_dict.keys()):
                p = init_dict["p"]
            if "Lewout" in list(init_dict.keys()):
                Lewout = init_dict["Lewout"]
            if "conductor" in list(init_dict.keys()):
                conductor = init_dict["conductor"]
            if "coil_pitch" in list(init_dict.keys()):
                coil_pitch = init_dict["coil_pitch"]
            if "wind_mat" in list(init_dict.keys()):
                wind_mat = init_dict["wind_mat"]
            if "Nlayer" in list(init_dict.keys()):
                Nlayer = init_dict["Nlayer"]
            if "per_a" in list(init_dict.keys()):
                per_a = init_dict["per_a"]
            if "is_aper_a" in list(init_dict.keys()):
                is_aper_a = init_dict["is_aper_a"]
            if "end_winding" in list(init_dict.keys()):
                end_winding = init_dict["end_winding"]
            if "is_reverse_layer" in list(init_dict.keys()):
                is_reverse_layer = init_dict["is_reverse_layer"]
            if "is_change_layer" in list(init_dict.keys()):
                is_change_layer = init_dict["is_change_layer"]
            if "is_permute_B_C" in list(init_dict.keys()):
                is_permute_B_C = init_dict["is_permute_B_C"]
            if "dual_tri_phase_shift" in list(init_dict.keys()):
                dual_tri_phase_shift = init_dict["dual_tri_phase_shift"]
            if "is_wye" in list(init_dict.keys()):
                is_wye = init_dict["is_wye"]
        # Set the properties (value check and convertion are done in setter)
        # Call Winding init
        super(WindingUD, self).__init__(
            is_reverse_wind=is_reverse_wind,
            Nslot_shift_wind=Nslot_shift_wind,
            qs=qs,
            Ntcoil=Ntcoil,
            Npcp=Npcp,
            type_connection=type_connection,
            p=p,
            Lewout=Lewout,
            conductor=conductor,
            coil_pitch=coil_pitch,
            wind_mat=wind_mat,
            Nlayer=Nlayer,
            per_a=per_a,
            is_aper_a=is_aper_a,
            end_winding=end_winding,
            is_reverse_layer=is_reverse_layer,
            is_change_layer=is_change_layer,
            is_permute_B_C=is_permute_B_C,
            dual_tri_phase_shift=dual_tri_phase_shift,
            is_wye=is_wye,
        )
        # The class is frozen (in Winding init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        WindingUD_str = ""
        # Get the properties inherited from Winding
        WindingUD_str += super(WindingUD, self).__str__()
        return WindingUD_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from Winding
        if not super(WindingUD, self).__eq__(other):
            return False
        return True

    def compare(self, other, name="self", ignore_list=None, is_add_value=False):
        """Compare two objects and return list of differences"""

        if ignore_list is None:
            ignore_list = list()
        if type(other) != type(self):
            return ["type(" + name + ")"]
        diff_list = list()

        # Check the properties inherited from Winding
        diff_list.extend(
            super(WindingUD, self).compare(
                other, name=name, ignore_list=ignore_list, is_add_value=is_add_value
            )
        )
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object

        # Get size of the properties inherited from Winding
        S += super(WindingUD, self).__sizeof__()
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

        # Get the properties inherited from Winding
        WindingUD_dict = super(WindingUD, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs
        )
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        WindingUD_dict["__class__"] = "WindingUD"
        return WindingUD_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        is_reverse_wind_val = self.is_reverse_wind
        Nslot_shift_wind_val = self.Nslot_shift_wind
        qs_val = self.qs
        Ntcoil_val = self.Ntcoil
        Npcp_val = self.Npcp
        type_connection_val = self.type_connection
        p_val = self.p
        Lewout_val = self.Lewout
        if self.conductor is None:
            conductor_val = None
        else:
            conductor_val = self.conductor.copy()
        coil_pitch_val = self.coil_pitch
        if self.wind_mat is None:
            wind_mat_val = None
        else:
            wind_mat_val = self.wind_mat.copy()
        Nlayer_val = self.Nlayer
        per_a_val = self.per_a
        is_aper_a_val = self.is_aper_a
        if self.end_winding is None:
            end_winding_val = None
        else:
            end_winding_val = self.end_winding.copy()
        is_reverse_layer_val = self.is_reverse_layer
        is_change_layer_val = self.is_change_layer
        is_permute_B_C_val = self.is_permute_B_C
        dual_tri_phase_shift_val = self.dual_tri_phase_shift
        is_wye_val = self.is_wye
        # Creates new object of the same type with the copied properties
        obj_copy = type(self)(
            is_reverse_wind=is_reverse_wind_val,
            Nslot_shift_wind=Nslot_shift_wind_val,
            qs=qs_val,
            Ntcoil=Ntcoil_val,
            Npcp=Npcp_val,
            type_connection=type_connection_val,
            p=p_val,
            Lewout=Lewout_val,
            conductor=conductor_val,
            coil_pitch=coil_pitch_val,
            wind_mat=wind_mat_val,
            Nlayer=Nlayer_val,
            per_a=per_a_val,
            is_aper_a=is_aper_a_val,
            end_winding=end_winding_val,
            is_reverse_layer=is_reverse_layer_val,
            is_change_layer=is_change_layer_val,
            is_permute_B_C=is_permute_B_C_val,
            dual_tri_phase_shift=dual_tri_phase_shift_val,
            is_wye=is_wye_val,
        )
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        # Set to None the properties inherited from Winding
        super(WindingUD, self)._set_None()
