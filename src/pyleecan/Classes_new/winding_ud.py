# Experimental dataclass generated from Generator/ClassesRef/Machine/WindingUD.csv
"""Generated experimental dataclass; do not edit by hand."""

import os
from csv import reader
from dataclasses import dataclass
from typing import ClassVar

import numpy as np

from ..Functions.Winding.reverse_wind_mat import reverse_wind_mat
from ..Functions.Winding.shift_wind_mat import shift_wind_mat
from .winding import Winding


@dataclass(eq=False)
class WindingUD(Winding):
    """User defined winding

    Attributes
    ----------
    """

    NAME: ClassVar = "User defined"

    # Inlined from Methods.Machine.WindingUD.import_from_csv
    def import_from_csv(
        self, file_path=None, *, ZS_COL=0, COIL_COL=1, RAD_COL=2, TAN_COL=3
    ):
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
        if not os.path.isfile(file_path):
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
            wind_mat = np.zeros(wind_shape)

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
                wind_mat = np.tile(wind_mat, (1, 1, Zs // wind_mat.shape[2], 1))

        # Update property
        self.clean()  # Remove periodicity
        self.wind_mat = wind_mat
        self.Nlayer = wind_shape[0] * wind_shape[1]
        self.qs = wind_shape[3]
        self.Ntcoil = np.amax(self.wind_mat)

    # Inlined from Methods.Machine.WindingUD.init_as_CW1L
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
        wind_mat = np.zeros((1, 1, Zs, qs))

        for k in range(0, int(Nt)):  # winding alternatively the teeth
            for q in range(0, qs):
                xenc = q * 4 + k * 2 * qs + np.array([1, 2])
                wind_mat[0][0][int((xenc[0] - 1) % Zs)][q] = np.power(
                    -1, xenc[0] + k + 1
                )
                wind_mat[0][0][int((xenc[1] - 1) % Zs)][q] = np.power(
                    -1, xenc[1] + k + 1
                )

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

    # Inlined from Methods.Machine.WindingUD.init_as_CW2LR
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

        wind_mat = np.zeros((2, 1, Zs, self.qs))
        # creates highest harmonic at Zs/2+1 and Zs/2-1
        if ms == 0.5:  # then Zs/qs is integer
            # traditional non overlapping all teeth wound winding
            for q in range(0, self.qs):
                for k in range(0, Zs // self.qs):  # number of Ncgr coils
                    xenc = q + np.array([1, 0]) + k * qs
                    wind_mat[
                        0, 0, int(np.mod(xenc[0] - 1, Zs)), q
                    ] = +Ntcoil  # right/top/2
                    wind_mat[
                        1, 0, int(np.mod(xenc[1] - 1, Zs)), q
                    ] = -Ntcoil  # left/bottom/1
        elif (
            ms != 0.5 and Ncgr % 1 == 0
        ):  # ms!=0.5 and Ncgr is an integer (ms>0.25 && ms<0.5)
            # new algorithm to reverse the coils
            for q in range(0, self.qs):
                for k in range(0, int((Zs // self.qs) // Ncgr)):  # number of Ncgr coils
                    for l in range(0, int(Ncgr)):
                        id0 = int(np.mod(q * Ncgr + 0 + k * qs * Ncgr - 1 + l, Zs))
                        id1 = int(np.mod(q * Ncgr + 1 + k * qs * Ncgr - 1 + l, Zs))
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

    # Inlined from Methods.Machine.WindingUD.init_as_CW2LT
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

        wind_mat = np.zeros((1, 2, Zs, int(qs)))
        # creates highest harmonic at Zs/2+1 and Zs/2-1
        if ms == 0.5:  # then Zs/qs is integer
            # traditional non overlapping all teeth wound winding
            for q in range(0, int(qs)):
                for k in range(0, int(Zs / qs)):  # number of Ncgr coils
                    xenc = q + np.array([1, 0]) + k * qs
                    wind_mat[
                        0, 0, int(np.mod(xenc[0] - 1, Zs)), q
                    ] = +Ntcoil  # right/top/2
                    wind_mat[
                        0, 1, int(np.mod(xenc[1] - 1, Zs)), q
                    ] = -Ntcoil  # left/bottom/1
        elif ms != 0.5 and Ncgr % 1 == 0:
            # ms!=0.5 and Ncgr is an integer (ms>0.25 && ms<0.5)
            # new algorithm to reverse the coils
            for q in range(0, int(qs)):
                for k in range(0, int(nlay)):  # number of Ncgr coils
                    for l in range(0, int(Ncgr)):
                        id0 = int(np.mod(q * Ncgr + 0 + k * qs * Ncgr - 1 + l, Zs))
                        id1 = int(np.mod(q * Ncgr + 1 + k * qs * Ncgr - 1 + l, Zs))
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

    # Inlined from Methods.Machine.WindingUD.init_as_DWL
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
        wind_mat = np.zeros((nlay, 1, Zs, qs))

        if qs == 3:
            phase_order = [1, -3, 2]
        else:
            phase_order = range(1, qs + 1)
        if ms % 1 != 0:  # if ms isn't an integer
            raise WindingDefMsError(
                "wrong winding definition, Zs/2/p/qs must be an integer !"
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
                        np.arange(1, ms + 1)
                        + i * (Zs / p)
                        + k * ms
                        + nl * (coil_pitch - tausp)
                    )

                    sp = ((z - 1) % Zs).astype(int)  # positive pole
                    sm = ((z + Zs / 2 / p - 1) % Zs).astype(int)  # negative pole
                    for s in sp:
                        wind_mat[nl, 0, s, ph - 1] = Ntcoil * np.sign(
                            phase_order[k]
                        )  # Accumulation for a single slot
                    for s in sm:
                        wind_mat[nl, 0, s, ph - 1] = -Ntcoil * np.sign(
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

    class WindingError(Exception):
        """ """

    class WindingT2DefNtError(WindingError):
        """

        Parameters
        ----------

        Returns
        -------

        Raises
        ------
        must
            be 0

        """

    class WindingT5DefMsError(WindingError):
        """

        Parameters
        ----------

        Returns
        -------

        Raises
        ------
        must
            be 0

        """

    class WindingT1DefMsError(WindingError):
        """

        Parameters
        ----------

        Returns
        -------

        Raises
        ------
        must
            be 0

        """

    class WindingDefMsError(WindingError):
        """ """


WindingError = WindingUD.WindingError
WindingT2DefNtError = WindingUD.WindingT2DefNtError
WindingT5DefMsError = WindingUD.WindingT5DefMsError
WindingT1DefMsError = WindingUD.WindingT1DefMsError
WindingDefMsError = WindingUD.WindingDefMsError
