# Experimental pydantic model generated from Generator/ClassesRef/Loss/LossModelBertotti.csv
"""Generated experimental pydantic model; do not edit by hand."""

from typing import TYPE_CHECKING, ClassVar

import matplotlib.pyplot as plt
import numpy as np
from pydantic import Field
from scipy.optimize import curve_fit

from ...classes_common.parents import container_or_parent
from .loss_model import LossModel

if TYPE_CHECKING:
    from ..material.material import Material
    from ..mesh.mesh_solution import MeshSolution
    from ..output.output import Output
    from ..scidatatool.data import Data
    from .loss import Loss


class LossModelBertotti(LossModel):
    """Bertotti Loss Model Class

    Attributes
    ----------
    k_hy : float or None
        Hysteresis loss coefficient
        Unit: W/kg; Default: None
    k_ed : float or None
        Eddy current loss coefficient
        Unit: W/kg; Default: None
    k_ex : float or None
        Excess loss coefficient
        Unit: W/kg; Default: None
    is_stacking_factor : bool
        True to consider lamination stacking factor when calculating core losses
        Default: False
    alpha_B : float or None
        Hysteresis loss exponent
        Default: None
    """

    k_hy: float | None = Field(default=None, json_schema_extra={"unit": "W/kg"})
    """Hysteresis loss coefficient"""
    k_ed: float | None = Field(default=None, json_schema_extra={"unit": "W/kg"})
    """Eddy current loss coefficient"""
    k_ex: float | None = Field(default=None, json_schema_extra={"unit": "W/kg"})
    """Excess loss coefficient"""
    is_stacking_factor: bool = False
    """True to consider lamination stacking factor when calculating core losses"""
    alpha_B: float | None = None
    """Hysteresis loss exponent"""

    _package: ClassVar[str] = "Loss"
    """Name of the package of the legacy class module"""

    # Inlined from Methods.Loss.LossModelBertotti.comp_coeff
    def comp_coeff(self, material: Material) -> None:
        """Enables to compute the coefficients of the loss model with a curve fitting
        on loss data stored in the material (stored in self.k_hy, self.k_ed, self.k_ex)

        Parameters
        ----------
        self : LossModelBertotti
            A loss model to compute Bertotti losses
        material : Material
            A material object, corresponding to the material used in the electrical machine.
            This material object must contain loss data as an ImportMatrixVal object.
            This matrix must contain 3 rows, correspoding to the excitation frequency (Hz),
            the peak magnetic flux density (T), and the loss density (W/kg) in this order.
        """

        parameter_names = ["k_hy", "k_ed", "k_ex", "alpha_B"]
        parameters = [getattr(self, name) for name in parameter_names]
        free_indices = [
            index for index, value in enumerate(parameters) if value is None
        ]

        def comp_loss(xdata, *free_parameters):
            """A function that compute the loss with respect to the maximum value and the frequency of the magnetic flux density

            Parameters
            ----------
            xdata : ndarray
                input matrix with f in the first line and B in the second line
            *free_parameters : float
                Values of the coefficients that are not fixed on the loss model

            Returns
            -------
            loss : ndarray
                loss for each value of f and B in the input array
            """

            fitted_parameters = parameters.copy()
            for index, value in zip(free_indices, free_parameters):
                fitted_parameters[index] = value

            return self.comp_loss_val(xdata, *fitted_parameters)

        loss_data = material.mag.LossData.get_data()

        f = loss_data[0]
        B = loss_data[1]
        loss = loss_data[2]

        xdata = np.array([f, B])
        ydata = np.array(loss)

        if free_indices:
            popt, _ = curve_fit(
                comp_loss,
                xdata,
                ydata,
                p0=np.ones(len(free_indices)),
                bounds=(
                    np.zeros(len(free_indices)),
                    np.full(len(free_indices), np.inf),
                ),
            )

            for index, value in zip(free_indices, popt):
                setattr(self, parameter_names[index], value)

    @staticmethod
    def comp_loss_val(
        xdata: np.ndarray, k_hy: float, k_ed: float, k_ex: float, alpha_B: float
    ) -> np.ndarray:
        """A function that compute the loss with respect to the maximum value and the frequency of the magnetic flux density

        Parameters
        ----------
        xdata : ndarray
            input matrix with f in the first line and B in the second line
        k_hy : float
            hysteresis loss coefficient
        k_ed : float
            Eddy current loss coefficient
        k_ex : float
            excess loss coefficient
        alpha_B : float
            hysteresis flux density amplitude exponent

        Returns
        -------
        loss : ndarray
            loss for each value of f and B in the input array
        """

        f = xdata[0]
        B = xdata[1]

        return k_hy * f * B**alpha_B + k_ed * (f * B) ** 2 + k_ex * (f * B) ** 1.5

    # Inlined from Methods.Loss.LossModelBertotti.comp_loss
    def comp_loss(
        self,
        meshsol: MeshSolution | None = None,
        loss: Loss | None = None,
        output: Output | None = None,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Calculate loss density in iron core given by group "stator core" or "rotor core"
        assuming power density is given by a Bertotti model

            Pcore = k_hy * f * B^2 + k_ed * (f B)^2 + k_ex * (f B)^1.5

        Parameters
        ----------
        self: LossModelBertotti
            a LossModelBertotti object
        meshsol : MeshSolution
            magnetic meshsolution with stator and rotor solutions merged (default: OutMag.get_meshsolution())
        loss : Loss, optional
            Loss object holding the model (default: the parent)
        output : Output, optional
            Output of the simulation (default: the parent of the simulation)

        Returns
        -------
        Pcore_density : ndarray
            Core loss density function of frequency and elements [W/m3]
        freqs: ndarray
            frequency vector [Hz]
        """
        output = container_or_parent(self, output, "output", depth=3)

        if output is None:
            raise ValueError("Cannot calculate core losses if simu is not in an Output")
        else:
            pass

        machine = output.simu.machine

        per_a = output.geo.per_a
        if output.geo.is_antiper_a:
            per_a *= 2

        lamination = machine.stator if "stator" in self.group else machine.rotor
        Lst = lamination.L1
        # Taking into account the stacking factor
        Kf = lamination.Kf1
        rho = lamination.mat_type.struct.rho

        # Compute the coefficients only if at least one is not provided
        if None in [self.k_hy, self.k_ed, self.k_ex]:
            material = lamination.mat_type
            self.comp_coeff(material)

        # Get loss coefficients
        # The loss data are given in W/kg, but the loss density in pyleecan are computed in W/m^3
        k_hy = self.k_hy / Kf * rho
        k_ed = self.k_ed / Kf * rho
        k_ex = self.k_ex / Kf * rho

        # Get fundamental frequency
        felec = output.elec.OP.get_felec()

        if output.mag is None:
            raise ValueError("Cannot calculate core losses if OutMag is None")

        if meshsol is None:
            if output.mag.meshsolution is None:
                raise ValueError(
                    "Cannot calculate core losses if OutMag.meshsolution is None"
                )
            # Merge stator and rotor frame solutions on the same Time axis
            meshsol = output.mag.get_meshsolution()

        group_list = list(meshsol.group.keys())

        if self.group not in group_list:
            raise ValueError("Cannot calculate core losses for group=" + self.group)

        try:
            solution_B = meshsol["B"]
        except KeyError:
            raise KeyError("Cannot calculate core losses if B is not in meshsolution")

        # Get element indices associated to group
        Igrp = meshsol.group[self.group]

        # Get element surface associated to group
        Se = meshsol.mesh.get_element_area()[Igrp]

        Bvect = solution_B.field
        axes_list = Bvect.get_axes()
        Time_orig = axes_list[0]
        Time = Time_orig.copy()

        # Check Time axis periodicity in function of group
        is_change_Time = False
        if "rotor" in self.group:
            if "antiperiod" in Time_orig.symmetries:
                Time.symmetries = {"period": Time_orig.symmetries["antiperiod"]}
                is_change_Time = True
        if is_change_Time:
            for comp in Bvect.components.values():
                comp.axes[0] = Time

        # # Plot 2D to check periodicity
        # # ii = Igrp[0]
        # ii = 1560
        # Bvect.components["comp_x"].plot_2D_Data(
        #     "time",
        #     "indice[" + str(ii) + "]",
        #     data_list=[Bvect.components["comp_y"]],
        #     legend_list=["Bx", "By"],
        # )

        # Bvect.components["comp_x"].plot_2D_Data(
        #     "freqs",
        #     "indice[" + str(ii) + "]",
        #     data_list=[Bvect.components["comp_y"]],
        #     legend_list=["Bx", "By"],
        # )

        # Compute magnetic flux density FFT
        Bfft = Bvect.get_xyz_along("freqs", "indice=" + str(Igrp), "z=mean")
        freqs = Bfft["freqs"]
        Bfft_magnitude = np.sqrt(
            np.abs(Bfft["comp_x"]) ** 2 + np.abs(Bfft["comp_y"]) ** 2
        )

        # Compute the loss density for each element and each frequency
        Pcore_density = k_ed * (freqs[:, None] * Bfft_magnitude) ** 2
        Pcore_density += k_hy * freqs[:, None] * Bfft_magnitude**2
        Pcore_density += k_ex * (freqs[:, None] * Bfft_magnitude) ** 1.5

        if is_change_Time:
            # Change periodicity back to original periodicity
            for comp in Bvect.components.values():
                comp.axes[0] = Time_orig

        # Get frequency orders
        n = freqs / felec

        # Integrate loss density over group volume to get polynomial coefficients
        coeff = Lst * per_a * np.matmul(Bfft_magnitude**2, Se)
        # Get polynomial coefficient
        B = np.sum(k_ed * coeff * n**2)

        coeff = Lst * per_a * np.matmul(Bfft_magnitude**1.5, Se)
        # Get polynomial coefficient
        C = np.sum(k_ex * coeff * n**1.5)

        coeff = Lst * per_a * np.matmul(Bfft_magnitude**2, Se)
        # Get polynomial coefficient
        A = np.sum(k_hy * coeff * n)

        self.coeff_dict = {"1": A, "2": B, "1.5": C}

        return Pcore_density, freqs

    # Inlined from Methods.Loss.LossModelBertotti.comp_loss_freq
    def comp_loss_freq(
        self, loss: Loss | None = None, output: Output | None = None
    ) -> tuple[np.ndarray, dict[str, np.ndarray], np.ndarray]:
        """Calculate loss density in iron core given by group "stator core" or "rotor core"
        assuming power density is given by a Bertotti model depending on frequency:

            Pcore = k_hy * f * B^(alpha_B) + k_ed * (f B)^2 + k_ex * (f B)^1.5

        Parameters
        ----------
        self: LossModelBertotti
            a LossModelBertotti object
        loss : Loss, optional
            Loss object holding the model (default: the parent)
        output : Output, optional
            Output of the simulation (default: the parent of the simulation)

        Returns
        -------
        Pcore_density : ndarray
            Average core loss density (frequency=0Hz) for all elements [W/m3]
        Pcore_dict: {ndarray}
            Dict containing the array of core losses by contribution and for all frequencies in magnetic flux density [W]
        freqs: ndarray
            frequency vector of magnetic flux density harmonics [Hz]
        """
        output = container_or_parent(self, output, "output", depth=3)

        if output is None:
            raise ValueError("Cannot calculate core losses if simu is not in an Output")
        else:
            pass

        machine = output.simu.machine

        lamination = machine.stator if "stator" in self.group else machine.rotor
        Lst = lamination.L1
        # Taking into account the stacking factor
        if self.is_stacking_factor:
            Kf = lamination.Kf1
        else:
            Kf = 1
        rho = lamination.mat_type.struct.rho

        # Compute the coefficients only if at least one is not provided (the others being enforced by Loss.run())
        if None in [self.k_hy, self.k_ed, self.k_ex, self.alpha_B]:
            material = lamination.mat_type
            self.comp_coeff(material)

        # Get loss coefficients
        # The loss data are given in W/kg, but the loss density in pyleecan are computed in W/m^3
        k_hy = self.k_hy * rho
        k_ed = self.k_ed * rho
        k_ex = self.k_ex * rho
        alpha_B = self.alpha_B

        # Get fundamental frequency
        felec = output.elec.OP.get_felec()

        # Get magnetic meshsolution and label suffix of the frame in which group quantities are calculated
        meshsol, suffix = output.get_frame_meshsolution(self.group, "core losses")

        if "B" + suffix in meshsol:
            Bvect = meshsol["B" + suffix].field
        else:
            raise ValueError("Cannot calculate core losses if B is not in meshsolution")

        # Get mesh spatial symmetries (including (anti)-periodicities)
        per_a = meshsol.mesh.sym

        # Get element indices associated to group
        Igrp = meshsol.group[self.group]

        # Get element surface associated to group
        Se = meshsol.mesh.get_element_area()[Igrp]

        # Compute magnetic flux density FFT
        Bfft = Bvect.get_xyz_along("freqs", "indice=" + str(Igrp), "z=mean")
        freqs = Bfft["freqs"]
        Bfft_square = np.abs(Bfft["comp_x"]) ** 2 + np.abs(Bfft["comp_y"]) ** 2

        # Compute the loss density for each element and each frequency
        Pcore_density_hys = k_hy / Kf * freqs[:, None] * Bfft_square ** (alpha_B / 2)
        Pcore_density_edd = k_ed / Kf * freqs[:, None] ** 2 * Bfft_square
        Pcore_density_exc = k_ex / Kf * freqs[:, None] ** 1.5 * Bfft_square**0.75

        # Sum all core losses contribution and sum over frequencies to get average loss density value per element
        Pcore_density = np.sum(
            Pcore_density_hys + Pcore_density_edd + Pcore_density_exc,
            axis=0,
            keepdims=True,
        )

        # Integrate volumic density over core volume to get loss value per contribution
        Pcore_hys = Lst * per_a * np.matmul(Pcore_density_hys, Se)
        Pcore_edd = Lst * per_a * np.matmul(Pcore_density_edd, Se)
        Pcore_exc = Lst * per_a * np.matmul(Pcore_density_exc, Se)

        # Sum all core losses contributions
        Pcore = Pcore_hys + Pcore_edd + Pcore_exc

        # Store losses contribution for each frequency in dict
        Pcore_dict = {
            self.group + " losses": Pcore,
            self.group + " hysteresis": Pcore_hys,
            self.group + " eddy current": Pcore_edd,
            self.group + " excess": Pcore_exc,
        }

        # Get hysteresis loss polynomial coefficient
        A = np.sum(Pcore_hys) / felec

        # Get eddy-current loss polynomial coefficient
        B = np.sum(Pcore_edd) / felec**2

        # Get excess loss polynomial coefficient
        C = np.sum(Pcore_exc) / felec**1.5

        # Store polynom coefficients in dict
        self.coeff_dict = {"1.0": A, "2.0": B, "1.5": C}

        return Pcore_density, Pcore_dict, freqs

    # Inlined from Methods.Loss.LossModelBertotti.comp_loss_time
    def comp_loss_time(
        self,
        axes_dict: dict[str, Data],
        is_mirror: bool,
        loss: Loss | None = None,
        output: Output | None = None,
    ) -> tuple[np.ndarray, dict[str, np.ndarray]]:
        """Calculate loss density over time in iron core given by group "stator core" or "rotor core"
        assuming power density is given by a Bertotti model

        The equations are given in :
        A Dynamic Core Loss Model for Soft Ferromagnetic and Power Ferrite Materials in Transient Finite Element Analysis.
        Lin, D. & Zhou, P. & Fu, Weinong & Badics, Zsolt & Cendes, Z.J.. (2004).
        IEEE Transactions on Magnetics. 40. 1318-1321. 10.1109/TMAG.2004.825025.

        Parameters
        ----------
        self: LossModelBertotti
            a LossModelBertotti object
        axes_dict: {Data}
            Dict containing Time (including (anti-)periodicties) and Indices axes used in any Loss module
        is_mirror : bool
            True to mirror magnetic mesh quantities calculate in stator and rotor frames to get the same Time axis
        loss : Loss, optional
            Loss object holding the model (default: the parent)
        output : Output, optional
            Output of the simulation (default: the parent of the simulation)

        Returns
        -------
        Pcore_density : ndarray
            Core loss density function of time and elements [W/m3]
        Pcore_dict: {ndarray}
            Dict containing the array of core losses over time
        """
        output = container_or_parent(self, output, "output", depth=3)

        if output is None:
            raise ValueError("Cannot calculate core losses if simu is not in an Output")
        else:
            pass

        machine = output.simu.machine

        lamination = machine.stator if "stator" in self.group else machine.rotor

        Lst = lamination.L1
        # Taking into account the stacking factor
        if self.is_stacking_factor:
            Kf = lamination.Kf1
        else:
            Kf = 1
        rho = lamination.mat_type.struct.rho

        # Compute the coefficients only if at least one is not provided
        if None in [self.k_hy, self.k_ed, self.k_ex]:
            material = lamination.mat_type
            self.comp_coeff(material)

        # Get loss coefficients
        # The loss data are given in W/kg, but the loss density in pyleecan are computed in W/m^3
        k_hy = self.k_hy * rho  # Not used in Bertotti time-dependant model
        k_ed = self.k_ed * rho
        k_ex = self.k_ex * rho

        # B exponent in hysteresis loss model
        alpha_B = self.alpha_B

        # Get magnetic meshsolution and label suffix of the frame in which group quantities are calculated
        meshsol, suffix = output.get_frame_meshsolution(self.group, "core losses")

        if "B" + suffix in meshsol:
            Bvect = meshsol["B" + suffix].field
        else:
            raise ValueError("Cannot calculate core losses if B is not in meshsolution")

        if "H" + suffix in meshsol:
            Hvect = meshsol["H" + suffix].field
        else:
            raise ValueError("Cannot calculate core losses if H is not in meshsolution")

        # Get mesh spatial symmetries (including (anti)-periodicities)
        per_a = meshsol.mesh.sym

        # Get surface and number of all elements
        Se_all = meshsol.mesh.get_element_area()

        # Get element indices associated to group
        Igrp = meshsol.group[self.group]

        # Get element surface associated to group
        Se = Se_all[Igrp]

        # Compute magnetic flux density derivative over time
        dB_dt_v = Bvect.get_vectorfield_along("time=derivate", "indice", "z")

        if is_mirror:
            # Rebuild magnet mesh quantities on time steps given by axes_dict
            time_val = axes_dict["time"].get_values(is_smallestperiod=True)
            H = Hvect.get_xyz_along(
                "time=axis_data",
                "indice=" + str(Igrp),
                "z=mean",
                axis_data={"time": time_val},
            )
            dB_dt = dB_dt_v.get_xyz_along(
                "time=axis_data",
                "indice=" + str(Igrp),
                "z=mean",
                axis_data={"time": time_val},
            )
        else:
            H = Hvect.get_xyz_along(
                "time[smallestperiod]", "indice=" + str(Igrp), "z=mean"
            )
            dB_dt = dB_dt_v.get_xyz_along(
                "time[smallestperiod]", "indice=" + str(Igrp), "z=mean"
            )

        # Compute the loss density for each element function of time
        # XXX problem hysterisys loss formula in time domain (losses are way too higher)
        Pcore_density_hys = (
            np.abs(H["comp_x"] * dB_dt["comp_x"]) ** (2 / alpha_B)
            + np.abs(H["comp_y"] * dB_dt["comp_y"]) ** (2 / alpha_B)
        ) ** (alpha_B / 2) / Kf

        # Pcore_density_hys = (
        #     1
        #     / (2 * np.pi**2)
        #     * k_hy
        #     * (
        #         np.abs(dB_dt["comp_x"]) ** (2 / alpha_B)
        #         + np.abs(dB_dt["comp_y"]) ** (2 / alpha_B)
        #     )
        #     ** (alpha_B / 2)
        # )

        Pcore_density_edd = (
            k_ed / Kf / (2 * np.pi**2) * (dB_dt["comp_x"] ** 2 + dB_dt["comp_y"] ** 2)
        )

        Pcore_density_exc = (
            k_ex / Kf / 8.763363 * (dB_dt["comp_x"] ** 2 + dB_dt["comp_y"] ** 2) ** 0.75
        )

        # Integrate volumic density over core volume
        Pcore_hys = Lst * per_a * np.matmul(Pcore_density_hys, Se)
        Pcore_edd = Lst * per_a * np.matmul(Pcore_density_edd, Se)
        Pcore_exc = Lst * per_a * np.matmul(Pcore_density_exc, Se)

        # Sum all core losses contribution
        Pcore = Pcore_hys + Pcore_edd + Pcore_exc

        Pcore_density = Pcore_density_hys + Pcore_density_edd + Pcore_density_exc

        Pcore_dict = {
            self.group + " losses": Pcore,
            self.group + " hysteresis": Pcore_hys,
            self.group + " eddy current": Pcore_edd,
            self.group + " excess": Pcore_exc,
        }

        # Get fundamental frequency
        felec = output.elec.OP.get_felec()

        # Save coefficients to rebuild losses for same (Id,Iq) but at a different speed
        A = Pcore_hys.mean() / felec
        B = Pcore_edd.mean() / felec**2
        C = Pcore_exc.mean() / felec**1.5
        self.coeff_dict = {"1": A, "2": B, "1.5": C}

        return Pcore_density, Pcore_dict

    # Inlined from Methods.Loss.LossModelBertotti.plot_fitting
    def plot_fitting(self, material: Material, is_show_fig: bool = True) -> None:
        """Plot the fitted loss curves (from fitted coefficients k_hy, k_ed, k_ex, beta) and the loss data stored in the material

        Parameters
        ----------
        self : LossModelBertotti
            A loss model to compute Bertotti losses
        material : Material
            A material object, corresponding to the material used in the electrical machine.
            This material object must contain loss data as an ImportMatrixVal object.
            This matrix must contain 3 rows, correspoding to the excitation frequency (Hz),
            the peak magnetic flux density (T), and the loss density (W/kg) in this order.
        is_show_fig : bool
            True to show figure
        """

        loss_data = material.mag.LossData.get_data()
        f = loss_data[0]
        B = loss_data[1]
        loss = loss_data[2]

        f_un, i0 = np.unique(f, return_inverse=True)
        fig = plt.figure("Curve fitting for Bertotti iron loss model", figsize=(14, 7))
        B_check = np.linspace(0, 2, 1000)

        ax = plt.gca()

        for ii, f_val in enumerate(f_un):
            f_check = np.ones((1000,)) * f_val
            x_check = np.array([f_check, B_check])
            j0 = np.where(i0 == ii)[0]
            B_experimental = B[j0]
            loss_experimental = loss[j0]
            # x_experimental = values[:, :2].T
            # fitted_loss = comp_loss(x_experimental, *popt)
            # R_list.append(
            #     (key, (np.corrcoef(fitted_loss, loss_experimental)[0, 1]) ** 2)
            # )
            color = ax._get_lines._prop_cycle._cycler_items[np.mod(ii, 10)]["color"]
            # color =  plt.rcParams['axes.prop_cycle']
            plt.plot(
                B_experimental,
                loss_experimental,
                color=color,
                label=f"measurements with f={f_val}Hz",
                marker="o",
            )

            loss_val = self.comp_loss_val(
                x_check, self.k_hy, self.k_ed, self.k_ex, self.alpha_B
            )
            plt.plot(
                B_check,
                loss_val,
                color=color,
                linestyle="dashed",
                label=f"fitting with f={f_val}Hz",
            )
        plt.xlabel("Peak magnetic flux density (T)")
        plt.ylabel("Iron loss (W/kg)")
        plt.title(
            f"Curve fitting for the Bertotti iron loss model of the {material.name} material"
        )

        txt = " $P_{{loss}}=k_{{hy}} f B^{\\beta} + k_{{ed}} (f B)^2 + k_{{ex}} (f B)^{{1.5}}$\n"

        txt += "where:\n"
        txt += "$k_{{hy}}$ = " + format(self.k_hy, ".5E") + "\n"
        txt += "$k_{{ed}}$ = " + format(self.k_ed, ".5E") + "\n"
        txt += "$k_{{ex}}$ = " + format(self.k_ex, ".5E") + "\n"
        txt += "$\\beta$ = " + format(self.alpha_B, ".5E") + "\n"

        # txt += "$\\alpha_f$ = " + format(popt[2], '.5E') +"\n"
        # txt += "$\\alpha_B$ = " + format(popt[3], '.5E') +"\n"
        # plt.title(f"Curve fitting for the iron loss of the {material.name} material")
        # text = textwrap.dedent(
        #     fr"""
        #                         $P_{{loss}}=k_{{hy}} f B^2 + k_{{ed}} (f B)^2 + k_{{ex}} (f B)^{{1.5}}$
        #                         where:
        #                         $k_{{hy}}$ = {popt[0]:.5E}
        #                         $k_{{ed}}$ = {popt[1]:.5E}
        #                         $k_{{ex}}$ = {popt[2]:.5E}
        #                         """
        # )

        fig.text(0.02, 0.5, txt, fontsize=12)
        plt.subplots_adjust(left=0.26)
        plt.legend()
        if is_show_fig:
            plt.show()
