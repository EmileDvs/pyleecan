# Experimental dataclass generated from Generator/ClassesRef/Machine/Winding.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass
from typing import ClassVar

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, Patch, Rectangle

from ..Classes._swat_em import datamodel
from ..definitions import config_dict
from ..Functions._swat_em import plots
from ..Functions._swat_em.config import config
from ..Functions.Geometry.inter_line_line import inter_line_line
from ..Functions.init_fig import init_fig
from ..Functions.Winding.gen_phase_list import gen_name
from ..Functions.Winding.reverse_wind_mat import (
    change_layer,
    permute_B_C,
    reverse_layer,
    reverse_wind_mat,
)
from ..Functions.Winding.shift_wind_mat import shift_wind_mat
from ._error import WindingError
from ._pyleecan_class import PyleecanClass
from .conductor import Conductor
from .end_winding import EndWinding


@dataclass(eq=False)
class Winding(PyleecanClass):
    """Winding class generating connection matrix using Star of slots method (coupling with SWAT-EM)

    Attributes
    ----------
    is_reverse_wind : bool
        True to reverse the default winding algorithm along the airgap (c, b, a instead of a, b, c along the trigonometric direction)
        Default: False
    Nslot_shift_wind : int
        Number of slots to shift the coils obtained with pyleecan winding algorithm (a, b, c becomes b, c, a with Nslot_shift_wind=1)
        Default: 0
    qs : int
        number of phases
        Default: 3; Minimum: 0
    Ntcoil : int
        number of turns per coil
        Default: 7; Minimum: 1
    Npcp : int
        number of parallel circuits per phase
        Default: 2; Minimum: 1
    type_connection : int
        Winding connection : 0 star (Y), 1 triangle (delta), -1 no connection
        Default: 0; Minimum: -1; Maximum: 1
    p : int
        pole pairs number
        Default: 3; Minimum: 1
    Lewout : float
        straight length of the conductors outside the lamination before the curved part of winding overhang [m] - can be negative to tune the average turn length (only used in voltage driven simulations)
        Unit: m; Default: 0.015; Minimum: 0
    conductor : Conductor or None
        Winding's conductor
        Default: None
    coil_pitch : int
        Distance (in slot) between a conductor of a certain phase and the corresponding return conductor
        Default: 1
    wind_mat : ndarray or None
        Winding matrix calculated with Star of slots (from SWAT_EM package)
        Default: None
    Nlayer : int
        Number of different coils in a slot
        Default: 1; Minimum: 1
    per_a : int or None
        Number of spatial periods of the winding
        Default: None; Minimum: 1
    is_aper_a : bool or None
        True if the winding is anti-periodic over space
        Default: None
    end_winding : EndWinding or None
        End Winding's definition
        Default: None
    is_reverse_layer : bool
        True to reverse the layers (rad from False to Nrad-True => Nrad-True to False)
        Default: False
    is_change_layer : bool
        True to change the layer from radial to tangential or tangential to radial
        Default: False
    is_permute_B_C : bool
        True to permute phase B and phase C
        Default: False
    dual_tri_phase_shift : float or None
        Phase shift between both tri-phase systems in dual-tri-phase case
        Unit: rad; Default: None
    is_wye : bool
        True if the alimentation is wye (else delta)
        Default: True
    """

    NAME: ClassVar = "Star of slots"
    PHASE_COLORS = config_dict["PLOT"]["COLOR_DICT"]["PHASE_COLORS"]
    ROTOR_COLOR = config_dict["PLOT"]["COLOR_DICT"]["ROTOR_COLOR"]
    STATOR_COLOR = config_dict["PLOT"]["COLOR_DICT"]["STATOR_COLOR"]
    is_reverse_wind: bool = False
    """True to reverse the default winding algorithm along the airgap (c, b, a instead of a, b, c along the trigonometric direction)"""
    Nslot_shift_wind: int = 0
    """Number of slots to shift the coils obtained with pyleecan winding algorithm (a, b, c becomes b, c, a with Nslot_shift_wind=1)"""
    qs: int = 3
    """number of phases """
    Ntcoil: int = 7
    """number of turns per coil"""
    Npcp: int = 2
    """number of parallel circuits per phase"""
    type_connection: int = 0
    """Winding connection : 0 star (Y), 1 triangle (delta), -1 no connection"""
    p: int = 3
    """pole pairs number"""
    Lewout: float = 0.015
    """straight length of the conductors outside the lamination before the curved part of winding overhang [m] - can be negative to tune the average turn length (only used in voltage driven simulations)"""
    conductor: Conductor | None = None
    """Winding's conductor"""
    coil_pitch: int = 1
    """Distance (in slot) between a conductor of a certain phase and the corresponding return conductor"""
    wind_mat: np.ndarray | None = None
    """Winding matrix calculated with Star of slots (from SWAT_EM package)"""
    Nlayer: int = 1
    """Number of different coils in a slot"""
    per_a: int | None = None
    """Number of spatial periods of the winding"""
    is_aper_a: bool | None = None
    """True if the winding is anti-periodic over space"""
    end_winding: EndWinding | None = None
    """End Winding's definition"""
    is_reverse_layer: bool = False
    """True to reverse the layers (rad from False to Nrad-True => Nrad-True to False)"""
    is_change_layer: bool = False
    """True to change the layer from radial to tangential or tangential to radial"""
    is_permute_B_C: bool = False
    """True to permute phase B and phase C"""
    dual_tri_phase_shift: float | None = None
    """Phase shift between both tri-phase systems in dual-tri-phase case"""
    is_wye: bool = True
    """True if the alimentation is wye (else delta)"""

    # Inlined from Methods.Machine.Winding.clean
    def clean(self):
        """Clean the internal properties (wind_mat and periodicity)

        Parameters
        ----------
        self : Winding
            A Winding object
        """
        self.wind_mat = None
        self.per_a = None
        self.is_aper_a = None

    # Inlined from Methods.Machine.Winding.comp_connection_mat
    def comp_connection_mat(self, Zs=None, p=None):
        """Compute the Winding Matrix for

        Parameters
        ----------
        self : Winding
            A: Winding object
        Zs : int
            Number of Slot (Integer >0)
        p : int
            Number of pole pairs (Integer >0)

        Returns
        -------
        wind_mat: numpy.ndarray
            Winding Matrix (1, 1, Zs, qs)

        Raises
        ------
        WindingT2DefNtError
            Zs/qs/2 must be an integer

        """

        if Zs is None:
            if not hasattr(self.parent, "slot") and not hasattr(
                self.parent, "slot_list"
            ):
                raise WindingError("The Winding object must be in a Lamination object.")

            Zs = self.parent.get_Zs()

        if p is None:
            if self.parent is None:
                raise WindingError("The Winding object must be in a Lamination object.")

            p = self.parent.get_pole_pair_number()

        assert Zs > 0, "Zs must be >0"
        assert Zs % 1 == 0, "Zs must be an integer"

        assert p > 0, "p must be >0"
        assert p % 1 == 0, "p must be an integer"

        qs = self.qs  # Phase Number

        Ntcoil = self.Ntcoil  # number of turns per coils

        Nlayer = self.Nlayer  # number of layers

        # Coil pitch (or coil span)
        if self.coil_pitch in [0, None]:
            # Number of slots per pole and per phase
            spp = Zs / (2 * p * qs)
            if spp > 0.5:
                # distributed winding
                self.coil_pitch = int(qs * spp)
            else:
                # tooth concentrated winding
                self.coil_pitch = 1

        # generate a datamodel for the winding
        wdg = datamodel()

        # generate winding from inputs
        wdg.genwdg(Q=Zs, P=2 * p, m=qs, layers=Nlayer, turns=Ntcoil, w=self.coil_pitch)

        # init connexion matrix
        wind_mat = np.zeros((Nlayer, 1, Zs, qs))

        # get connexion matrix from swat-em
        wind_mat_swat = wdg.get_phases()

        # perform checks
        assert p == wdg.get_num_polepairs(), (
            "number of pole pairs is not as requested (returned "
            + str(wdg.get_num_polepairs())
            + " expected "
            + str(p)
            + ")"
        )
        assert qs == wdg.get_num_phases(), (
            "number of phases is not as requested (returned "
            + str(wdg.get_num_phases())
            + " expected "
            + str(qs)
            + ")"
        )

        # convert swat-em connexion matrix to pyleecan connexion matrix
        for qq, phase in enumerate(wind_mat_swat):
            for ll, layer in enumerate(phase):
                if len(layer) > 0:
                    for cond in layer:
                        wind_mat[Nlayer - ll - 1, 0, abs(cond) - 1, qq] = (
                            np.sign(cond) * Ntcoil
                        )

        # permute radial and tangential layers if coil span is 1
        if wdg.get_coilspan() == 1:
            wind_mat = np.swapaxes(wind_mat, 0, 1)

        # check that requested number of parallel connections is feasible
        Npcp_list = wdg.get_parallel_connections()
        if self.Npcp is None:
            self.Npcp = Npcp_list[0]
        elif self.Npcp > 2 * p:
            # self.Npcp = 2 * p
            self.get_logger().warning(
                "Number of parallel circuits per phase should be < 2*p, current value is: "
                + str(self.Npcp)
            )
        # if self.Npcp not in Npcp_list:

        #     if self.Npcp is not None:
        #         self.get_logger().warning(
        #             "Requested number of parallel circuits per phase is not feasible, assign it to: "
        #             + str(Npcp_list[0])
        #         )

        #     self.Npcp = Npcp_list[0]

        # enforce the number of layers if it is not as requested
        Nlayer_actual = wdg.get_num_layers()
        if self.Nlayer != Nlayer_actual:
            self.Nlayer = Nlayer_actual
            self.get_logger().info(
                "Requested number of layers is not feasible, assign it to: "
                + str(Nlayer_actual)
            )

        # get periodicities
        # self.per_a = wdg.get_periodicity_t()
        # self.is_aper_a = wdg.get_is_symmetric()

        # To check periodicities swat-em / pyleecan definitions
        self.per_a, self.is_aper_a = self.comp_periodicity(wind_mat=wind_mat)
        # if is_aper_a:  # Different def for Anti per
        #     per_a = per_a / 2
        # if self.per_a != per_a or self.is_aper_a != is_aper_a:
        #     self.get_logger().warning(
        #         "(Anti-)periodicity calculated by pyleecan and SWAT_EM differs"
        #     )

        # Set default values
        if self.is_reverse_wind is None:
            self.is_reverse_wind = False
        if self.Nslot_shift_wind is None:
            self.Nslot_shift_wind = 0

        return wind_mat

    # Inlined from Methods.Machine.Winding.comp_length_endwinding
    def comp_length_endwinding(self):
        """Compute the Winding overhang length on one side for a half-turn[m]

        Parameters
        ----------
        self: Winding
            A Winding object

        Returns
        -------
        Lewout : float
            End-winding length on one side for a half-turn [m].
        """

        if self.end_winding is None:
            return self.Lewout
        else:
            return self.Lewout + self.end_winding.comp_length()

    # Inlined from Methods.Machine.Winding.comp_Ncps
    def comp_Ncps(self):
        """Compute the number of conductors per slot

        Parameters
        ----------
        self : Winding
            A Winding object

        Returns
        -------
        Ncps: float
            Number of conductors per slot

        """
        Ncps_ = abs(self.get_connection_mat().sum(axis=(0, 1))).sum(axis=1)
        Ncps = Ncps_.mean()

        if Ncps_.std() != 0:
            self.get_logger().warning(
                "LamSlotWind.comp_fill_factor: "
                "Uneven number of conductors per slot. "
                + "Max. number of conductors will be used to compute slot fill factor."
            )
            Ncps = Ncps_.max()

        return Ncps

    # Inlined from Methods.Machine.Winding.comp_Ncspc
    def comp_Ncspc(self, Zs=None):
        """Compute the number of coils in series per parallel circuit

        Parameters
        ----------
        self : Winding
            A Winding object
        Zs : int
            number of slot

        Returns
        -------
        Ncspc: float
            Number of coils in series per parallel circuit

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

        (Nrad, Ntan) = self.get_dim_wind()
        Ncspc = Zs * Nrad * Ntan / (2.0 * self.qs * self.Npcp)

        return Ncspc

    # Inlined from Methods.Machine.Winding.comp_Ntsp
    def comp_Ntsp(self, Zs=None):
        """Compute the number of turns in series per phase

        Parameters
        ----------
        self : Winding
            A Winding object
        Zs : int
            Number of slot

        Returns
        -------
        Ntspc: float
            Number of turns in series per phase

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

        # effective number of turns in series per phase from connection matrix
        Ntspc_eff_ = (
            abs(self.get_connection_mat(Zs).sum(axis=(0, 1))).sum(axis=0)
            / self.Npcp
            / 2
        )
        if Ntspc_eff_.std() != 0:
            self.get_logger().warning(
                "Winding.comp_Ntsp: "
                "Uneven number of turns in series per phase. "
                + "Mean number of turns will be used."
            )

        Ntspc_eff = Ntspc_eff_.mean()

        return Ntspc_eff

    # Inlined from Methods.Machine.Winding.comp_periodicity
    def comp_periodicity(self, wind_mat=None):
        """Computes the winding matrix (anti-)periodicity

        Parameters
        ----------
        self : Winding
            A Winding object
        wind_mat : ndarray
            Winding connection matrix

        Returns
        -------
        per_a: int
            Number of spatial periods of the winding
        is_aper_a: bool
            True if the winding is anti-periodic over space

        """

        if wind_mat is None:
            wind_mat = self.get_connection_mat()

        assert wind_mat.ndim == 4, "dim 4 expected for wind_mat"

        Zs = wind_mat.shape[2]  # Number of Slot
        qs = wind_mat.shape[3]  # Number of phase

        # Summing on all the layers (Nlay_r and Nlay_theta)
        wind_mat2 = wind_mat
        # Avoid to squeeze qs=1 (WRSM)
        if wind_mat.shape[1] == 1:
            wind_mat2 = np.squeeze(wind_mat2, 1)
        if wind_mat.shape[0] == 1:
            wind_mat2 = np.squeeze(wind_mat2, 0)

        if wind_mat2.ndim == 4:  # rad and tan > 2
            Nlay = wind_mat2.shape[0] * wind_mat2.shape[1]
            wind_mat2 = wind_mat2.reshape((Nlay, Zs, qs))
        elif wind_mat2.ndim == 2:
            Nlay = 1
            wind_mat2 = wind_mat2[None, :, :]
        else:
            Nlay = wind_mat2.shape[0]

        Nperw = Zs  # Number of electrical period of the winding
        is_aper = True  # True if winding pattern is anti-periodic

        # Looking for the periodicity of each phase
        for q in range(qs):
            # Looking for the periodicity of each layer
            for l in range(Nlay):
                # FFT of connectivity array for the given layer and phase
                wind_mat_ql_fft = np.fft.fft(wind_mat2[l, :, q])
                # Find indices of nonzero amplitudes
                I0 = np.where(np.abs(wind_mat_ql_fft) > 1e-3)[0]
                if len(I0) == 0:  # This phase is not present in this layer
                    pass  # No impact on symmetry
                else:
                    # Periodicity is given by the non zero lowest order
                    Nperw_ql = I0[0] if I0[0] != 0 else I0[1]
                    Nperw = np.gcd(Nperw, Nperw_ql)
                    if I0[0] == 0:
                        # Anti-periodicity is necessary false if there is a constant component
                        is_aper = False
                    else:
                        # Anti-periodicity is true if all non-zero components are odd multiple of periodicity
                        is_aper = is_aper and np.all(np.mod(I0 / Nperw_ql, 2) == 1)

                if Nperw == 1 and not is_aper:
                    # No need to further continue if there is no anti-periodicity
                    break

        # Multiply periodicity number by two in case of anti-periodicity
        Nperw = Nperw * 2 if is_aper else Nperw

        return int(Nperw), bool(is_aper)

    # Inlined from Methods.Machine.Winding.comp_phasor_angle
    def comp_phasor_angle(self, Zs=None):
        """Compute the phasor angle of the winding phases related to the first slot

        Parameters
        ----------
        self : Winding
            A: Winding object
        Zs : int
            Number of Slot (Integer >0)

        Returns
        -------
        angle_vec: numpy.ndarray
            Phasor Angle Vector (qs)

        Raises
        ------

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

        wind_mat = self.get_connection_mat(Zs)
        p = self.p
        qs = self.qs  # number of phases

        slot_ang = (
            np.linspace(0, Zs, num=Zs, endpoint=False) * 2 * np.pi / Zs * p
        )  # slot electrical angle
        phasor = np.exp(1j * slot_ang)  # slot voltage phasor

        angle_vec = np.zeros(qs)

        for phase in range(qs):
            wind_sum = np.sum(wind_mat[:, :, :, phase], (0, 1))
            phasor_sum = np.sum(wind_sum * phasor)
            angle_vec[phase] = np.angle(phasor_sum)

        return angle_vec

    # Inlined from Methods.Machine.Winding.comp_winding_factor
    def comp_winding_factor(self, Harmonics=[1]):
        """Compute the winding factor of phase 1 (asuming symmetry)

        Parameters
        ----------
        self : Winding
            A: Winding object
        Harmonics : list of floats
            list of harmonics to calculate the winding factor

        Returns
        -------
        xi: numpy.ndarray
            winding factor

        Raises
        ------

        """
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

        wind_mat = self.get_connection_mat(Zs)
        p = self.p

        # slot electrical angle
        slot_ang = np.linspace(0, Zs, num=Zs, endpoint=False) * 2 * np.pi / Zs * p

        phase = 0
        wind_ph1 = np.sum(wind_mat[:, :, :, phase], (0, 1))
        wind_ref = np.sum(np.abs(wind_mat[:, :, :, phase]))

        xi = []

        for harm in Harmonics:
            xi.append(
                np.abs(np.sum(np.exp(1j * slot_ang * harm) * wind_ph1)) / wind_ref
            )

        xi = np.array(xi)

        return xi

    # Inlined from Methods.Machine.Winding.export_to_csv
    def export_to_csv(
        self,
        file_path=None,
        is_add_header=True,
        is_skip_empty=False,
        *,
        ZS_NAME="Slot Id",
        COIL_NAME="Ntcoil",
        RAD_NAME="Rad Layer Id",
        TAN_NAME="Tan Layer Id",
        SEP=",",
    ):
        """Export the winding matrix to a csv file. One matrix for each phase
        Column Slot id, Ntcoil, Rad id, Tan id

        Parameters
        ----------
        self : Winding
            A: Winding object
        file_path : str
            Path to the file to save
        is_add_header : bool
            True to add first line and first column
        is_skip_empty : bool
            True to remove the lines with Ntcoil=0
        """

        # parse file_path
        if file_path[-4:] != ".csv":
            file_path += ".csv"

        # Get matrix
        wind_mat = self.get_connection_mat()
        Nrad = wind_mat.shape[0]
        Ntan = wind_mat.shape[1]
        Zs = wind_mat.shape[2]
        qs = wind_mat.shape[3]

        # Write the file
        csv_txt = ""
        if is_add_header:
            csv_txt = (
                '"'
                + str(wind_mat.shape)
                + '"'
                + SEP
                + ZS_NAME
                + SEP
                + COIL_NAME
                + SEP
                + RAD_NAME
                + SEP
                + TAN_NAME
                + "\n"
            )

        phases = gen_name(qs, is_add_phase=True)
        for ii, name in enumerate(phases):
            Nb_line = 0  # Add header on first line only
            for jj in range(Zs):
                for kk in range(Nrad):
                    for ll in range(Ntan):
                        value = wind_mat[kk, ll, jj, ii]
                        if not (is_skip_empty and wind_mat[kk, ll, jj, ii] == 0):
                            if is_add_header and Nb_line == 0:
                                csv_txt += name + " Layout" + SEP
                            elif is_add_header:
                                csv_txt += SEP
                            csv_txt += str(jj) + SEP
                            csv_txt += str(value) + SEP
                            csv_txt += str(kk) + SEP
                            csv_txt += str(ll) + SEP + "\n"
                            Nb_line += 1
            # Separate each phase by an empty line
            csv_txt += "\n"

        # Write the csv file
        with open(file_path, "w") as csv_file:
            csv_file.write(csv_txt)

    # Inlined from Methods.Machine.Winding.get_connection_mat
    def get_connection_mat(self, Zs=None, p=None):
        """Get the Winding Matrix

        Parameters
        ----------
        self : Winding
            A: Winding object
        Zs : int
            Number of Slot (Integer >0)
        p : int
            Number of pole pairs (Integer >0)

        Returns
        -------
        wind_mat: numpy.ndarray
            Winding Matrix (1, 1, Zs, qs)


        """

        if self.wind_mat is None:
            self.wind_mat = self.comp_connection_mat(Zs=Zs, p=p)
        elif Zs is not None and self.wind_mat.shape[2] != Zs:
            # Winding matrix is outdated
            self.clean()
            self.wind_mat = self.comp_connection_mat(Zs=Zs, p=p)

        wind_mat = self.wind_mat.copy()
        # Apply the transformations
        if self.is_reverse_wind:
            wind_mat = reverse_wind_mat(wind_mat)
        if self.Nslot_shift_wind not in [0, None]:
            wind_mat = shift_wind_mat(wind_mat, self.Nslot_shift_wind)
        if self.is_reverse_layer:
            wind_mat = reverse_layer(wind_mat)
        if self.is_change_layer:
            wind_mat = change_layer(wind_mat)
        if self.is_permute_B_C:
            wind_mat = permute_B_C(wind_mat)
        return wind_mat

    # Inlined from Methods.Machine.Winding.get_dim_wind
    def get_dim_wind(self):
        """Get the two first dimension of the winding matrix

        Parameters
        ----------
        self : Winding
            A Winding object

        Returns
        -------
        (Nrad, Ntan): tuple
            Number of layer in radial and tangential direction

        """

        wind_mat = self.get_connection_mat()

        return wind_mat.shape[0:2]

    # Inlined from Methods.Machine.Winding.get_periodicity
    def get_periodicity(self):
        """Computes the winding matrix (anti-)periodicity

        Parameters
        ----------
        self : Winding
            A Winding object

        Returns
        -------
        per_a: int
            Number of spatial periods of the winding
        is_aper_a: bool
            True if the winding is anti-periodic over space

        """

        if self.per_a is None or self.is_aper_a is None:
            self.per_a, self.is_aper_a = self.comp_periodicity()

        return self.per_a, self.is_aper_a

    # Inlined from Methods.Machine.Winding.plot_linear
    def plot_linear(
        self,
        fig=None,
        ax=None,
        is_max_sym=True,
        is_show_fig=True,
        save_path=None,
        win_title=None,
        is_legend=True,
    ):
        """Plots the winding linear pattern. Method based on plot_overhang method of swat-em module

        Parameters
        ----------
        self : Winding
            A Winding object
        fig : Matplotlib.figure.Figure
            existing figure to use if None create a new one
        ax : Matplotlib.axes.Axes object
            Axis on which to plot the data
        sym : int
            Symmetry factor (1= full machine, 2= half of the machine...)
        is_max_sym : bool
            To only plot the linear pattern on the maximum symetry of the machine
        is_show_fig : bool
            To call show at the end of the method
        save_path : str
            full path including folder, name and extension of the file to save if save_path is not None
        win_title : str
            Title for the window
        is_legend : bool
            True to add the legend
        """

        # Recovering the colors of the phases
        if (
            not isinstance(config_dict["PLOT"]["COLOR_DICT"]["PHASE_COLORS"][0], str)
            and len(config_dict["PLOT"]["COLOR_DICT"]["PHASE_COLORS"][0]) == 4
        ):  # convert rgba to hex
            config["plt"]["phase_colors"] = [
                "#{:02x}{:02x}{:02x}".format(
                    int(color[0] * 255 * (1 - color[3]) + 255 * color[3]),
                    int(color[1] * 255 * (1 - color[3]) + 255 * color[3]),
                    int(color[2] * 255 * (1 - color[3]) + 255 * color[3]),
                )
                for color in config_dict["PLOT"]["COLOR_DICT"]["PHASE_COLORS"]
            ]
        else:
            config["plt"]["phase_colors"] = config_dict["PLOT"]["COLOR_DICT"][
                "PHASE_COLORS"
            ]

        # Step 1 : Generate a datamodel for the winding
        Zs = self.parent.get_Zs()
        p = self.parent.get_pole_pair_number()

        # Generating the winding from inputs and recovering its attributes
        wdg = datamodel()
        wdg.genwdg(
            Q=Zs,
            P=2 * p,
            m=self.qs,
            layers=self.Nlayer,
            turns=self.Ntcoil,
            w=self.coil_pitch,
        )

        # Detecting the direction of the layer (tangential or radial)
        # If Nlayer > 1 then we have to precise if the direction is tangential or radial to draw the coil at the right location in the slot
        Nrad, Ntan = self.get_dim_wind()
        if Nrad < Ntan:
            is_tangential_layer = True
        else:
            is_tangential_layer = False

        # Input used to build the coils that we will display
        bz = 0.5  # tooth width
        hz = 0.5  # slot height
        h1 = 0.6  # height of the coil side
        h2 = 0.5 + self.coil_pitch / 6  # height of the winding overhang
        db1 = (
            0 if self.Nlayer == 1 or not is_tangential_layer else 0.1
        )  # distance between coil side and slot center

        # Only plotting the machine for a period (if antiperiod given using the full period)
        # This done by only taking into account Zs for a period
        if is_max_sym:
            per, is_antiper = self.comp_periodicity()
            Zs_per = Zs // (per // 2) if is_antiper else Zs // per
        else:
            Zs_per = Zs

        # Step 2: Creating a list of patches and lines that will be plotted
        patches = []
        lines_dict = {}

        # Step 2-1: Adding slot surface as rectangural patches
        xy = [(k - 0.5 - bz / 2, -hz / 2) for k in range(Zs_per + 1)]
        width = np.ones([Zs_per + 1]) * bz
        height = hz

        # First tooth is cut in half so we have two surfaces instead of 1
        xy[0] = (-0.5, -hz / 2)
        width[0] = bz / 2
        width[-1] = bz / 2

        for idx_slot in range(Zs_per + 1):
            point = xy[idx_slot]
            width_patch = width[idx_slot]
            patch = Rectangle(
                xy=point,
                width=width_patch,
                height=height,
                color=self.STATOR_COLOR if self.parent.is_stator else self.ROTOR_COLOR,
                linewidth=0,
            )
            patches.append(patch)

        # Step 2-2: Adding coil pattern as line between six points
        head = wdg.get_wdg_overhang(optimize_overhang=False)

        # Taking into account slot shifting transformation
        if self.Nslot_shift_wind not in [0, None]:
            Nslot_shift_wind = self.Nslot_shift_wind
        else:
            Nslot_shift_wind = 0

        # Permuting B and C if asked
        if self.is_permute_B_C:
            head_2 = head.copy()
            head_2[1] = head[2]
            head_2[2] = head[1]
            head = head_2

        for idx_phase, phase in enumerate(head):
            coils = []  # list of points that constitutes the coils of a phase
            for coil in phase:
                # Step 2-2-1: Building 6 points to have the following coil pattern
                #        P1
                #       /  \
                #      /    \
                #     P0    P2
                #     |      |
                #     |      |
                #     |      |
                #     P5     P3
                #      \    /
                #       \  /
                #        P4

                P0 = db1 + 1j * h1
                P1 = coil[1] / 2 + 1j * h2
                P2 = coil[1] - db1 + 1j * h1
                P3 = coil[1] - db1 - 1j * h1
                P4 = coil[1] / 2 - 1j * h2
                P5 = db1 - 1j * h1

                point_list = [P0, P1, P2, P3, P4, P5]
                x_, y_ = np.real(point_list), np.imag(point_list)

                # Step 2-2-2: Shifting the coil pattern to the right slot according to the direction of the winding and the potential winding transformation
                direct = coil[2]
                if self.is_reverse_wind:
                    if direct < 0:
                        slot_shift = Zs - coil[0][0]
                    else:
                        slot_shift = Zs - coil[0][1]
                else:
                    if direct > 0:
                        slot_shift = coil[0][0] - 1
                    else:
                        slot_shift = coil[0][1] - 1

                x_ += slot_shift + Nslot_shift_wind

                point_list_updated = x_ + 1j * y_

                # Step 2-2-3: If a coil cross the right border then it must be splitted in 2,
                # if the coil is completely out of bounds then we do not plot it at all
                idx_point_too_far = [i for i in range(len(x_)) if x_[i] > Zs_per - 0.5]
                # if the coil is on the left border, not plotting it (overlap with coil splitted on right border)
                idx_point_too_low = [i for i in range(len(x_)) if x_[i] < -0.5]
                if (
                    idx_point_too_far != []
                    and len(idx_point_too_far) != len(x_)
                    and idx_point_too_low == []
                ):
                    wrong_points = x_[idx_point_too_far] + 1j * y_[idx_point_too_far]

                    # Correcting first point so that it is on the right border (new P2 point) and getting P3 as the conjugate of P2
                    # if there more than two points that are incorrect we have to remove them as we only need the first and the last one
                    idx_point_to_remove = (
                        idx_point_too_far[1:-1] if len(idx_point_too_far) > 2 else []
                    )
                    idx_point_too_far = [idx_point_too_far[0], idx_point_too_far[-1]]

                    # For the point that we have to correct, we have to find the intersection
                    # between the segments that are too far and a vertical line on Y= Zs_per-0.5
                    wrong_point = (
                        x_[idx_point_too_far[0]] + 1j * y_[idx_point_too_far[0]]
                    )
                    previous_point = (
                        x_[idx_point_too_far[0] - 1] + 1j * y_[idx_point_too_far[0] - 1]
                    )

                    lim_axis_y_point_A = Zs_per - 0.5 + 1j * h2
                    lim_axis_y_point_B = Zs_per - 0.5 - 1j * h2

                    point_correct = inter_line_line(
                        previous_point,
                        wrong_point,
                        lim_axis_y_point_A,
                        lim_axis_y_point_B,
                    )

                    # Listing the point corrected and its conjugate
                    point_corrected = []
                    point_corrected.append(point_correct[0])
                    point_corrected.append(np.conjugate(point_correct[0]))

                    # Putting the corrected point on the left border to complete the coil
                    point_to_add = np.array(point_corrected) - Zs_per
                    point_to_add = np.insert(point_to_add, 1, wrong_points - Zs_per)

                    # Replacing the incorrect point by the new P2 and P3
                    for idx_point, _ in enumerate(idx_point_too_far):
                        point_list_updated[idx_point_too_far[idx_point]] = (
                            point_corrected[idx_point]
                        )

                    # Removing point that are not necessary (when more that 2 point are out of bounds)
                    if idx_point_to_remove != []:
                        point_list_updated = np.delete(
                            point_list_updated, idx_point_to_remove
                        )

                    coils.append(point_list_updated)
                    coils.append(point_to_add)
                elif len(idx_point_too_far) != len(x_) and idx_point_too_low == []:
                    coils.append(point_list_updated)

                # If we apply the reverse winding transformation then we must invert the the signe of the coil
                if self.is_reverse_wind:
                    direct *= -1

                # Step 2-2-4: Adding arrow patch for each coil between P2<->P3 and P5<->P0 (direction depending on winding direction)
                if len(idx_point_too_far) != len(x_) and idx_point_too_low == []:
                    if idx_point_too_far != []:
                        # If the coil is splitted, then the point of the arrow are different compared with other case
                        if direct > 0:
                            # Winding direction from left to right
                            start_point_1 = point_list_updated[-1]
                            start_point_2 = point_to_add[len(point_to_add) // 2 - 1]

                        else:
                            # Winding direction from right to left
                            start_point_1 = point_list_updated[0]
                            start_point_2 = point_to_add[len(point_to_add) // 2]
                    else:
                        if direct > 0:
                            # Winding direction from left to right
                            start_point_1 = point_list_updated[5]
                            start_point_2 = point_list_updated[2]

                        else:
                            # Winding direction from right to left
                            start_point_1 = point_list_updated[0]
                            start_point_2 = point_list_updated[3]

                    arrow_1 = FancyArrowPatch(
                        (start_point_1.real, start_point_1.imag),
                        (start_point_1.real, 0),
                        facecolor=self.PHASE_COLORS[idx_phase],
                        linewidth=0,
                        arrowstyle="Simple, tail_width=0, head_width=8, head_length=12",
                    )
                    arrow_2 = FancyArrowPatch(
                        (start_point_2.real, start_point_2.imag),
                        (start_point_2.real, 0),
                        facecolor=self.PHASE_COLORS[idx_phase],
                        linewidth=0,
                        arrowstyle="Simple, tail_width=0, head_width=8, head_length=12",
                    )

                    patches.append(arrow_1)
                    patches.append(arrow_2)

            # Step 2-2-4: Keeping the coils of each phase inside a dict
            lines_dict["Phase " + str(idx_phase + 1)] = coils

        # Step 3: plotting the line and patches that we computed before
        # Step 3-1: Initializing the figure
        (fig, ax, patch_leg, label_leg) = init_fig(fig=fig, ax=ax, shape="rectangle")

        # Step 3-2: Drawing the coils
        for idx_phase, phase in enumerate(lines_dict):
            for coil in lines_dict[phase]:
                for idx_coil in range(len(coil)):
                    # If the line begin at P5 then it ends at P0
                    if idx_coil == len(coil) - 1:
                        begin = coil[idx_coil]
                        end = coil[0]
                    # Drawing the line betwe PN and PN+1
                    else:
                        begin = coil[idx_coil]
                        end = coil[idx_coil + 1]

                    # Adding condition to make sure that we do not draw lines between two point on the left or  the right border
                    if (
                        np.round(np.real(begin), decimals=1) != -0.5
                        or np.round(np.real(end), decimals=1) != -0.5
                    ) and (
                        np.round(np.real(begin), decimals=1) != Zs_per - 0.5
                        or np.round(np.real(end), decimals=1) != Zs_per - 0.5
                    ):
                        points = np.array([begin, end])
                        ax.plot(
                            points.real,
                            points.imag,
                            color=self.PHASE_COLORS[idx_phase],
                        )

        # Step 3-3: Adding stator tooth patches to the figure
        for patch in patches:
            ax.add_patch(patch)

        # Step 3-4: Adding plot slot number between each tooth
        for slot_nb in range(Zs_per):
            ax.annotate(
                xy=(slot_nb, -hz / 2),
                text=str(slot_nb + 1),
                family=config_dict["PLOT"]["FONT_NAME"],
                horizontalalignment="center",
                color="k",
            )

        # Step 3-5: Setting limits of the figure and removing axes
        ax.set_xlim(-0.5, Zs_per - 0.5)
        ax.set_ylim(-h2 * 1.2, h2 * 1.2)
        ax.set_axis_off()

        # Step 3-6: Setting the title of the window and of the figure
        if self.parent.is_stator:
            title = "Stator winding linear pattern"
            prefix = "Stator "
        else:
            title = "Rotor winding linear pattern"
            prefix = "Rotor "
        # Add machine name if available
        if self.parent.parent is not None and self.parent.parent.name not in ["", None]:
            win_title = self.parent.parent.name + " " + title
        else:
            win_title = title
        manager = plt.get_current_fig_manager()
        if manager is not None:
            manager.set_window_title(win_title)
        ax.set_title(win_title)

        # Step 3-7: Setting the legend of the figure
        # Adding lamination name in the lamination
        if self.parent.is_stator and "Stator" not in label_leg:
            patch_leg.append(Patch(color=self.STATOR_COLOR))
            label_leg.append("Stator")
        elif not self.parent.is_stator and "Rotor" not in label_leg:
            patch_leg.append(Patch(color=self.ROTOR_COLOR))
            label_leg.append("Rotor")

        # Adding each Phase name in the lamination
        phase_name = [prefix + n for n in gen_name(self.qs, is_add_phase=True)]
        for idx_phase_nb in range(self.qs):
            # Avoid adding twice the same label
            if not phase_name[idx_phase_nb] in label_leg:
                index = idx_phase_nb % len(self.PHASE_COLORS)
                patch_leg.append(Patch(color=self.PHASE_COLORS[index]))
                label_leg.append(phase_name[idx_phase_nb])

        # Adding the legend if necessary
        if is_legend:
            ax.legend(patch_leg, label_leg, bbox_to_anchor=(1, 1))

        fig.tight_layout()

        # Saving the figure if necessary
        if save_path is not None:
            fig.savefig(save_path)
            plt.close(fig=fig)

        # Displaying the figure if necessary
        if is_show_fig:
            fig.show()

        return fig, ax

    # Inlined from Methods.Machine.Winding.plot_radial
    def plot_radial(self, is_show_fig=True):
        """Plots the winding radial pattern

        Parameters
        ----------
        self : Winding
            A Winding object
        is_show_fig : bool
            True to call fig.show

        """
        Zs = self.parent.get_Zs()

        p = self.parent.get_pole_pair_number()

        # generate a datamodel for the winding
        wdg = datamodel()

        # generate winding from inputs
        wdg.genwdg(
            Q=Zs,
            P=2 * p,
            m=self.qs,
            layers=self.Nlayer,
            turns=self.Ntcoil,
            w=self.coil_pitch,
        )
        if (
            not isinstance(config_dict["PLOT"]["COLOR_DICT"]["PHASE_COLORS"][0], str)
            and len(config_dict["PLOT"]["COLOR_DICT"]["PHASE_COLORS"][0]) == 4
        ):  # rgba to hex
            config["plt"]["phase_colors"] = [
                "#{:02x}{:02x}{:02x}".format(
                    int(color[0] * 255 * (1 - color[3]) + 255 * color[3]),
                    int(color[1] * 255 * (1 - color[3]) + 255 * color[3]),
                    int(color[2] * 255 * (1 - color[3]) + 255 * color[3]),
                )
                for color in config_dict["PLOT"]["COLOR_DICT"]["PHASE_COLORS"]
            ]
        else:
            config["plt"]["phase_colors"] = config_dict["PLOT"]["COLOR_DICT"][
                "PHASE_COLORS"
            ]
        plt = plots._polar_layout_plot(None, None, wdg)
        plt.plot(show=is_show_fig, optimize_overhang=False)
