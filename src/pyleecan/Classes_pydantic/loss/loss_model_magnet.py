# Experimental pydantic model generated from Generator/ClassesRef/Loss/LossModelMagnet.csv
"""Generated experimental pydantic model; do not edit by hand."""

from typing import TYPE_CHECKING, ClassVar

import numpy as np

from ...Functions_pydantic.MeshSolution.get_frame_meshsolution import (
    get_frame_meshsolution,
)
from ..machine.lam_hole import LamHole
from ..machine.lam_slot_mag import LamSlotMag
from ..slot.hole_m_50 import HoleM50
from ..slot.hole_m_51 import HoleM51
from ..slot.hole_m_52 import HoleM52
from ..slot.hole_m_53 import HoleM53
from ..slot.hole_m_57 import HoleM57
from ..slot.hole_m_58 import HoleM58
from .loss_model import LossModel

if TYPE_CHECKING:
    from ..machine.machine import Machine
    from ..mesh.mesh_solution import MeshSolution
    from ..scidatatool.data import Data


class LossModelMagnet(LossModel):
    """Magnet Loss Model Class

    Attributes
    ----------
    """

    _package: ClassVar[str] = "Loss"
    """Name of the package of the legacy class module"""

    # Inlined from Methods.Loss.LossModelMagnet.comp_kseg
    def comp_kseg(self, machine: Machine) -> float:
        """Calculate segmentation coefficient from:
        "Effect of Eddy-Current Loss Reduction by Magnet Segmentation in Synchronous Motors With Concentrated Windings
        Katsumi Yamazaki, Member, IEEE, and Yu Fukushima, Equation (9)

        Parameters
        ----------
        self: LossModelMagnet
            a LossModelMagnet object
        machine: Machine
            a machine object

        Returns
        -------
        kseg : float
            Magnet segmentation coefficient
        """

        # Calculate segmentation coefficient from:
        # "Effect of Eddy-Current Loss Reduction by Magnet Segmentation in Synchronous Motors With Concentrated Windings"
        # Katsumi Yamazaki, Member, IEEE, and Yu Fukushima, Equation (9)
        # Get Hmag for segmentation calculation
        if isinstance(machine.rotor, LamSlotMag):
            magnet = machine.rotor.magnet
            slot = machine.rotor.slot
            if hasattr(slot, "Hmag"):
                Hmag = slot.Hmag
            else:
                Hmag = np.sqrt(slot.comp_surface_active())
            if hasattr(slot, "Wmag"):
                Wmag = slot.Wmag
            else:
                Wmag = np.sqrt(slot.comp_surface_active())

        elif isinstance(machine.rotor, LamHole):
            hole0 = machine.rotor.hole[0]
            magnet = hole0.get_magnet_dict()["magnet_0"]
            if isinstance(hole0, HoleM50):
                Hmag = hole0.H3
                Wmag = hole0.W4
            elif isinstance(hole0, (HoleM51, HoleM53, HoleM57, HoleM58)):
                Hmag = hole0.H2
                if isinstance(hole0, HoleM51):
                    Wmag = (hole0.W3 + hole0.W5 + hole0.W7) / 3
                elif isinstance(hole0, HoleM53):
                    Wmag = hole0.W3
                elif isinstance(hole0, HoleM57):
                    Wmag = hole0.W4
                elif isinstance(hole0, HoleM58):
                    Wmag = hole0.W1
            elif isinstance(hole0, HoleM52):
                Hmag = hole0.H1
                Wmag = hole0.W0
            else:  # HoleUD
                Hmag = np.sqrt(hole0.comp_surface_magnet_id(0))
                Wmag = Hmag
        else:
            raise Exception(
                "Cannot calculate magnet losses for rotor lamination other than LamSlotMag or LamHole"
            )
        Lmag = magnet.Lmag
        Nseg = magnet.Nseg
        kseg = ((Lmag + Wmag) / (Lmag * Nseg + Wmag)) ** 2

        return kseg

    # Inlined from Methods.Loss.LossModelMagnet.comp_loss
    def comp_loss(
        self, meshsol: MeshSolution | None = None
    ) -> tuple[np.ndarray, np.ndarray]:
        """Calculate eddy-current losses in rotor permanent magnets assuming power density
        is given by (cf. https://www.femm.info/wiki/SPMLoss):

            Pmag = Jm^2/sigma_m with Jm = -sigma_m*1j*2pi*f*Az + Jc where Jc=<Jm> on the magnet surface

        Parameters
        ----------
        self: LossModelMagnet
            a LossModelMagnet object
        meshsol : MeshSolution
            magnetic meshsolution with stator and rotor solutions merged (default: OutMag.get_meshsolution())

        Returns
        -------
        Pmagnet_density : ndarray
            Magnet loss density function of frequency and elements [W/m3]
        freqs: ndarray
            frequency vector [Hz]
        """

        if self.parent.parent.parent is None:
            raise Exception("Cannot calculate core losses if simu is not in an Output")
        else:
            output = self.parent.parent.parent

        machine = output.simu.machine

        per_a = output.geo.per_a
        if output.geo.is_antiper_a:
            per_a *= 2

        if isinstance(machine.rotor, LamSlotMag):
            magnet = machine.rotor.magnet
            slot = machine.rotor.slot
            if hasattr(slot, "Hmag"):
                Hmag = slot.Hmag
            else:
                Hmag = np.sqrt(slot.comp_surface_active())
            if hasattr(slot, "Wmag"):
                Wmag = slot.Wmag
            else:
                Wmag = np.sqrt(slot.comp_surface_active())

        elif isinstance(machine.rotor, LamHole):
            hole0 = machine.rotor.hole[0]
            magnet = hole0.get_magnet_dict()["magnet_0"]
            if isinstance(hole0, HoleM50):
                Hmag = hole0.H3
                Wmag = hole0.W4
            elif isinstance(hole0, (HoleM51, HoleM53, HoleM57, HoleM58)):
                Hmag = hole0.H2
                if isinstance(hole0, HoleM51):
                    Wmag = (hole0.W3 + hole0.W5 + hole0.W7) / 3
                elif isinstance(hole0, HoleM53):
                    Wmag = hole0.W3
                elif isinstance(hole0, HoleM57):
                    Wmag = hole0.W4
                elif isinstance(hole0, HoleM58):
                    Wmag = hole0.W1
            elif isinstance(hole0, HoleM52):
                Hmag = hole0.H1
                Wmag = hole0.W0
            else:  # HoleUD
                Hmag = np.sqrt(hole0.comp_surface_magnet_id(0))
                Wmag = Hmag
        else:
            raise Exception(
                "Cannot calculate magnet losses for rotor lamination other than LamSlotMag or LamHole"
            )

        # Get rotor length
        L1 = machine.rotor.L1

        # Calculate segmentation coefficient from:
        # "Effect of Eddy-Current Loss Reduction by Magnet Segmentation in Synchronous Motors With Concentrated Windings"
        # Katsumi Yamazaki, Member, IEEE, and Yu Fukushima, Equation (9)
        if (
            magnet.Lmag is None
            or magnet.Nseg is None
            or Wmag is None
            or magnet.Nseg == 1
        ):
            kseg = 1
        else:
            Lmag = magnet.Lmag
            Nseg = magnet.Nseg
            kseg = ((Lmag + Wmag) / (Lmag * Nseg + Wmag)) ** 2

        # Get fundamental frequency
        felec = output.elec.OP.get_felec()

        if output.mag is None:
            raise Exception("Cannot calculate magnet losses if OutMag is None")

        if meshsol is None:
            if output.mag.meshsolution is None:
                raise Exception(
                    "Cannot calculate magnet losses if OutMag.meshsolution is None"
                )
            # Merge stator and rotor frame solutions on the same Time axis
            meshsol = output.mag.get_meshsolution()

        group_list = list(meshsol.group.keys())

        if self.group not in group_list:
            raise Exception("Cannot calculate magnet losses for group=" + self.group)

        # Extract the solution
        solution_A = meshsol["A_z^{element}"]

        if solution_A.type_element != "triangle":
            raise ValueError(
                "Cannot calculate magnet losses if A_z calculated on element center is not in meshsolution"
            )

        # Get magnetic vector potential over time and for each element center in current group
        Az_dt = solution_A.field
        axes_list = Az_dt.get_axes()
        Time_orig = axes_list[0]
        Time = Time_orig.copy()

        # Check Time axis periodicity in function of group
        is_change_Time = False
        if "rotor" in self.group:
            if "antiperiod" in Time_orig.symmetries:
                Time.symmetries = {"period": Time_orig.symmetries["antiperiod"]}
                is_change_Time = True
        if is_change_Time:
            Az_dt.axes[0] = Time

        # Get all element surfaces
        Se = meshsol.mesh.get_element_area()

        # Get list of element indices for each magnet
        list_Imag = []
        ind_list = []
        for key in meshsol.group:
            if self.group in key and key != self.group:
                ind = int(key.split("_")[-1])
                ind_list.append(ind)
                list_Imag.append(meshsol.group[key])
        ind_all = meshsol.group[self.group]

        # Calculate induced current density and loss density
        jj = 0
        for ii, kmag in enumerate(list_Imag):
            Se_mag = Se[kmag]

            # derivation in frequency domain
            Az_df = Az_dt.get_along("freqs", "indice" + str(kmag), "z=mean")
            if ii == 0:
                freqs = Az_df["freqs"]
                w = 2 * np.pi * freqs[:, None]
                sigma_m = magnet.mat_type.elec.get_conductivity(T_op=self.parent.Trot)
                # if self.type_skin_effect:
                #     # Get magnet conductivity including skin effect
                #     magnet_cond = CondType21(Hbar=Hmag, Wbar=1, cond_mat=magnet.mat_type)
                #     kr_skin = magnet_cond.comp_skin_effect_resistance(
                #         freqs, T_op=self.parent.Trot, b=1, zt=1
                #     )
                #     kr_skin[np.isnan(kr_skin)] = 1
                #     sigma_m = sigma_m / kr_skin[:, None]
                Pmagnet_density = np.zeros((freqs.size, len(ind_all)))
            Az_fft = Az_df["A_z^{element}"]
            Az_mean = np.matmul(Az_fft, Se_mag)[:, None] / np.sum(Se_mag)
            Jm_fft = -1j * sigma_m * w * (Az_fft - Az_mean)
            Pmagnet_density[:, jj : (jj + len(kmag))] = (
                0.5 * kseg * np.abs(Jm_fft) ** 2 / sigma_m
            )
            jj += len(kmag)

            # # # derivation in time domain
            # dAz_dt = Az_dt.get_data_along("time=derivate", "indice" + str(kmag), "z[0]")
            # dAz_df = dAz_dt.get_along("freqs", "indice", "z[0]")
            # dAz_fft = dAz_df["A_z"]
            # if ii == 0:
            #     freqs = dAz_df["freqs"]
            #     w = 2 * pi * freqs[:, None]
            #     sigma_m = magnet.mat_type.elec.get_conductivity(T_op=self.Trot)
            #     if is_skin_effect:
            #         # Get magnet conductivity including skin effect
            #         magnet_cond = CondType21(Hbar=Hmag, Wbar=1, cond_mat=magnet.mat_type)
            #         kr_skin = magnet_cond.comp_skin_effect_resistance(
            #             freqs, T_op=self.Trot, b=1, zt=1
            #         )
            #         kr_skin[np.isnan(kr_skin)] = 1
            #         sigma_m = sigma_m / kr_skin[:, None]
            #     Pmagnet_density = np.zeros((freqs.size, len(ind_all)))
            # Jm_fft0 = sigma_m * (
            #     -dAz_fft + matmul(dAz_fft, Se_mag)[:, None] / np_sum(Se_mag)
            # )

            # # # Plot
            # Az_df0 = Az_dt.get_data_along("freqs", "indice" + str(kmag), "z[0]")
            # dAz_df0 = Az_df0.copy()
            # dAz_df0.values *= 1j * w[:, :, None]
            # dAz_df0.unit = "Wb/ms"
            # dAz_df0.plot_2D_Data(
            #     "freqs", "indice[0]", data_list=[dAz_dt], legend_list=["df", "dt"]
            # )
            # dAz_df0.plot_2D_Data(
            #     "time", "indice[0]", data_list=[dAz_dt], legend_list=["df", "dt"]
            # )
            # from SciDataTool import DataFreq

            # Jm_df = DataFreq(
            #     name="Current density",
            #     symbol="J_m",
            #     unit="A/m^2",
            #     values=Jm_fft,
            #     axes=Az_df0.axes,
            # )
            # Jm_df0 = DataFreq(
            #     name="Current density",
            #     symbol="J_m",
            #     unit="A/m^2",
            #     values=Jm_fft0,
            #     axes=Az_df0.axes,
            # )
            # Jm_df.plot_2D_Data(
            #     "time", "indice[0]", data_list=[Jm_df0], legend_list=["df", "dt"]
            # )
            # Jm_df.plot_2D_Data(
            #     "freqs", "indice[0]", data_list=[Jm_df0], legend_list=["df", "dt"]
            # )

        if is_change_Time:
            # Change periodicity back to original periodicity
            Az_dt.axes[0] = Time_orig

        # Get frequency orders
        n = freqs / felec
        # Integrate loss density over group volume
        I0 = n != 0
        Af = np.zeros(w.size)
        Af[I0] = (
            L1
            * per_a
            * np.matmul(Pmagnet_density[I0, :] / freqs[I0, None] ** 2, Se[ind_all])
        )
        # Sum over orders
        A = np.sum(Af * n**2)
        self.coeff_dict = {"2": A}

        return Pmagnet_density, freqs

    # Inlined from Methods.Loss.LossModelMagnet.comp_loss_freq
    def comp_loss_freq(self) -> tuple[np.ndarray, dict[str, np.ndarray], np.ndarray]:
        """Calculate eddy-current losses in rotor permanent magnets assuming power density depending on frequency
        is given by (cf. https://www.femm.info/wiki/SPMLoss):

            Pmag = Jm^2/sigma_m with Jm = -sigma_m*1j*2pi*f*Az + Jc where Jc=<Jm> on the magnet surface

        Parameters
        ----------
        self: LossModelMagnet
            a LossModelMagnet object

        Returns
        -------
        Pmagnet_density : ndarray
           Average magnet loss density (frequency=0Hz) for all elements [W/m3]
        Pmag_dict: {ndarray}
            Dict containing the array of magnet losses by contribution and for all frequencies in magnetic flux density [W]
        freqs: ndarray
            frequency vector of magnetic flux density harmonics [Hz]
        """

        if self.parent.parent.parent is None:
            raise ValueError(
                "Cannot calculate magnet losses if simu is not in an Output"
            )
        else:
            output = self.parent.parent.parent

        machine = output.simu.machine

        if isinstance(machine.rotor, LamSlotMag):
            magnet = machine.rotor.magnet
        elif isinstance(machine.rotor, LamHole):
            hole0 = machine.rotor.hole[0]
            magnet = hole0.get_magnet_dict()["magnet_0"]

        # Get rotor length
        Lst = machine.rotor.L1

        # Get magnet electrical conductivity
        sigma_m = magnet.mat_type.elec.get_conductivity(T_op=self.parent.Trot)

        # Get magnet segmentation coefficient
        if magnet.Lmag is None or magnet.Nseg is None or magnet.Nseg == 1:
            kseg = 1
        else:
            kseg = self.comp_kseg(machine)

        # Get fundamental frequency
        felec = output.elec.OP.get_felec()

        # Get magnetic meshsolution and label suffix of the frame in which group quantities are calculated
        meshsol, suffix = get_frame_meshsolution(output, self.group, "magnet losses")

        # Get magnetic vector potential over time and for each element center in current group
        if "A_z^{element}" + suffix in meshsol:
            Az_dt = meshsol["A_z^{element}" + suffix].field
        else:
            raise ValueError(
                "Cannot calculate magnet losses if  A_z calculated on element center is not in meshsolution"
            )

        # Get mesh spatial symmetries (including (anti)-periodicities)
        per_a = meshsol.mesh.sym

        # Get all element surfaces
        Se = meshsol.mesh.get_element_area()

        # Get list of element indices for each magnet
        list_Imag = []
        ind_list = []
        for key in meshsol.group:
            if self.group in key and key != self.group:
                ind = int(key.split("_")[-1])
                ind_list.append(ind)
                list_Imag.append(meshsol.group[key])
        ind_all = meshsol.group[self.group]

        # Calculate induced current density and loss density
        jj = 0
        for ii, kmag in enumerate(list_Imag):
            Se_mag = Se[kmag]

            # derivation in frequency domain
            Az_df = Az_dt.get_along("freqs", "indice=" + str(kmag), "z=mean")
            if ii == 0:
                freqs = Az_df["freqs"]
                w = 2 * np.pi * freqs[:, None]
                # if self.type_skin_effect:
                #     # Get magnet conductivity including skin effect
                #     magnet_cond = CondType21(Hbar=Hmag, Wbar=1, cond_mat=magnet.mat_type)
                #     kr_skin = magnet_cond.comp_skin_effect_resistance(
                #         freqs, T_op=self.parent.Trot, b=1, zt=1
                #     )
                #     kr_skin[np.isnan(kr_skin)] = 1
                #     sigma_m = sigma_m / kr_skin[:, None]
                Pmagnet_density = np.zeros((freqs.size, len(ind_all)))
            Az_fft = Az_df["A_z^{element}"]
            Az_mean = np.matmul(Az_fft, Se_mag)[:, None] / np.sum(Se_mag)
            Jm_fft = -1j * sigma_m * w * (Az_fft - Az_mean)
            Pmagnet_density[:, jj : (jj + len(kmag))] = (
                0.5 * kseg * np.abs(Jm_fft) ** 2 / sigma_m
            )
            jj += len(kmag)

        # Integrate loss density over group volume
        Pmagnet = Lst * per_a * np.matmul(Pmagnet_density, Se[ind_all])

        # Sum over frequencies to get average loss density value per element
        Pmagnet_density = np.sum(Pmagnet_density, axis=0, keepdims=True)

        # Store losses contribution for each frequency in dict
        Pmagnet_dict = {self.group + " losses": Pmagnet}

        # Get eddy-current magnet loss polynomial coefficient
        A = np.sum(Pmagnet) / felec**2
        self.coeff_dict = {"2.0": A}

        return Pmagnet_density, Pmagnet_dict, freqs

    # Inlined from Methods.Loss.LossModelMagnet.comp_loss_time
    def comp_loss_time(
        self, axes_dict: dict[str, Data], is_mirror: bool
    ) -> tuple[np.ndarray, dict[str, np.ndarray]]:
        """Calculate eddy-current losses in rotor permanent magnets in time domain assuming power density
        is given by (cf. https://www.femm.info/wiki/SPMLoss):

            Pmag = Jm^2/sigma_m with Jm = -sigma_m*dAz/dt + Jc where Jc=<Jm> on the magnet surface

        Parameters
        ----------
        self: LossModelMagnet
            a LossModelMagnet object
        axes_dict: {Data}
            Dict containing Time (including (anti-)periodicties) and Indices axes used in any Loss module
        is_mirror : bool
            True to mirror magnetic mesh quantities calculate in stator and rotor frames to get the same Time axis

        Returns
        -------
        Pmagnet_density : ndarray
            Magnet loss density function of time and elements [W/m3]
        Pmagnet_dict: {ndarray}
            Dict containing the array of magnet losses over time

        """

        if self.parent.parent.parent is None:
            raise ValueError(
                "Cannot calculate magnet losses if simu is not in an Output"
            )
        else:
            output = self.parent.parent.parent

        machine = output.simu.machine

        if isinstance(machine.rotor, LamSlotMag):
            magnet = machine.rotor.magnet
        elif isinstance(machine.rotor, LamHole):
            hole0 = machine.rotor.hole[0]
            magnet = hole0.get_magnet_dict()["magnet_0"]

        # Get rotor length
        Lst = machine.rotor.L1

        # Get magnet electrical conductivity
        sigma_m = magnet.mat_type.elec.get_conductivity(T_op=self.parent.Trot)

        # Get magnet segmentation coefficient
        if magnet.Lmag is None or magnet.Nseg is None or magnet.Nseg == 1:
            kseg = 1
        else:
            kseg = self.comp_kseg(machine)

        # Get magnetic meshsolution and label suffix of the frame in which group quantities are calculated
        meshsol, suffix = get_frame_meshsolution(output, self.group, "magnet losses")

        # Get magnetic vector potential over time and for each element center in current group
        if "A_z^{element}" + suffix in meshsol:
            Az = meshsol["A_z^{element}" + suffix].field
        else:
            raise ValueError(
                "Cannot calculate magnet losses if  A_z calculated on element center is not in meshsolution"
            )

        # Get mesh spatial symmetries (including (anti)-periodicities)
        per_a = meshsol.mesh.sym

        # Get surface and number of all elements
        Se_all = meshsol.mesh.get_element_area()

        # Get list of element indices for each magnet
        list_Imag = []
        ind_list = []
        for key in meshsol.group:
            if self.group in key and key != self.group:
                ind = int(key.split("_")[-1])
                ind_list.append(ind)
                list_Imag.append(meshsol.group[key])
        Igrp = meshsol.group[self.group]

        # Calculate induced current density and loss density in each magnet
        time_val = axes_dict["time"].get_values(is_smallestperiod=True)
        Pmagnet_density = np.zeros((time_val.size, len(Igrp)))
        jj = 0
        for kmag in list_Imag:
            Se_mag = Se_all[kmag]

            # Compute magnetic vector potential derivative over time
            dAz_dt = Az.get_data_along("time=derivate", "indice=" + str(kmag), "z")

            if is_mirror:
                # Rebuild mesh quantities on time steps given by axes_dict
                dAz_dt_val = dAz_dt.get_along(
                    "time=axis_data", "indice", "z=mean", axis_data={"time": time_val}
                )[dAz_dt.symbol]
            else:
                dAz_dt_val = dAz_dt.get_along(
                    "time[smallestperiod]", "indice", "z=mean"
                )[dAz_dt.symbol]

            # Calculate eddy-current current density in this magnet
            Jm = -sigma_m * dAz_dt_val

            # Ensure average current flowing through the surface is 0
            Jc = np.matmul(Jm, Se_mag)[:, None] / Se_mag.sum()
            Jm -= Jc

            # Calculate loss density due to eddy-current
            Pmagnet_density[:, jj : (jj + len(kmag))] = kseg * Jm**2 / sigma_m

            # Increment by the number elements of in this magnet
            jj += len(kmag)

        # Integrate volumic density over elements volume
        Pmagnet = Lst * per_a * np.matmul(Pmagnet_density, Se_all[Igrp])

        Pmagnet_dict = {self.group + " losses": Pmagnet}

        # Get fundamental frequency
        felec = output.elec.OP.get_felec()

        # Save coefficients to rebuild losses for same (Id,Iq) but at a different speed
        A = Pmagnet.mean() / felec**2
        self.coeff_dict = {"2": A}

        return Pmagnet_density, Pmagnet_dict
