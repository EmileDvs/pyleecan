# -*- coding: utf-8 -*-
# File generated according to Generator/ClassesRef/Machine/Winding.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Machine/Winding
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
from pyleecan.Classes._frozen import FrozenClass

# Import all class method
# Try/catch to remove unnecessary dependencies in unused method
import numpy as np, matplotlib.pyplot as plt
from pyleecan.Classes._swat_em import datamodel
from pyleecan.Functions.Winding.gen_phase_list import gen_name
from pyleecan.Functions.Winding.reverse_wind_mat import (
    reverse_wind_mat,
    reverse_layer,
    change_layer,
    permute_B_C,
)
from pyleecan.Functions.Winding.shift_wind_mat import shift_wind_mat
from matplotlib.patches import FancyArrowPatch, Patch, Rectangle
from pyleecan.definitions import config_dict
from pyleecan.Functions._swat_em.config import config
from pyleecan.Functions.Geometry.inter_line_line import inter_line_line
from pyleecan.Functions.init_fig import init_fig
from pyleecan.Functions._swat_em import plots


from pyleecan.Classes._check import InitUnKnowClassError


class Winding(FrozenClass):
    """Winding class generating connection matrix using Star of slots method (coupling with SWAT-EM)"""

    VERSION = 1
    NAME = "Star of slots"
    PHASE_COLORS = config_dict["PLOT"]["COLOR_DICT"]["PHASE_COLORS"]
    ROTOR_COLOR = config_dict["PLOT"]["COLOR_DICT"]["ROTOR_COLOR"]
    STATOR_COLOR = config_dict["PLOT"]["COLOR_DICT"]["STATOR_COLOR"]

    # cf Methods.Machine.Winding.clean
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

    # cf Methods.Machine.Winding.comp_connection_mat
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

    # cf Methods.Machine.Winding.comp_length_endwinding
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

    # cf Methods.Machine.Winding.comp_Ncps
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

    # cf Methods.Machine.Winding.comp_Ncspc
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

    # cf Methods.Machine.Winding.comp_Ntsp
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

    # cf Methods.Machine.Winding.comp_periodicity
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

    # cf Methods.Machine.Winding.comp_phasor_angle
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

    # cf Methods.Machine.Winding.comp_winding_factor
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

        xi = list()

        for harm in Harmonics:
            xi.append(
                np.abs(np.sum(np.exp(1j * slot_ang * harm) * wind_ph1)) / wind_ref
            )

        xi = np.array(xi)

        return xi

    # cf Methods.Machine.Winding.export_to_csv
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
        SEP=","
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

    # cf Methods.Machine.Winding.get_connection_mat
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

    # cf Methods.Machine.Winding.get_dim_wind
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

    # cf Methods.Machine.Winding.get_periodicity
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

    # cf Methods.Machine.Winding.plot_linear
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
        patches = list()
        lines_dict = dict()

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
            coils = list()  # list of points that constitutes the coils of a phase
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
                    idx_point_too_far != list()
                    and len(idx_point_too_far) != len(x_)
                    and idx_point_too_low == list()
                ):
                    wrong_points = x_[idx_point_too_far] + 1j * y_[idx_point_too_far]

                    # Correcting first point so that it is on the right border (new P2 point) and getting P3 as the conjugate of P2
                    # if there more than two points that are incorrect we have to remove them as we only need the first and the last one
                    idx_point_to_remove = (
                        idx_point_too_far[1:-1]
                        if len(idx_point_too_far) > 2
                        else list()
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
                    point_corrected = list()
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
                    if idx_point_to_remove != list():
                        point_list_updated = np.delete(
                            point_list_updated, idx_point_to_remove
                        )

                    coils.append(point_list_updated)
                    coils.append(point_to_add)
                elif len(idx_point_too_far) != len(x_) and idx_point_too_low == list():
                    coils.append(point_list_updated)

                # If we apply the reverse winding transformation then we must invert the the signe of the coil
                if self.is_reverse_wind:
                    direct *= -1

                # Step 2-2-4: Adding arrow patch for each coil between P2<->P3 and P5<->P0 (direction depending on winding direction)
                if len(idx_point_too_far) != len(x_) and idx_point_too_low == list():
                    if idx_point_too_far != list():
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

    # cf Methods.Machine.Winding.plot_radial
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
        self.parent = None
        self.is_reverse_wind = is_reverse_wind
        self.Nslot_shift_wind = Nslot_shift_wind
        self.qs = qs
        self.Ntcoil = Ntcoil
        self.Npcp = Npcp
        self.type_connection = type_connection
        self.p = p
        self.Lewout = Lewout
        self.conductor = conductor
        self.coil_pitch = coil_pitch
        self.wind_mat = wind_mat
        self.Nlayer = Nlayer
        self.per_a = per_a
        self.is_aper_a = is_aper_a
        self.end_winding = end_winding
        self.is_reverse_layer = is_reverse_layer
        self.is_change_layer = is_change_layer
        self.is_permute_B_C = is_permute_B_C
        self.dual_tri_phase_shift = dual_tri_phase_shift
        self.is_wye = is_wye

        # The class is frozen, for now it's impossible to add new properties
        self._freeze()

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        Winding_str = ""
        if self.parent is None:
            Winding_str += "parent = None " + linesep
        else:
            Winding_str += "parent = " + str(type(self.parent)) + " object" + linesep
        Winding_str += "is_reverse_wind = " + str(self.is_reverse_wind) + linesep
        Winding_str += "Nslot_shift_wind = " + str(self.Nslot_shift_wind) + linesep
        Winding_str += "qs = " + str(self.qs) + linesep
        Winding_str += "Ntcoil = " + str(self.Ntcoil) + linesep
        Winding_str += "Npcp = " + str(self.Npcp) + linesep
        Winding_str += "type_connection = " + str(self.type_connection) + linesep
        Winding_str += "p = " + str(self.p) + linesep
        Winding_str += "Lewout = " + str(self.Lewout) + linesep
        if self.conductor is not None:
            tmp = self.conductor.__str__().replace(linesep, linesep + "\t").rstrip("\t")
            Winding_str += "conductor = " + tmp
        else:
            Winding_str += "conductor = None" + linesep + linesep
        Winding_str += "coil_pitch = " + str(self.coil_pitch) + linesep
        Winding_str += (
            "wind_mat = "
            + linesep
            + str(self.wind_mat).replace(linesep, linesep + "\t")
            + linesep
            + linesep
        )
        Winding_str += "Nlayer = " + str(self.Nlayer) + linesep
        Winding_str += "per_a = " + str(self.per_a) + linesep
        Winding_str += "is_aper_a = " + str(self.is_aper_a) + linesep
        if self.end_winding is not None:
            tmp = (
                self.end_winding.__str__().replace(linesep, linesep + "\t").rstrip("\t")
            )
            Winding_str += "end_winding = " + tmp
        else:
            Winding_str += "end_winding = None" + linesep + linesep
        Winding_str += "is_reverse_layer = " + str(self.is_reverse_layer) + linesep
        Winding_str += "is_change_layer = " + str(self.is_change_layer) + linesep
        Winding_str += "is_permute_B_C = " + str(self.is_permute_B_C) + linesep
        Winding_str += (
            "dual_tri_phase_shift = " + str(self.dual_tri_phase_shift) + linesep
        )
        Winding_str += "is_wye = " + str(self.is_wye) + linesep
        return Winding_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False
        if other.is_reverse_wind != self.is_reverse_wind:
            return False
        if other.Nslot_shift_wind != self.Nslot_shift_wind:
            return False
        if other.qs != self.qs:
            return False
        if other.Ntcoil != self.Ntcoil:
            return False
        if other.Npcp != self.Npcp:
            return False
        if other.type_connection != self.type_connection:
            return False
        if other.p != self.p:
            return False
        if other.Lewout != self.Lewout:
            return False
        if other.conductor != self.conductor:
            return False
        if other.coil_pitch != self.coil_pitch:
            return False
        if not np.array_equal(other.wind_mat, self.wind_mat):
            return False
        if other.Nlayer != self.Nlayer:
            return False
        if other.per_a != self.per_a:
            return False
        if other.is_aper_a != self.is_aper_a:
            return False
        if other.end_winding != self.end_winding:
            return False
        if other.is_reverse_layer != self.is_reverse_layer:
            return False
        if other.is_change_layer != self.is_change_layer:
            return False
        if other.is_permute_B_C != self.is_permute_B_C:
            return False
        if other.dual_tri_phase_shift != self.dual_tri_phase_shift:
            return False
        if other.is_wye != self.is_wye:
            return False
        return True

    def compare(self, other, name="self", ignore_list=None, is_add_value=False):
        """Compare two objects and return list of differences"""

        if ignore_list is None:
            ignore_list = list()
        if type(other) != type(self):
            return ["type(" + name + ")"]
        diff_list = list()
        if other._is_reverse_wind != self._is_reverse_wind:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._is_reverse_wind)
                    + ", other="
                    + str(other._is_reverse_wind)
                    + ")"
                )
                diff_list.append(name + ".is_reverse_wind" + val_str)
            else:
                diff_list.append(name + ".is_reverse_wind")
        if other._Nslot_shift_wind != self._Nslot_shift_wind:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._Nslot_shift_wind)
                    + ", other="
                    + str(other._Nslot_shift_wind)
                    + ")"
                )
                diff_list.append(name + ".Nslot_shift_wind" + val_str)
            else:
                diff_list.append(name + ".Nslot_shift_wind")
        if other._qs != self._qs:
            if is_add_value:
                val_str = " (self=" + str(self._qs) + ", other=" + str(other._qs) + ")"
                diff_list.append(name + ".qs" + val_str)
            else:
                diff_list.append(name + ".qs")
        if other._Ntcoil != self._Ntcoil:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._Ntcoil)
                    + ", other="
                    + str(other._Ntcoil)
                    + ")"
                )
                diff_list.append(name + ".Ntcoil" + val_str)
            else:
                diff_list.append(name + ".Ntcoil")
        if other._Npcp != self._Npcp:
            if is_add_value:
                val_str = (
                    " (self=" + str(self._Npcp) + ", other=" + str(other._Npcp) + ")"
                )
                diff_list.append(name + ".Npcp" + val_str)
            else:
                diff_list.append(name + ".Npcp")
        if other._type_connection != self._type_connection:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._type_connection)
                    + ", other="
                    + str(other._type_connection)
                    + ")"
                )
                diff_list.append(name + ".type_connection" + val_str)
            else:
                diff_list.append(name + ".type_connection")
        if other._p != self._p:
            if is_add_value:
                val_str = " (self=" + str(self._p) + ", other=" + str(other._p) + ")"
                diff_list.append(name + ".p" + val_str)
            else:
                diff_list.append(name + ".p")
        if (
            other._Lewout is not None
            and self._Lewout is not None
            and np.isnan(other._Lewout)
            and np.isnan(self._Lewout)
        ):
            pass
        elif other._Lewout != self._Lewout:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._Lewout)
                    + ", other="
                    + str(other._Lewout)
                    + ")"
                )
                diff_list.append(name + ".Lewout" + val_str)
            else:
                diff_list.append(name + ".Lewout")
        if (other.conductor is None and self.conductor is not None) or (
            other.conductor is not None and self.conductor is None
        ):
            diff_list.append(name + ".conductor None mismatch")
        elif self.conductor is not None:
            diff_list.extend(
                self.conductor.compare(
                    other.conductor,
                    name=name + ".conductor",
                    ignore_list=ignore_list,
                    is_add_value=is_add_value,
                )
            )
        if other._coil_pitch != self._coil_pitch:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._coil_pitch)
                    + ", other="
                    + str(other._coil_pitch)
                    + ")"
                )
                diff_list.append(name + ".coil_pitch" + val_str)
            else:
                diff_list.append(name + ".coil_pitch")
        if not np.array_equal(other.wind_mat, self.wind_mat):
            diff_list.append(name + ".wind_mat")
        if other._Nlayer != self._Nlayer:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._Nlayer)
                    + ", other="
                    + str(other._Nlayer)
                    + ")"
                )
                diff_list.append(name + ".Nlayer" + val_str)
            else:
                diff_list.append(name + ".Nlayer")
        if other._per_a != self._per_a:
            if is_add_value:
                val_str = (
                    " (self=" + str(self._per_a) + ", other=" + str(other._per_a) + ")"
                )
                diff_list.append(name + ".per_a" + val_str)
            else:
                diff_list.append(name + ".per_a")
        if other._is_aper_a != self._is_aper_a:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._is_aper_a)
                    + ", other="
                    + str(other._is_aper_a)
                    + ")"
                )
                diff_list.append(name + ".is_aper_a" + val_str)
            else:
                diff_list.append(name + ".is_aper_a")
        if (other.end_winding is None and self.end_winding is not None) or (
            other.end_winding is not None and self.end_winding is None
        ):
            diff_list.append(name + ".end_winding None mismatch")
        elif self.end_winding is not None:
            diff_list.extend(
                self.end_winding.compare(
                    other.end_winding,
                    name=name + ".end_winding",
                    ignore_list=ignore_list,
                    is_add_value=is_add_value,
                )
            )
        if other._is_reverse_layer != self._is_reverse_layer:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._is_reverse_layer)
                    + ", other="
                    + str(other._is_reverse_layer)
                    + ")"
                )
                diff_list.append(name + ".is_reverse_layer" + val_str)
            else:
                diff_list.append(name + ".is_reverse_layer")
        if other._is_change_layer != self._is_change_layer:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._is_change_layer)
                    + ", other="
                    + str(other._is_change_layer)
                    + ")"
                )
                diff_list.append(name + ".is_change_layer" + val_str)
            else:
                diff_list.append(name + ".is_change_layer")
        if other._is_permute_B_C != self._is_permute_B_C:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._is_permute_B_C)
                    + ", other="
                    + str(other._is_permute_B_C)
                    + ")"
                )
                diff_list.append(name + ".is_permute_B_C" + val_str)
            else:
                diff_list.append(name + ".is_permute_B_C")
        if (
            other._dual_tri_phase_shift is not None
            and self._dual_tri_phase_shift is not None
            and np.isnan(other._dual_tri_phase_shift)
            and np.isnan(self._dual_tri_phase_shift)
        ):
            pass
        elif other._dual_tri_phase_shift != self._dual_tri_phase_shift:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._dual_tri_phase_shift)
                    + ", other="
                    + str(other._dual_tri_phase_shift)
                    + ")"
                )
                diff_list.append(name + ".dual_tri_phase_shift" + val_str)
            else:
                diff_list.append(name + ".dual_tri_phase_shift")
        if other._is_wye != self._is_wye:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._is_wye)
                    + ", other="
                    + str(other._is_wye)
                    + ")"
                )
                diff_list.append(name + ".is_wye" + val_str)
            else:
                diff_list.append(name + ".is_wye")
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object
        S += getsizeof(self.is_reverse_wind)
        S += getsizeof(self.Nslot_shift_wind)
        S += getsizeof(self.qs)
        S += getsizeof(self.Ntcoil)
        S += getsizeof(self.Npcp)
        S += getsizeof(self.type_connection)
        S += getsizeof(self.p)
        S += getsizeof(self.Lewout)
        S += getsizeof(self.conductor)
        S += getsizeof(self.coil_pitch)
        S += getsizeof(self.wind_mat)
        S += getsizeof(self.Nlayer)
        S += getsizeof(self.per_a)
        S += getsizeof(self.is_aper_a)
        S += getsizeof(self.end_winding)
        S += getsizeof(self.is_reverse_layer)
        S += getsizeof(self.is_change_layer)
        S += getsizeof(self.is_permute_B_C)
        S += getsizeof(self.dual_tri_phase_shift)
        S += getsizeof(self.is_wye)
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

        Winding_dict = dict()
        Winding_dict["is_reverse_wind"] = self.is_reverse_wind
        Winding_dict["Nslot_shift_wind"] = self.Nslot_shift_wind
        Winding_dict["qs"] = self.qs
        Winding_dict["Ntcoil"] = self.Ntcoil
        Winding_dict["Npcp"] = self.Npcp
        Winding_dict["type_connection"] = self.type_connection
        Winding_dict["p"] = self.p
        Winding_dict["Lewout"] = self.Lewout
        if self.conductor is None:
            Winding_dict["conductor"] = None
        else:
            Winding_dict["conductor"] = self.conductor.as_dict(
                type_handle_ndarray=type_handle_ndarray,
                keep_function=keep_function,
                **kwargs
            )
        Winding_dict["coil_pitch"] = self.coil_pitch
        if self.wind_mat is None:
            Winding_dict["wind_mat"] = None
        else:
            if type_handle_ndarray == 0:
                Winding_dict["wind_mat"] = self.wind_mat.tolist()
            elif type_handle_ndarray == 1:
                Winding_dict["wind_mat"] = self.wind_mat.copy()
            elif type_handle_ndarray == 2:
                Winding_dict["wind_mat"] = self.wind_mat
            else:
                raise Exception(
                    "Unknown type_handle_ndarray: " + str(type_handle_ndarray)
                )
        Winding_dict["Nlayer"] = self.Nlayer
        Winding_dict["per_a"] = self.per_a
        Winding_dict["is_aper_a"] = self.is_aper_a
        if self.end_winding is None:
            Winding_dict["end_winding"] = None
        else:
            Winding_dict["end_winding"] = self.end_winding.as_dict(
                type_handle_ndarray=type_handle_ndarray,
                keep_function=keep_function,
                **kwargs
            )
        Winding_dict["is_reverse_layer"] = self.is_reverse_layer
        Winding_dict["is_change_layer"] = self.is_change_layer
        Winding_dict["is_permute_B_C"] = self.is_permute_B_C
        Winding_dict["dual_tri_phase_shift"] = self.dual_tri_phase_shift
        Winding_dict["is_wye"] = self.is_wye
        # The class name is added to the dict for deserialisation purpose
        Winding_dict["__class__"] = "Winding"
        return Winding_dict

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

        self.is_reverse_wind = None
        self.Nslot_shift_wind = None
        self.qs = None
        self.Ntcoil = None
        self.Npcp = None
        self.type_connection = None
        self.p = None
        self.Lewout = None
        if self.conductor is not None:
            self.conductor._set_None()
        self.coil_pitch = None
        self.wind_mat = None
        self.Nlayer = None
        self.per_a = None
        self.is_aper_a = None
        if self.end_winding is not None:
            self.end_winding._set_None()
        self.is_reverse_layer = None
        self.is_change_layer = None
        self.is_permute_B_C = None
        self.dual_tri_phase_shift = None
        self.is_wye = None

    def _get_is_reverse_wind(self):
        """getter of is_reverse_wind"""
        return self._is_reverse_wind

    def _set_is_reverse_wind(self, value):
        """setter of is_reverse_wind"""
        check_var("is_reverse_wind", value, "bool")
        self._is_reverse_wind = value

    is_reverse_wind = property(
        fget=_get_is_reverse_wind,
        fset=_set_is_reverse_wind,
        doc="""1 to reverse the default winding algorithm along the airgap (c, b, a instead of a, b, c along the trigonometric direction)

        :Type: bool
        """,
    )

    def _get_Nslot_shift_wind(self):
        """getter of Nslot_shift_wind"""
        return self._Nslot_shift_wind

    def _set_Nslot_shift_wind(self, value):
        """setter of Nslot_shift_wind"""
        check_var("Nslot_shift_wind", value, "int")
        self._Nslot_shift_wind = value

    Nslot_shift_wind = property(
        fget=_get_Nslot_shift_wind,
        fset=_set_Nslot_shift_wind,
        doc="""Number of slots to shift the coils obtained with pyleecan winding algorithm (a, b, c becomes b, c, a with Nslot_shift_wind=1)

        :Type: int
        """,
    )

    def _get_qs(self):
        """getter of qs"""
        return self._qs

    def _set_qs(self, value):
        """setter of qs"""
        check_var("qs", value, "int", Vmin=0)
        self._qs = value

    qs = property(
        fget=_get_qs,
        fset=_set_qs,
        doc="""number of phases 

        :Type: int
        :min: 0
        """,
    )

    def _get_Ntcoil(self):
        """getter of Ntcoil"""
        return self._Ntcoil

    def _set_Ntcoil(self, value):
        """setter of Ntcoil"""
        check_var("Ntcoil", value, "int", Vmin=1)
        self._Ntcoil = value

    Ntcoil = property(
        fget=_get_Ntcoil,
        fset=_set_Ntcoil,
        doc="""number of turns per coil

        :Type: int
        :min: 1
        """,
    )

    def _get_Npcp(self):
        """getter of Npcp"""
        return self._Npcp

    def _set_Npcp(self, value):
        """setter of Npcp"""
        check_var("Npcp", value, "int", Vmin=1)
        self._Npcp = value

    Npcp = property(
        fget=_get_Npcp,
        fset=_set_Npcp,
        doc="""number of parallel circuits per phase

        :Type: int
        :min: 1
        """,
    )

    def _get_type_connection(self):
        """getter of type_connection"""
        return self._type_connection

    def _set_type_connection(self, value):
        """setter of type_connection"""
        check_var("type_connection", value, "int", Vmin=-1, Vmax=1)
        self._type_connection = value

    type_connection = property(
        fget=_get_type_connection,
        fset=_set_type_connection,
        doc="""Winding connection : 0 star (Y), 1 triangle (delta), -1 no connection

        :Type: int
        :min: -1
        :max: 1
        """,
    )

    def _get_p(self):
        """getter of p"""
        return self._p

    def _set_p(self, value):
        """setter of p"""
        check_var("p", value, "int", Vmin=1)
        self._p = value

    p = property(
        fget=_get_p,
        fset=_set_p,
        doc="""pole pairs number

        :Type: int
        :min: 1
        """,
    )

    def _get_Lewout(self):
        """getter of Lewout"""
        return self._Lewout

    def _set_Lewout(self, value):
        """setter of Lewout"""
        check_var("Lewout", value, "float", Vmin=0)
        self._Lewout = value

    Lewout = property(
        fget=_get_Lewout,
        fset=_set_Lewout,
        doc="""straight length of the conductors outside the lamination before the curved part of winding overhang [m] - can be negative to tune the average turn length (only used in voltage driven simulations)

        :Type: float
        :min: 0
        """,
    )

    def _get_conductor(self):
        """getter of conductor"""
        return self._conductor

    def _set_conductor(self, value):
        """setter of conductor"""
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
                "pyleecan.Classes", value.get("__class__"), "conductor"
            )
            value = class_obj(init_dict=value)
        elif type(value) is int and value == -1:  # Default constructor
            Conductor = import_class("pyleecan.Classes", "Conductor", "conductor")
            value = Conductor()
        check_var("conductor", value, "Conductor")
        self._conductor = value

        if self._conductor is not None:
            self._conductor.parent = self

    conductor = property(
        fget=_get_conductor,
        fset=_set_conductor,
        doc="""Winding's conductor

        :Type: Conductor
        """,
    )

    def _get_coil_pitch(self):
        """getter of coil_pitch"""
        return self._coil_pitch

    def _set_coil_pitch(self, value):
        """setter of coil_pitch"""
        check_var("coil_pitch", value, "int")
        self._coil_pitch = value

    coil_pitch = property(
        fget=_get_coil_pitch,
        fset=_set_coil_pitch,
        doc="""Distance (in slot) between a conductor of a certain phase and the corresponding return conductor

        :Type: int
        """,
    )

    def _get_wind_mat(self):
        """getter of wind_mat"""
        return self._wind_mat

    def _set_wind_mat(self, value):
        """setter of wind_mat"""
        if type(value) is int and value == -1:
            value = np.array([])
        elif type(value) is list:
            try:
                value = np.array(value)
            except:
                pass
        check_var("wind_mat", value, "ndarray")
        self._wind_mat = value

    wind_mat = property(
        fget=_get_wind_mat,
        fset=_set_wind_mat,
        doc="""Winding matrix calculated with Star of slots (from SWAT_EM package)

        :Type: ndarray
        """,
    )

    def _get_Nlayer(self):
        """getter of Nlayer"""
        return self._Nlayer

    def _set_Nlayer(self, value):
        """setter of Nlayer"""
        check_var("Nlayer", value, "int", Vmin=1)
        self._Nlayer = value

    Nlayer = property(
        fget=_get_Nlayer,
        fset=_set_Nlayer,
        doc="""Number of different coils in a slot

        :Type: int
        :min: 1
        """,
    )

    def _get_per_a(self):
        """getter of per_a"""
        return self._per_a

    def _set_per_a(self, value):
        """setter of per_a"""
        check_var("per_a", value, "int", Vmin=1)
        self._per_a = value

    per_a = property(
        fget=_get_per_a,
        fset=_set_per_a,
        doc="""Number of spatial periods of the winding

        :Type: int
        :min: 1
        """,
    )

    def _get_is_aper_a(self):
        """getter of is_aper_a"""
        return self._is_aper_a

    def _set_is_aper_a(self, value):
        """setter of is_aper_a"""
        check_var("is_aper_a", value, "bool")
        self._is_aper_a = value

    is_aper_a = property(
        fget=_get_is_aper_a,
        fset=_set_is_aper_a,
        doc="""True if the winding is anti-periodic over space

        :Type: bool
        """,
    )

    def _get_end_winding(self):
        """getter of end_winding"""
        return self._end_winding

    def _set_end_winding(self, value):
        """setter of end_winding"""
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
                "pyleecan.Classes", value.get("__class__"), "end_winding"
            )
            value = class_obj(init_dict=value)
        elif type(value) is int and value == -1:  # Default constructor
            EndWinding = import_class("pyleecan.Classes", "EndWinding", "end_winding")
            value = EndWinding()
        check_var("end_winding", value, "EndWinding")
        self._end_winding = value

        if self._end_winding is not None:
            self._end_winding.parent = self

    end_winding = property(
        fget=_get_end_winding,
        fset=_set_end_winding,
        doc="""End Winding's definition

        :Type: EndWinding
        """,
    )

    def _get_is_reverse_layer(self):
        """getter of is_reverse_layer"""
        return self._is_reverse_layer

    def _set_is_reverse_layer(self, value):
        """setter of is_reverse_layer"""
        check_var("is_reverse_layer", value, "bool")
        self._is_reverse_layer = value

    is_reverse_layer = property(
        fget=_get_is_reverse_layer,
        fset=_set_is_reverse_layer,
        doc="""1 to reverse the layers (rad from 0 to Nrad-1 => Nrad-1 to 0)

        :Type: bool
        """,
    )

    def _get_is_change_layer(self):
        """getter of is_change_layer"""
        return self._is_change_layer

    def _set_is_change_layer(self, value):
        """setter of is_change_layer"""
        check_var("is_change_layer", value, "bool")
        self._is_change_layer = value

    is_change_layer = property(
        fget=_get_is_change_layer,
        fset=_set_is_change_layer,
        doc="""1 to change the layer from radial to tangential or tangential to radial

        :Type: bool
        """,
    )

    def _get_is_permute_B_C(self):
        """getter of is_permute_B_C"""
        return self._is_permute_B_C

    def _set_is_permute_B_C(self, value):
        """setter of is_permute_B_C"""
        check_var("is_permute_B_C", value, "bool")
        self._is_permute_B_C = value

    is_permute_B_C = property(
        fget=_get_is_permute_B_C,
        fset=_set_is_permute_B_C,
        doc="""True to permute phase B and phase C

        :Type: bool
        """,
    )

    def _get_dual_tri_phase_shift(self):
        """getter of dual_tri_phase_shift"""
        return self._dual_tri_phase_shift

    def _set_dual_tri_phase_shift(self, value):
        """setter of dual_tri_phase_shift"""
        check_var("dual_tri_phase_shift", value, "float")
        self._dual_tri_phase_shift = value

    dual_tri_phase_shift = property(
        fget=_get_dual_tri_phase_shift,
        fset=_set_dual_tri_phase_shift,
        doc="""Phase shift between both tri-phase systems in dual-tri-phase case

        :Type: float
        """,
    )

    def _get_is_wye(self):
        """getter of is_wye"""
        return self._is_wye

    def _set_is_wye(self, value):
        """setter of is_wye"""
        check_var("is_wye", value, "bool")
        self._is_wye = value

    is_wye = property(
        fget=_get_is_wye,
        fset=_set_is_wye,
        doc="""True if the alimentation is wye (else delta)

        :Type: bool
        """,
    )

    class WindingError(Exception):
        """ """

        pass


WindingError = Winding.WindingError
