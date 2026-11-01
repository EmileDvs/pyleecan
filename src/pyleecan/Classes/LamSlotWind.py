# File generated according to Generator/ClassesRef/Machine/LamSlotWind.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Machine/LamSlotWind"""

from os import linesep
from sys import getsizeof

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, Patch
from matplotlib.pyplot import plot, subplots
from pyleecan.Classes.Lamination import Lamination
from pyleecan.Classes.OPdq import OPdq
from pyleecan.Classes.SlotW22 import SlotW22
from pyleecan.Classes.WindingSC import WindingSC
from pyleecan.Classes.WindingUD import WindingUD

from pyleecan.Classes._check import check_var
from pyleecan.Classes._swat_em import datamodel
from pyleecan.Classes.Data1D import Data1D
from pyleecan.Classes.DataFreq import DataFreq
from pyleecan.Classes.DataTime import DataTime
from pyleecan.Classes.Input import CURRENT_DIR_REF, PHASE_DIR_REF, ROT_DIR_REF
from pyleecan.Classes.LamSlot import LamSlot
from pyleecan.definitions import config_dict
from pyleecan.Functions.Electrical.dqh_transformation import dqh2n
from pyleecan.Functions.get_logger import get_logger
from pyleecan.Functions.init_fig import init_fig
from pyleecan.Functions.labels import (
    BAR_LAB,
    BOUNDARY_PROP_LAB,
    COND_BOUNDARY_PROP_LAB,
    WIND_LAB,
    YSML_LAB,
    YSMR_LAB,
    decode_label,
    update_RTS_index,
)
from pyleecan.Functions.load import load_init_dict
from pyleecan.Functions.Load.import_class import import_class
from pyleecan.Functions.Plot import dict_2D
from pyleecan.Functions.Plot.get_color_legend_from_surface import (
    get_color_legend_from_surface,
)
from pyleecan.Functions.Plot.set_plot_gui_icon import set_plot_gui_icon
from pyleecan.Functions.save import save
from pyleecan.Functions.Winding.comp_cond_function import comp_cond_function
from pyleecan.Functions.Winding.find_wind_phase_color import find_wind_phase_color
from pyleecan.Functions.Winding.gen_phase_list import gen_color, gen_name


class LamSlotWind(LamSlot):
    """Lamination with Slot filled with winding"""

    VERSION = 1
    PHASE_COLORS = config_dict["PLOT"]["COLOR_DICT"]["PHASE_COLORS"]

    # cf Methods.Machine.LamSlotWind.build_geometry
    def build_geometry(self, sym=1, alpha=0, delta=0, is_circular_radius=False):
        """Build the geometry of the Lamination with winding in slots

        Parameters
        ----------
        self : LamSlotWind
            A LamSlotWind object
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
        # getting the Lamination surface
        surf_lam = LamSlot.build_geometry(
            self,
            sym=sym,
            alpha=alpha,
            delta=delta,
            is_circular_radius=is_circular_radius,
        )
        surf_list = list()
        if self.slot is not None and self.slot.Zs != 0:
            # getting number of slot
            Zs = self.slot.Zs
            # getting angle between Slot
            slot_pitch = 2 * np.pi / Zs
            # getting Nrad and Ntan
            if self.winding is None or self.winding.conductor is None:
                Nrad, Ntan = 1, 1
                surf_Wind = list()
            else:
                try:
                    Nrad, Ntan = self.winding.get_dim_wind()
                except Exception:
                    Nrad, Ntan = 1, 1

                surf_Wind = self.slot.build_geometry_active(
                    Nrad=Nrad,
                    Ntan=Ntan,
                    alpha=alpha,
                    delta=delta,
                )

            st = self.get_label()
            assert (self.slot.Zs % sym) == 0, (
                "ERROR, Wrong symmetry for "
                + st
                + " "
                + str(self.slot.Zs)
                + " slots and sym="
                + str(sym)
            )
            for ii in range(Zs // sym):  # for each slot
                # for each part of the winding surface in the slot
                for surf in surf_Wind:
                    new_surf = surf.copy()
                    # changing the slot reference number
                    new_surf.label = update_RTS_index(
                        label=surf.label, S_id=ii, surf_type_label=WIND_LAB
                    )
                    new_surf.rotate(ii * slot_pitch)
                    surf_list.append(new_surf)
            # Update the winding BC (if winding side matches sym lines ex: SlotM18)
            if self.slot.is_full_pitch_active() and sym > 1:
                for surf in surf_list:
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
            # Add wedges if any
            if self.slot.wedge_mat is not None:
                wedge_list = self.slot.get_surface_wedges()
                for ii in range(Zs // sym):  # for each slot
                    # for each wedges surface in the slot
                    for surf in wedge_list:
                        new_surf = type(surf)(init_dict=surf.as_dict())
                        # changing the slot reference number
                        new_surf.label = update_RTS_index(label=surf.label, S_id=ii)
                        new_surf.rotate(ii * slot_pitch)
                        surf_list.append(new_surf)
            # Shift to have a tooth center on Ox
            for surf in surf_list:
                surf.rotate(np.pi / Zs)

        surf_list = surf_lam + surf_list

        return surf_list

    # cf Methods.Machine.LamSlotWind.check
    def check(self):
        """Check that the Lamination object is correct

        Parameters
        ----------
        self :
            A LamSlotWind object

        Returns
        -------
        None

        Raises
        _______
        LWC_SlotTooLong
            The Slot is too long for the lamination (HYoke <0)
        LWC_MismatchPhase
            The Winding and the Converter don't have the same number of phase
        LWC_OverlappingSlot
            The Lamination has overlapping slot
        """

        Lamination.check(self)

        self.winding.conductor.check()
        self.slot.check()

        if self.comp_height_yoke() < 0:
            raise LWC_SlotTooLong(
                "The Slot is too long for the lamination " "(HYoke <0)"
            )

        """
        Wt = self.slot.comp_tooth_widths()["WTooth_min"]

        if Wt < 0:
            raise LWC_OverlappingSlot("The Lamination has overlapping slot")
        """

    # cf Methods.Machine.LamSlotWind.comp_angle_d_axis
    def comp_angle_d_axis(self, is_plot=False):
        """Compute the angle between the X axis and the first d+ axis
        By convention a "Tooth" is centered on the X axis
        Parameters
        ----------
        self : LamSlotWind
            A LamSlotWind object
        is_plot : bool
            True to plot d axis position regarding unit mmf
        Returns
        -------
        d_angle : float
            angle between the X axis and the first d+ axis
        """

        if (
            self.winding is None
            or self.winding.qs == 0
            or self.winding.conductor is None
        ):
            return 0

        p = self.get_pole_pair_number()

        MMF, _ = self.comp_mmf_unit(Nt=100, Na=400 * p)

        # Get angle values
        results1 = MMF.get_along("angle[oneperiod]")
        angle_stator = results1["angle"]

        # Get the unit mmf FFT and wavenumbers
        results = MMF.get_along("wavenumber")
        wavenumber = results["wavenumber"]
        mmf_ft = results[MMF.symbol]

        # Find the fundamental harmonic of MMF
        indr_fund = np.abs(wavenumber - p).argmin()
        phimax = np.angle(mmf_ft[indr_fund])

        # Get the angle for which mmf is max
        # MMF_max = A*cos(p*d_angle + phimax) which is maximum for p*d_angle + phimax = 2*pi
        d_angle = ((2 * np.pi - phimax) / p) % (2 * np.pi / p)

        if is_plot:

            # Reconstruct fundamental MMF wave
            magmax = np.abs(mmf_ft[indr_fund])
            mmf_waveform = magmax * np.cos(p * angle_stator + phimax)

            # Get the first angle where mmf is max
            I_max = np.argmax(mmf_waveform)
            d_angle0 = angle_stator[I_max]  # d_angle0->d_angle when Na->inf

            fig, ax = plt.subplots()
            ax.plot(
                angle_stator,
                np.squeeze(MMF.get_along("angle[oneperiod]")[MMF.symbol]),
                "k",
            )
            ax.plot(angle_stator, mmf_waveform, "r")
            ax.plot([d_angle, d_angle], [-magmax, magmax], "--k")
            ax.plot([d_angle0, d_angle0], [-magmax, magmax], "--b")
            plt.show()

        return d_angle

    # cf Methods.Machine.LamSlotWind.comp_fill_factor
    def comp_fill_factor(self):
        """Compute the fill factor of the winding

        Parameters
        ----------
        self : LamSlotWind
            a LamSlotWind object

        Returns
        -------
        Kfill : float
            fill factor of the winding
        """

        if (
            self.winding is None
            or self.winding.qs == 0
            or self.winding.conductor is None
        ):
            return 0
        else:
            # compute the number of conductors per slot
            Ncps = self.winding.comp_Ncps()

            # compute the winding surfaces
            S_slot_wind = self.slot.comp_surface_active()
            S_wind_act = self.winding.conductor.comp_surface_active() * Ncps

            return S_wind_act / S_slot_wind

    # cf Methods.Machine.LamSlotWind.comp_lengths_winding
    def comp_lengths_winding(self):
        """Compute the lengths of the Lamination's Winding.
        - Lwtot : total length of lamination winding incl. end-windings and
        radial ventilation ducts [m].
        - Lwact : active length of lamination winding excl. end-windings and
        radial ventilation ducts [m].
        - Lewt : total end-winding length [m].
        - Lew : end-winding length on one side for a half-turn
        - Lwvent : length of lamination winding in the radial ventilation ducts [m]
        Parameters
        ----------
        self: LamSlotWind
            a LamSlotWind object
        Returns
        -------
        L_dict: dict
            Dictionary of the length (Lwtot, Lwact, Lew, Lwvent)
        """

        # length of the stack including ventilation ducts
        L1vd = self.comp_length()

        # end-winding length on one side for a half-turn
        Lew = self.winding.comp_length_endwinding()

        # total end-winding length
        Ntspc = self.winding.comp_Ntsp(self.get_Zs())
        qb = self.comp_number_phase_eq()
        Lewt = qb * Ntspc * self.winding.Npcp * 4 * Lew

        # average length of a lamination winding half-turn (one "go" conductor
        # without "return" conductor)
        Lwht = L1vd + 2 * Lew

        # total length of lamination winding incl. end windings [m]
        Lwtot = qb * Ntspc * self.winding.Npcp * 2 * Lwht

        # Active length of lamination winding excl. end windings and radial
        # ventilation duct [m]
        Lwact = qb * Ntspc * self.winding.Npcp * 2 * self.L1

        # length of lamination winding in the radial ventilation duct [m]
        if self.Nrvd is None or self.Wrvd is None:
            Lwvent = 0
        else:
            Lwvent = qb * Ntspc * self.winding.Npcp * 2 * self.Nrvd * self.Wrvd

        return {
            "Lwtot": Lwtot,
            "Lwht": Lwht,
            "Lwact": Lwact,
            "Lewt": Lewt,
            "Lwvent": Lwvent,
            "Lew": Lew,
            "MLT": Lwht * 2,
        }

    # cf Methods.Machine.LamSlotWind.comp_masses
    def comp_masses(self):
        """Compute the Lamination masses

        Parameters
        ----------
        self : LamSlotWind
            A LamSlotWind object

        Returns
        -------
        M_dict: dict
            Lamination mass dictionary (Mtot, Mlam, Mwind) [kg]
        """

        M_dict = LamSlot.comp_masses(self)

        if self.winding is not None:
            # Check
            if self.winding.conductor.cond_mat.struct.rho is None:
                if self.is_stator:
                    lam_name = "Stator"
                else:
                    lam_name = "Rotor"
                mat_name = str(self.winding.conductor.cond_mat.name)
                raise Exception(
                    "Error: The "
                    + lam_name
                    + " winding conductor material ("
                    + mat_name
                    + ") is not fully defined. Please set struct.rho"
                )
            # Compute
            L_dict = self.comp_lengths_winding()
            Mwind = (
                self.winding.conductor.comp_surface_active()
                * self.winding.conductor.cond_mat.struct.rho
                * L_dict["Lwtot"]
            )
        else:
            Mwind = 0
        if self.slot is None or self.slot.wedge_mat is None:
            M_dict["Mwedge"] = 0
        else:
            Lf = self.comp_length()  # Include radial ventilation ducts
            M_dict["Mwedge"] = (
                self.slot.wedge_mat.struct.rho
                * Lf
                * self.get_Zs()
                * self.slot.comp_surface_wedges()
            )

        M_dict["Mtot"] += Mwind + M_dict["Mwedge"]
        M_dict["Mwind"] = Mwind

        return M_dict

    # cf Methods.Machine.LamSlotWind.comp_mmf_dir
    def comp_mmf_dir(self, current_dir=None, phase_dir=None, is_plot=False):
        """Compute the rotation direction of the fundamental magnetomotive force induced by the winding

        Parameters
        ----------
        self : LamSlotWind
            A LamSlotWind object
        current_dir: int
            Stator current rotation direction +/-1
        phase_dir: int
            Stator winding phasor rotation direction +/-1
        is_plot: bool
            True to plot fft2 of stator MMF

        Returns
        -------
        mmf_dir : int
            -1 or +1
        """
        p = self.get_pole_pair_number()

        # Compute unit mmf
        # 20 points per pole over time and space is enough to capture rotating direction of fundamental mmf
        MMF, _ = self.comp_mmf_unit(
            Nt=20 * p, Na=20 * p, current_dir=current_dir, phase_dir=phase_dir
        )

        # Extract fundamental from unit mmf
        result_p = MMF.get_harmonics(1, "freqs>0", "wavenumber=" + str(p))
        result_n = MMF.get_harmonics(1, "freqs>0", "wavenumber=" + str(-p))

        if result_p[MMF.symbol][0] > result_n[MMF.symbol][0]:
            result = result_p
        else:
            result = result_n

        # Get frequency and wavenumber of fundamental
        f = result["freqs"][0]
        r = result["wavenumber"][0]

        # Rotating direction is the sign of the mechanical speed of the magnetomotive force fundamental,
        # i.e frequency over wavenumber
        mmf_dir = int(np.sign(f / r))

        if is_plot:
            MMF.plot_3D_Data("freqs", "wavenumber")

        return mmf_dir

    # cf Methods.Machine.LamSlotWind.comp_mmf_unit
    def comp_mmf_unit(
        self, Na=None, Nt=None, felec=1, current_dir=None, phase_dir=None
    ):
        """Compute the winding unit magnetomotive force for given inputs

        Parameters
        ----------
        self : LamSlotWind
            an LamSlotWind object
        Na : int
            Space discretization for offline computation
        Nt : int
            Time discretization for offline computation
        felec : float
            Stator current frequency to consider
        current_dir: int
            Stator current rotation direction +/-1
        phase_dir: int
            Stator winding phasor rotation direction +/-1

        Returns
        -------
        MMF_U : DataTime
            Unit magnetomotive force (Na,Nt)
        WF : DataTime
            Winding functions (qs,Na)

        """

        # Check that parent machine is not None
        if self.parent is None:
            raise Exception("Cannot calculate mmf unit if parent machine is None")
        else:
            machine = self.parent

        # Compute the winding function and mmf
        if self.winding is None:
            raise Exception("Cannot calculate mmf unit if winding is None")
        else:
            # Get stator winding number of phases
            qs = self.winding.qs

        if current_dir is None:
            current_dir = CURRENT_DIR_REF
        elif current_dir not in [-1, 1]:
            raise Exception("Cannot enforce current_dir other than +1 or -1")

        if phase_dir is None:
            phase_dir = PHASE_DIR_REF
        elif phase_dir not in [-1, 1]:
            raise Exception("Cannot enforce phase_dir other than +1 or -1")

        InputVoltage = import_class("pyleecan.Classes", "InputVoltage")
        input = InputVoltage(
            Na_tot=Na,
            Nt_tot=Nt,
            OP=OPdq(felec=felec),
            current_dir=current_dir,
            rot_dir=ROT_DIR_REF,  # rotor rotating dir has not impact on unit mmf
        )

        axes_dict = input.comp_axes(
            axes_list=["time", "angle", "phase_S", "phase_R"],
            machine=machine,
            is_periodicity_t=False,
            is_periodicity_a=False,
            is_antiper_t=False,
            is_antiper_a=False,
        )

        # Compute winding function
        angle = axes_dict["angle"].get_values(is_oneperiod=True)
        per_a, _ = axes_dict["angle"].get_periodicity()
        wf = self.comp_wind_function(angle=angle, per_a=per_a)

        # Compute unit current function of time applying constant Id=1 Arms, Iq=Ih=0
        angle_elec = axes_dict["time"].get_values(
            is_oneperiod=True, normalization="angle_elec"
        )

        if qs == 6 and self.winding.dual_tri_phase_shift is not None:
            Is_val = np.zeros((1, 6), dtype=complex)
            Id = 1
            Iq = 0
            I0 = np.sqrt(Id**2 + Iq**2) * np.sqrt(2)
            phi0 = 0
            if not self.winding.is_wye:
                I0 = I0 / np.sqrt(3)
                phi0 = phi0 + np.pi / 6
            Is_val[0, 0] = I0 * np.exp(1j * phi0)
            Is_val[0, 1] = I0 * np.exp(1j * (phi0 + self.winding.dual_tri_phase_shift))
            Is_val[0, 2] = I0 * np.exp(1j * (phi0 + 2 * np.pi / 3))
            Is_val[0, 3] = I0 * np.exp(
                1j * (phi0 + 2 * np.pi / 3 + self.winding.dual_tri_phase_shift)
            )
            Is_val[0, 4] = I0 * np.exp(1j * (phi0 + 4 * np.pi / 3))
            Is_val[0, 5] = I0 * np.exp(
                1j * (phi0 + 4 * np.pi / 3 + self.winding.dual_tri_phase_shift)
            )
            # Create Data object
            Phases = Data1D(
                name="phase",
                unit="",
                values=["A1", "A2", "B1", "B2", "C1", "C2"],
                is_components=True,
            )
            Freqs = Data1D(
                values=[felec],
                unit="Hz",
                name="freqs",
                normalizations=axes_dict["time"].normalizations.copy(),
            )
            Is = DataFreq(
                name="Stator current",
                unit="A",
                symbol="I_s",
                axes=[Freqs, Phases],
                values=Is_val,
            )
            I = Is.get_along(
                "time=axis_data",
                "phase",
                axis_data={"time": axes_dict["time"].get_values(is_oneperiod=True)},
            )["I_s"]
        else:
            Idq = np.zeros((angle_elec.size, 3))
            Idq[:, 0] = np.ones(angle_elec.size)
            I = dqh2n(Idq, angle_elec, n=qs, is_n_rms=False, phase_dir=phase_dir)

        # Compute unit mmf
        mmf_u = np.squeeze(np.dot(I, wf))

        # Create a Data object

        MMF_U = DataTime(
            name="Overall MMF",
            unit="A",
            symbol="MMF",
            axes=[axes_dict["time"], axes_dict["angle"]],
            values=mmf_u,
        )

        WF = DataTime(
            name="Phase MMF",
            unit="A",
            symbol="MMF",
            axes=[axes_dict["angle"], axes_dict["phase_" + self.get_label()]],
            values=wf.T,
        )

        return MMF_U, WF

    # cf Methods.Machine.LamSlotWind.comp_number_phase_eq
    def comp_number_phase_eq(self):
        """Compute the equivalent number of phase

        Parameters
        ----------
        self : LamSlotWind
            A LamSlotWind object

        Returns
        -------
        qb: float
            Number of winding phase
        """

        return float(self.winding.qs)

    # cf Methods.Machine.LamSlotWind.comp_output_geo
    def comp_output_geo(self):
        """Compute the main geometry output

        Parameters
        ----------
        self : Lamination
            A Lamination object

        Returns
        -------
        output: OutGeoLam
            Main geometry output of the lamintion

        """

        output = Lamination.comp_output_geo(self)
        output.Ksfill = self.comp_fill_factor()
        if self.slot is None:
            output.S_slot = 0
            output.S_slot_wind = 0
        else:
            output.S_slot = self.slot.comp_surface()
            output.S_slot_wind = self.slot.comp_surface_active()
        # output.S_wind_act = self.winding.conductor.comp_surface_active()

        return output

    # cf Methods.Machine.LamSlotWind.comp_periodicity_spatial
    def comp_periodicity_spatial(self):
        """Compute the periodicity factor of the lamination

        Parameters
        ----------
        self : LamSlotWind
            A LamSlotWind object

        Returns
        -------
        per_a : int
            Number of spatial periodicities of the lamination over 2*pi
        is_antiper_a : bool
            True if an spatial anti-periodicity is possible after the periodicities
        """
        # get Lamination periodicity
        per_a, is_antiper_a = super(type(self), self).comp_periodicity_spatial()

        # Angular periodicity
        if self.winding is not None and self.winding.conductor is not None:
            per_a_w, is_antiper_a_w = self.winding.get_periodicity()
            per_a = int(np.gcd(per_a, per_a_w))
            is_antiper_a = is_antiper_a and is_antiper_a_w

        per_a, is_antiper_a = self.comp_periodicity_duct_spatial(per_a, is_antiper_a)

        return int(per_a), bool(is_antiper_a)

    # cf Methods.Machine.LamSlotWind.comp_resistance_wind
    def comp_resistance_wind(self, T=20):
        """Compute the DC winding resistance per phase without skin effect at average temperature T degC

        Parameters
        ----------
        self : LamSlotWind
            a LamSlotWind object
        T : float
            mean winding temperature [°C], default value is 20°C

        Returns
        -------
        R : float
            DC winding resistance per phase without skin effect [Ohm]
        """

        Zs = self.slot.Zs
        Ntspc = self.winding.comp_Ntsp(Zs)
        # length of the stack including ventilation ducts
        L1vd = self.comp_length()

        # end-winding length on one side for a half-turn
        # TODO implement endwinding length (return Enforced endwinding length)
        Lew = self.winding.comp_length_endwinding()

        # average length of a lamination winding half-turn (one "go" conductor
        # without "return" conductor)
        Lwht = L1vd + 2 * Lew

        # Active surface of conductor
        Sact = self.winding.conductor.comp_surface_active()

        # temperature coefficient and electrical conductivity
        rhow = self.winding.conductor.cond_mat.elec.get_resistivity(T_op=T, T_ref=20)

        # DC winding resistance per phase at specified temperature
        R = (1.0 / self.winding.Npcp) * rhow * (Ntspc * 2 * Lwht) / (Sact)

        return R

    # cf Methods.Machine.LamSlotWind.comp_surfaces
    def comp_surfaces(self):
        """Compute the Lamination surfaces (Slam, Svent, Sslot, Swind)

        Parameters
        ----------
        self : LamSlotWind
            A LamSlotWind object

        Returns
        -------
        S_dict: dict
            Lamination surface dictionary (Slam, Svent, Sslot, Swind) [m**2]

        """

        S_dict = LamSlot.comp_surfaces(self)

        if self.slot is not None:
            S_dict["Swind"] = self.get_Zs() * self.slot.comp_surface_active()
            S_dict["Swedge"] = self.get_Zs() * self.slot.comp_surface_wedges()
        else:
            S_dict["Swind"] = 0
            S_dict["Swedge"] = 0

        return S_dict

    # cf Methods.Machine.LamSlotWind.comp_volumes
    def comp_volumes(self):
        """Compute the Lamination volumes (Vlam, Vvent, Vslot, Vwind)

        Parameters
        ----------
        self : LamSlotWind
            A LamSlotWind object

        Returns
        -------
        V_dict: dict
            Lamination volume dictionary (Vlam, Vvent, Vslot, Vwind) [m**3]

        """

        V_dict = LamSlot.comp_volumes(self)
        Lf = self.comp_length()  # Include radial ventilation ducts
        if self.slot is None:
            V_dict["Vwind"] = 0
            V_dict["Vwedge"] = 0
        else:
            V_dict["Vwind"] = Lf * self.get_Zs() * self.slot.comp_surface_active()
            V_dict["Vwedge"] = Lf * self.get_Zs() * self.slot.comp_surface_wedges()
        return V_dict

    # cf Methods.Machine.LamSlotWind.comp_wind_function
    def comp_wind_function(self, angle=None, Na=2048, alpha_mmf0=0, per_a=1):
        """Computation of the winding function for the lamination.
        By convention a tooth is centered on the X axis

        Parameters
        ----------
        self : LamSlotWind
            A LamSlotWind object
        angle : ndarray
            Space discretization to compute the winding functions
        Na : int
            Number of angular points for the winding function (not used if angle is set)
        alpha_mmf0 : float
            Angle to shift the winding function (Default value = 0)
        per_a : int
            Spatial periodicity factor

        Returns
        -------
        wf: ndarray
            Winding function Matrix (qs,Na)
        """

        # Space discretization
        if angle is None:
            angle = np.linspace(0, np.pi * 2 / per_a, Na, endpoint=False)
        else:
            Na = angle.size

        qs = self.winding.qs  # number of phases
        # Number of point on rad and tan direction
        Nrad, Ntan = self.winding.get_dim_wind()
        Zs = self.slot.Zs  # Number of slot
        Zs0 = int(Zs / per_a)

        slot_angle = self.slot.comp_angle_active_eq()
        slot_opening = self.slot.comp_angle_opening()

        wind_mat = self.winding.get_connection_mat(Zs)
        # sum wind_mat along Nlay_rad axis
        wind_mat = np.sum(wind_mat, axis=0)

        # angle of the center of the slots
        # By convention a tooth is centered on the X axis
        alpha_slot = np.linspace(0, 2 * np.pi / per_a, Zs0, endpoint=False) + np.pi / Zs

        # angle of the lay in a slot (Nlay point, end and begin excluded)
        alpha_lay = np.linspace(
            -slot_angle / 2, slot_angle / 2, Ntan + 1, endpoint=False
        )[1:]

        if alpha_mmf0 != 0:
            angle = (angle - alpha_mmf0) % (2 * np.pi)

        wf = np.zeros((qs, Na))
        for n in range(Ntan):
            # [Na, Zs]
            Xalpha_slot, Xangle = np.meshgrid(alpha_slot + alpha_lay[n], angle)

            Xwind = np.zeros((1, Zs0, qs))
            Xwind[0, :, :] = wind_mat[n, 0:Zs0, :]
            # Extended winding matrix [Na, Zs, qs]
            Xwind = np.repeat(Xwind, Na, axis=0)
            # Single winding function in every slot and angle for nth layer [Na, Zs]
            Xwf = -0.5 * comp_cond_function(Xalpha_slot, slot_opening, Xangle)

            for q in range(qs):
                # winding function of qth phase (sum over layers) [qs, Na]
                wf[q, :] += np.sum(Xwind[:, :, q] * Xwf, axis=1)

        if per_a > 1:
            wf = wf - np.mean(wf, axis=1)[:, None]

        return wf

    # cf Methods.Machine.LamSlotWind.get_polar_eq
    def get_polar_eq(self):
        """Returns a polar equivalent of the lamination

        Parameters
        ----------
        self : LamSlotWind
            A LamSlotWind object to convert to polar

        Returns
        -------
        polar_eq: LamSlotWind
            The polar equivalent of the lamination
        """

        # Copy the lamination
        polar_eq = type(self)(init_dict=self.as_dict())

        # Compute the polar dimension of the slot
        Hwind = self.slot.comp_height_active()
        Histhmus = self.slot.comp_height() - Hwind
        Wwind = self.slot.comp_angle_active_eq()
        Wisthmus = self.slot.comp_angle_opening()

        polar_eq.slot = SlotW22(
            Zs=self.slot.Zs, H0=Histhmus, W0=Wisthmus, H2=Hwind, W2=Wwind
        )

        # TODO: Polar eq for ventilations ?
        polar_eq.axial_vent = list()

        return polar_eq

    # cf Methods.Machine.LamSlotWind.get_pole_pair_number
    def get_pole_pair_number(self):
        """Return the number of pair of pole of the Lamination

        Parameters
        ----------
        self : LamSlotWind
            A LamSlotWind object

        Returns
        -------
        p: int
            Number of pair of pole

        """

        if self.winding is not None:
            return self.winding.p
        else:
            return None

    # cf Methods.Machine.LamSlotWind.plot
    def plot(
        self,
        fig=None,
        ax=None,
        is_lam_only=False,
        sym=1,
        alpha=0,
        delta=0,
        is_edge_only=False,
        edgecolor=None,
        is_add_arrow=False,
        is_display=True,
        is_add_sign=True,
        is_show_fig=True,
        save_path=None,
        win_title=None,
        is_legend=True,
        is_clean_plot=False,
        is_winding_connection=False,
        is_winding_connection_phase_A=False,
        *,
        PLUS_HATCH="++",
        MINUS_HATCH="..",
    ):
        """Plot the Lamination in a matplotlib fig

        Parameters
        ----------
        self : LamSlotWind
            A LamSlotWind object
        fig : Matplotlib.figure.Figure
            existing figure to use if None create a new one
        ax : Matplotlib.axes.Axes object
            Axis on which to plot the data
        is_lam_only : bool
            True to plot only the lamination (remove the Winding)
        sym : int
            Symmetry factor (1= full machine, 2= half of the machine...)
        alpha : float
            Angle for rotation [rad]
        delta : complex
            Complex value for translation
        is_edge_only: bool
            To plot transparent Patches
        edgecolor:
            Color of the edges if is_edge_only=True
        is_display : bool
            False to return the patches
        is_add_sign : bool
            True to Add + / - on the winding
        is_show_fig : bool
            To call show at the end of the method
        save_path : str
            full path including folder, name and extension of the file to save if save_path is not None
        win_title : str
            Title for the window
        is_legend : bool
            True to add the legend
        is_clean_plot : bool
            True to remove title, legend, axis (only machine on plot with white background)
        is_winding_connection : bool
            True to display winding connections (plot based on plot_polar_layout method of swat-em)
        is_winding_connection : bool
            True to display winding connections on phase A only
        Returns
        -------
        patches : list
            List of Patches
        fig : Matplotlib.figure.Figure
            Figure containing the plot
        ax : Matplotlib.axes.Axes object
            Axis containing the plot
        """
        # Arrow style
        head = None
        style = "Simple, tail_width=2, head_width=8, head_length=12"
        kw = dict(arrowstyle=style, linewidth=0.8, edgecolor="k")

        # If the winding is user defined, we can not plot the radial pattern
        if isinstance(self.winding, WindingUD):
            is_winding_connection = False

        # Get the LamSlot surface(s)
        surf_list = self.build_geometry(sym=sym, alpha=alpha, delta=delta)

        patches = list()
        # getting the number of phases and winding connection matrix
        if self.winding is not None:
            if isinstance(self.winding, WindingSC):  # plot only one phase for WindingSC
                wind_mat = None
                qs = 1
            else:
                try:
                    wind_mat = self.winding.get_connection_mat(self.get_Zs())
                    qs = self.winding.qs
                    # Calling swat-em method for the winding if we want to plot the radial pattern
                    if is_winding_connection:
                        # generate a datamodel for the winding
                        wdg = datamodel()
                        # generate winding from inputs
                        wdg.genwdg(
                            Q=self.get_Zs(),
                            P=2 * self.get_pole_pair_number(),
                            m=qs,
                            layers=self.winding.Nlayer,
                            turns=self.winding.Ntcoil,
                            w=self.winding.coil_pitch,
                        )
                        head = wdg.get_wdg_overhang(optimize_overhang=False)
                except:
                    wind_mat = None
                    qs = 1
        else:
            wind_mat = None
            qs = 1

        patch_leg, label_leg = list(), list()
        for surf in surf_list:
            label_dict = decode_label(surf.label)
            if (
                WIND_LAB in label_dict["surf_type"]
                or BAR_LAB in label_dict["surf_type"]
            ):
                if not is_lam_only:
                    color, sign = find_wind_phase_color(
                        wind_mat=wind_mat, label=surf.label
                    )
                    if sign == "+" and is_add_sign:
                        hatch = PLUS_HATCH
                    elif sign == "-" and is_add_sign:
                        hatch = MINUS_HATCH
                    else:
                        hatch = None
                    patches.extend(
                        surf.get_patches(
                            color=color,
                            is_edge_only=is_edge_only,
                            hatch=hatch,
                            edgecolor=edgecolor,
                        )
                    )
            else:
                color, legend = get_color_legend_from_surface(surf, is_lam_only)

                if color is not None:
                    patches.extend(
                        surf.get_patches(
                            color=color,
                            is_edge_only=is_edge_only,
                            edgecolor=edgecolor,
                        )
                    )
                if not is_edge_only and legend is not None and legend not in label_leg:
                    label_leg.append(legend)
                    patch_leg.append(Patch(color=color))

        # Adding arrows between slots for winding radial pattern
        if head is not None:
            # Taking into account slot shifting transformation
            if self.winding.Nslot_shift_wind not in [0, None]:
                Nslot_shift_wind = self.winding.Nslot_shift_wind
            else:
                Nslot_shift_wind = 0

            # Permuting B and C if asked
            if self.winding.is_permute_B_C:
                head_2 = head.copy()
                head_2[1] = head[2]
                head_2[2] = head[1]
                head = head_2

            # Detecting the direction of the layer (tangential or radial)
            # If Nlayer > 1 then we have to precise if the direction is tangential or radial
            # If Nlayer ==1 then checking radial but value always equal to 0
            Nrad, Ntan = self.winding.get_dim_wind()
            if Nrad < Ntan:
                layer_id_name = "T_id"
            else:
                layer_id_name = "R_id"

            Zs = self.get_Zs()
            for idx_phase, phase in enumerate(head):
                # Take into account case where only want to plot one phase for readability
                if is_winding_connection_phase_A and idx_phase != 0:
                    break
                for coil in phase:
                    # Recovering the starting and ending slot index of the coil (applying reverse layer transformation if needed)
                    if self.winding.is_reverse_wind:
                        start_slot_idx = Zs + Nslot_shift_wind + 1 - coil[0][0]
                        end_slot_idx = Zs + Nslot_shift_wind + 1 - coil[0][1]
                    else:
                        start_slot_idx = coil[0][0] + Nslot_shift_wind
                        end_slot_idx = coil[0][1] + Nslot_shift_wind

                    # Recovering the starting and ending slot layer index of the coil (applying reverse layer transformation if needed)
                    if (
                        self.winding.is_reverse_layer
                        ^ (self.winding.is_reverse_wind and layer_id_name == "T_id")
                        ^ (
                            self.winding.is_reverse_wind
                            and layer_id_name == "R_id"
                            and self.is_internal
                        )
                    ):
                        start_slot_layer_idx = coil[3][0]
                        end_slot_layer_idx = coil[3][1]
                    else:
                        start_slot_layer_idx = self.winding.Nlayer - 1 - coil[3][0]
                        end_slot_layer_idx = self.winding.Nlayer - 1 - coil[3][1]

                    start_slot = (start_slot_idx, start_slot_layer_idx)
                    end_slot = (end_slot_idx, end_slot_layer_idx)

                    # If the value is geater than Zs putting it back between 1 and Zs
                    if start_slot[0] > Zs:
                        start_slot = (start_slot[0] % Zs, start_slot[1])
                    if end_slot[0] > Zs:
                        end_slot = (end_slot[0] % Zs, end_slot[1])

                    # Recovering the winding direction:  1-> from left to right, -1-> from right to left
                    # Applying reverse winding transformation by changing the winding direction as well
                    if self.winding.is_reverse_wind:
                        winding_direction = -1 * coil[2]
                    else:
                        winding_direction = coil[2]

                    # Recovering the surface corresponding to the starting slot and ending slot
                    wind_surf_list = [
                        surf
                        for surf in surf_list
                        if WIND_LAB in decode_label(surf.label)["surf_type"]
                    ]

                    start_slot_surf = [
                        surf
                        for surf in wind_surf_list
                        if decode_label(surf.label)["S_id"] + 1 == start_slot[0]
                        and decode_label(surf.label)[layer_id_name] == start_slot[1]
                    ]

                    end_slot_surf = [
                        surf
                        for surf in wind_surf_list
                        if decode_label(surf.label)["S_id"] + 1 == end_slot[0]
                        and decode_label(surf.label)[layer_id_name] == end_slot[1]
                    ]

                    # Making sure that only one surface was selected for each slot
                    if len(start_slot_surf) != 1 or len(end_slot_surf) != 1:
                        raise Exception(
                            "Could not find the surface of the starting or ending slot of the winding"
                        )
                    else:
                        start_slot_surf = start_slot_surf[0]
                        end_slot_surf = end_slot_surf[0]

                    # Recovering the start point and ending point of the arrow as the center of each slot
                    start_point = [
                        start_slot_surf.comp_point_ref().real,
                        start_slot_surf.comp_point_ref().imag,
                    ]

                    end_point = [
                        end_slot_surf.comp_point_ref().real,
                        end_slot_surf.comp_point_ref().imag,
                    ]

                    # Computing the angle of the arc and its sign
                    dist_AB = np.sqrt(
                        (end_point[0] - start_point[0]) ** 2
                        + (end_point[1] - start_point[1]) ** 2
                    )

                    # Changing arrow size depending on type of rotor (inner or outer)
                    arrow_size = -0.5 if self.is_internal else 1.5
                    angle = winding_direction * (arrow_size * self.Rext) / dist_AB

                    # Adding the arrow as a Patch
                    line = FancyArrowPatch(
                        start_point,
                        end_point,
                        connectionstyle="arc3,rad=" + str(angle),
                        facecolor=self.PHASE_COLORS[idx_phase],
                        **kw,
                    )
                    patches.append(line)

        if is_display:
            # Display the result
            (fig, ax, patch_leg_1, label_leg_1) = init_fig(
                fig=fig, ax=ax, shape="rectangle"
            )

            # Merge patch_leg, label_leg
            for l, p in zip(label_leg_1, patch_leg_1):
                if l not in label_leg:
                    label_leg.append(l)
                    patch_leg.append(p)

            ax.set_xlabel("[m]")
            ax.set_ylabel("[m]")
            for patch in patches:
                ax.add_patch(patch)
            # Axis Setup
            ax.axis("equal")

            # Window title
            if is_winding_connection:
                if self.is_stator:
                    prefix = "Stator winding radial pattern "
                else:
                    prefix = "Rotor winding radial pattern "
            else:
                if self.is_stator:
                    prefix = "Stator "
                else:
                    prefix = "Rotor "
            if (
                win_title is None
                and self.parent is not None
                and self.parent.name not in [None, ""]
            ):
                win_title = self.parent.name + " " + prefix[:-1]
            elif win_title is None:
                win_title = prefix[:-1]
            manager = plt.get_current_fig_manager()
            if manager is not None:
                manager.set_window_title(win_title)

            # The Lamination is centered in the figure
            Lim = self.Rext * 1.5
            ax.set_xlim(-Lim, Lim)
            ax.set_ylim(-Lim, Lim)

            title = None

            # Add the legend
            if not is_edge_only:
                if is_winding_connection:
                    if self.is_stator and "Stator" not in label_leg:
                        title = "Stator winding radial pattern"
                    elif not self.is_stator and "Rotor" not in label_leg:
                        title = "Rotor winding radial pattern"
                elif is_lam_only:
                    if self.is_stator and "Stator" not in label_leg:
                        title = "Stator Lamination"
                    elif not self.is_stator and "Rotor" not in label_leg:
                        title = "Rotor Lamination"
                else:
                    if self.is_stator and "Stator" not in label_leg:
                        title = "Stator with winding"
                    elif not self.is_stator and "Rotor" not in label_leg:
                        title = "Rotor with winding"

                ax.set_title(title)

                # Add the winding legend only if needed
                if not is_lam_only and self.winding is not None:
                    if is_add_sign:
                        if "Phase +" not in label_leg:
                            # Adding + and - in the legend as separate patch
                            patch_leg.append(Patch(color="w", hatch=PLUS_HATCH))
                            patch_leg[-1].set_edgecolor("k")
                            label_leg.append("Phase +")

                        if "Phase -" not in label_leg:
                            # Adding + and - legend
                            patch_leg.append(Patch(color="w", hatch=MINUS_HATCH))
                            patch_leg[-1].set_edgecolor("k")
                            label_leg.append("Phase -")

                    phase_name = [prefix + n for n in gen_name(qs, is_add_phase=True)]
                    for ii in range(qs):
                        if not phase_name[ii] in label_leg:
                            # Avoid adding twice the same label
                            index = ii % len(self.PHASE_COLORS)
                            patch_leg.append(Patch(color=self.PHASE_COLORS[index]))
                            label_leg.append(phase_name[ii])

                if is_legend:
                    ax.legend(
                        patch_leg,
                        label_leg,
                        prop={
                            "family": dict_2D["font_name"],
                            "size": dict_2D["font_size_legend"],
                        },
                    )

                for item in (
                    [ax.xaxis.label, ax.yaxis.label]
                    + ax.get_xticklabels()
                    + ax.get_yticklabels()
                ):
                    item.set_fontname(dict_2D["font_name"])
                    item.set_fontsize(dict_2D["font_size_label"])
                ax.title.set_fontname(dict_2D["font_name"])
                ax.title.set_fontsize(dict_2D["font_size_title"])

            if save_path is not None:
                fig.savefig(save_path)
                plt.close(fig=fig)
            # Clean figure
            if is_clean_plot:
                ax.set_axis_off()
                ax.axis("equal")
                if ax.get_legend() is not None:
                    ax.get_legend().remove()
                ax.set_title("")

            if is_show_fig:
                fig.show()
            return fig, ax
        else:
            return patches

    # cf Methods.Machine.LamSlotWind.plot_mmf_unit
    def plot_mmf_unit(self, save_path=None, is_show_fig=False):
        """Plot the winding unit mmf as a function of space

        Parameters
        ----------
        self : LamSlotWind
            an LamSlotWind object
        save_path : str
            File path to save the figure
        is_show_fig : bool
            To call show at the end of the method

        Returns
        -------
        fig : Matplotlib.figure.Figure
            Figure containing the plot
        """

        name = ""
        if self.parent is not None and self.parent.name not in [None, ""]:
            name += self.parent.name + " "
        if self.is_stator:
            name += "Stator "
        else:
            name += "Rotor "

        # Compute the winding function and mmf
        qs = self.winding.qs
        p = self.get_pole_pair_number()
        MMF_U, WF = self.comp_mmf_unit(Nt=1, Na=400 * p)

        color_list = config_dict["PLOT"]["COLOR_DICT"]["COLOR_LIST"][:qs]

        fig, axs = plt.subplots(2, 1, tight_layout=True, figsize=(8, 8))

        dict_2D_0 = dict_2D.copy()
        dict_2D_0["color_list"] = color_list + ["k"]

        WF.plot_2D_Data(
            "angle{°}",
            "phase[]",
            data_list=[MMF_U],
            fig=fig,
            ax=axs[0],
            is_show_fig=is_show_fig,
            win_title=name + "phase MMF",
            **dict_2D_0,
        )

        dict_2D_0["color_list"] = [color_list[0], "k"]

        r_max = 100
        WF.plot_2D_Data(
            "wavenumber=[0," + str(r_max) + "]",
            data_list=[MMF_U],
            fig=fig,
            ax=axs[1],
            is_show_fig=is_show_fig,
            win_title=name + "phase MMF FFT",
            save_path=save_path,
            **dict_2D_0,
        )
        set_plot_gui_icon()

        return fig

    # cf Methods.Machine.LamSlotWind.plot_winding
    def plot_winding(
        self,
        wind_mat=None,
        all_slot=False,
        is_show_fig=True,
        save_path=None,
        win_title=None,
    ):
        """Plot the Winding in a matplotlib fig

        Parameters
        ----------
        self : LamSlotWind
            A: LamSlotWind object
        wind_mat : numpy.ndarray
            Winding Matrix, if None will call get_connection_mat (Default value = None)
        all_slot : bool
            True if we plot all slot and false when plotting only needed one(sym)
        is_show_fig : bool
            To call show at the end of the method
        save_path : str
            full path including folder, name and extension of the file to save if save_path is not None
        win_title:str
            Window title
        Returns
        -------
        None
        """

        # We compute the wind_mat only if needed
        if wind_mat is None:
            wind_mat = self.winding.get_connection_mat(self.slot.Zs)

        # Number of point on rad and tan direction
        Nrad, Ntan = self.winding.get_dim_wind()
        Zs = self.slot.Zs  # Number of slot

        # Number of Slot to plot
        if all_slot:  # Every Slot
            Nplot = Zs
        else:  # Only the needed one (sym)
            Nperw, _ = self.winding.get_periodicity()  # Symmetry of the winding
            Nplot = Zs // Nperw

        qs = wind_mat.shape[3]  # Number of phase

        # Symbole for pole
        qs_color = gen_color(self.winding.qs)
        qs_name = gen_name(self.winding.qs)

        # Schematic slot without ratio
        Wt = 0.5
        W0 = 0.5
        H = 1

        # Coordinate of the First Slot   (center on 0)
        Slot_tan = np.array(
            [-Wt / 2 - W0 / 2, -W0 / 2, -W0 / 2, W0 / 2, W0 / 2, W0 / 2 + Wt / 2]
        )
        Slot_rad = [0, 0, H, H, 0, 0]

        # Duplicate the Slot along tan direction (angular abscissa )
        x = list()
        y = list()
        for i in range(0, Nplot):
            x.extend((Slot_tan + (Wt + W0) * i).tolist())
            y.extend(Slot_rad)

        # Plot the Schematics Slots
        fig, ax = subplots()
        plot(x, y, "r-")

        # First Winding Grid (Coordinate of the winding mark)
        range_x = np.linspace(-W0 / 2, W0 / 2, Ntan + 1, endpoint=False)
        range_y = np.linspace(0, H, Nrad + 1, endpoint=False)
        # We don't want the first and last point of the linespace
        Grid_x, Grid_y = np.meshgrid(range_x[1:], range_y[1:])

        # Plot the Winding Grid point by point by reading wind_mat
        for Zs in range(0, Nplot):  # For "every" Slot
            for q in range(0, qs):  # For every phase
                for r in range(0, Nrad):  # For every rad layer
                    for theta in range(0, Ntan):  # For every tan layer
                        if wind_mat[r, theta, Zs, q] != 0:
                            # Add the correct mark at the correct coordinates
                            if wind_mat[r, theta, Zs, q] > 0:
                                plot(
                                    Grid_x[r][theta] + Zs * (Wt + W0),
                                    Grid_y[r][theta],
                                    color=qs_color[q],
                                    linewidth=0,
                                    marker="+",
                                    markeredgewidth=3,
                                    markersize=20,
                                )
                            else:
                                plot(
                                    Grid_x[r][theta] + Zs * (Wt + W0),
                                    Grid_y[r][theta],
                                    color=qs_color[q],
                                    linewidth=0,
                                    marker="x",
                                    markeredgewidth=3,
                                    markersize=20,
                                )
        if self.is_stator:
            Lam_Name = "Stator"
        else:
            Lam_Name = "Rotor"
        if all_slot or Nperw == 1:
            ax.set_title(Lam_Name + "'s Winding (every slot)")
        else:
            ax.set_title(Lam_Name + "'s Winding (periodicity 1/" + str(Nperw) + ")")

        # Window title
        if (
            win_title is None
            and self.parent is not None
            and self.parent.name not in [None, ""]
        ):
            win_title = self.parent.name + " " + Lam_Name + " Winding"
        elif win_title is None:
            win_title = Lam_Name + " Winding"
        manager = plt.get_current_fig_manager()
        if manager is not None:
            manager.set_window_title(win_title)

        ax.axis("equal")
        ax.get_yaxis().set_visible(False)

        # Legend qs
        sym_leg = list()  # Symbol
        label_leg = list()  # Text
        for q in range(0, qs):  # Positive mark
            sym_leg.append(
                Line2D(
                    [],
                    [],
                    color=qs_color[q],
                    linewidth=0,
                    marker="+",
                    markeredgewidth=3,
                    markersize=20,
                )
            )
            label_leg.append(qs_name[q] + "+")
        for q in range(0, qs):  # Negative mark
            sym_leg.append(
                Line2D(
                    [],
                    [],
                    color=qs_color[q],
                    linewidth=0,
                    marker="x",
                    markeredgewidth=3,
                    markersize=20,
                )
            )
            label_leg.append(qs_name[q] + "-")

        ax.legend(sym_leg, label_leg, ncol=2)

        if is_show_fig:
            fig.show()

        if save_path is not None:
            fig.savefig(save_path)
            plt.close(fig=fig)
        return fig, ax

    # cf Methods.Machine.LamSlotWind.set_pole_pair_number
    def set_pole_pair_number(self, p):
        """Set the number of pair of pole of the Lamination

        Parameters
        ----------
        self : LamSlotWind
            A LamSlotWind object
        p: int
            Number of pair of pole

        """

        if self.winding is not None:
            self.winding.p = p
            # Enforce call to redefine winding matrix
            self.winding.clean()

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
        Ksfill=None,
        winding=-1,
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
            if "Ksfill" in list(init_dict.keys()):
                Ksfill = init_dict["Ksfill"]
            if "winding" in list(init_dict.keys()):
                winding = init_dict["winding"]
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
        self.Ksfill = Ksfill
        self.winding = winding
        # Call LamSlot init
        super(LamSlotWind, self).__init__(
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
        # The class is frozen (in LamSlot init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        LamSlotWind_str = ""
        # Get the properties inherited from LamSlot
        LamSlotWind_str += super(LamSlotWind, self).__str__()
        LamSlotWind_str += "Ksfill = " + str(self.Ksfill) + linesep
        if self.winding is not None:
            tmp = self.winding.__str__().replace(linesep, linesep + "\t").rstrip("\t")
            LamSlotWind_str += "winding = " + tmp
        else:
            LamSlotWind_str += "winding = None" + linesep + linesep
        return LamSlotWind_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from LamSlot
        if not super(LamSlotWind, self).__eq__(other):
            return False
        if other.Ksfill != self.Ksfill:
            return False
        if other.winding != self.winding:
            return False
        return True

    def compare(self, other, name="self", ignore_list=None, is_add_value=False):
        """Compare two objects and return list of differences"""

        if ignore_list is None:
            ignore_list = list()
        if type(other) != type(self):
            return ["type(" + name + ")"]
        diff_list = list()

        # Check the properties inherited from LamSlot
        diff_list.extend(
            super(LamSlotWind, self).compare(
                other, name=name, ignore_list=ignore_list, is_add_value=is_add_value
            )
        )
        if (
            other._Ksfill is not None
            and self._Ksfill is not None
            and np.isnan(other._Ksfill)
            and np.isnan(self._Ksfill)
        ):
            pass
        elif other._Ksfill != self._Ksfill:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._Ksfill)
                    + ", other="
                    + str(other._Ksfill)
                    + ")"
                )
                diff_list.append(name + ".Ksfill" + val_str)
            else:
                diff_list.append(name + ".Ksfill")
        if (other.winding is None and self.winding is not None) or (
            other.winding is not None and self.winding is None
        ):
            diff_list.append(name + ".winding None mismatch")
        elif self.winding is not None:
            diff_list.extend(
                self.winding.compare(
                    other.winding,
                    name=name + ".winding",
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

        # Get size of the properties inherited from LamSlot
        S += super(LamSlotWind, self).__sizeof__()
        S += getsizeof(self.Ksfill)
        S += getsizeof(self.winding)
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

        # Get the properties inherited from LamSlot
        LamSlotWind_dict = super(LamSlotWind, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs,
        )
        LamSlotWind_dict["Ksfill"] = self.Ksfill
        if self.winding is None:
            LamSlotWind_dict["winding"] = None
        else:
            LamSlotWind_dict["winding"] = self.winding.as_dict(
                type_handle_ndarray=type_handle_ndarray,
                keep_function=keep_function,
                **kwargs,
            )
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        LamSlotWind_dict["__class__"] = "LamSlotWind"
        return LamSlotWind_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        Ksfill_val = self.Ksfill
        if self.winding is None:
            winding_val = None
        else:
            winding_val = self.winding.copy()
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
            Ksfill=Ksfill_val,
            winding=winding_val,
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

        self.Ksfill = None
        if self.winding is not None:
            self.winding._set_None()
        # Set to None the properties inherited from LamSlot
        super(LamSlotWind, self)._set_None()

    def _get_Ksfill(self):
        """getter of Ksfill"""
        return self._Ksfill

    def _set_Ksfill(self, value):
        """setter of Ksfill"""
        check_var("Ksfill", value, "float", Vmin=0, Vmax=1)
        self._Ksfill = value

    Ksfill = property(
        fget=_get_Ksfill,
        fset=_set_Ksfill,
        doc="""Imposed Slot Fill factor (if None, will be computed according to the winding and the slot)

        :Type: float
        :min: 0
        :max: 1
        """,
    )

    def _get_winding(self):
        """getter of winding"""
        return self._winding

    def _set_winding(self, value):
        """setter of winding"""
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
                "pyleecan.Classes", value.get("__class__"), "winding"
            )
            value = class_obj(init_dict=value)
        elif type(value) is int and value == -1:  # Default constructor
            Winding = import_class("pyleecan.Classes", "Winding", "winding")
            value = Winding()
        check_var("winding", value, "Winding")
        self._winding = value

        if self._winding is not None:
            self._winding.parent = self

    winding = property(
        fget=_get_winding,
        fset=_set_winding,
        doc="""Lamination's Winding

        :Type: Winding
        """,
    )

    class MachineCheckError(Exception):
        """ """

        pass

    class LaminationCheckError(MachineCheckError):
        """ """

        pass

    class Lam_WindCheckError(LaminationCheckError):
        """ """

        pass

    class LWC_SlotTooLong(Lam_WindCheckError):
        """ """

        pass


MachineCheckError = LamSlotWind.MachineCheckError

LaminationCheckError = LamSlotWind.LaminationCheckError

Lam_WindCheckError = LamSlotWind.Lam_WindCheckError

LWC_SlotTooLong = LamSlotWind.LWC_SlotTooLong
