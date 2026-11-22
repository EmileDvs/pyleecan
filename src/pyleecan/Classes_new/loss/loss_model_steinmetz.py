# Experimental dataclass generated from Generator/ClassesRef/Loss/LossModelSteinmetz.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, ClassVar

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit

from ...classes_common.errors import FieldMissingError
from ...classes_common.parents import container_or_parent
from .loss_model import LossModel

if TYPE_CHECKING:
    from ..material.material import Material
    from ..mesh.mesh_solution import MeshSolution
    from ..output.output import Output
    from ..scidatatool.data import Data
    from .loss import Loss


@dataclass(eq=False)
class LossModelSteinmetz(LossModel):
    """Steinmetz Loss Model Class

    Attributes
    ----------
    k_hy : float or None
        Hysteresis loss coefficient
        Unit: W/kg; Default: None
    k_ed : float or None
        Eddy current loss coefficient
        Unit: W/kg; Default: None
    alpha_f : float or None
        Hysteresis loss power coefficient for the frequency
        Default: None
    alpha_B : float or None
        Hysteresis loss power coefficient for the flux density magnitude
        Default: None
    is_stacking_factor : bool
        True to consider lamination stacking factor when calculating core losses
        Default: False
    """

    k_hy: float | None = field(default=None, metadata={"unit": "W/kg"})
    """Hysteresis loss coefficient"""
    k_ed: float | None = field(default=None, metadata={"unit": "W/kg"})
    """Eddy current loss coefficient"""
    alpha_f: float | None = None
    """Hysteresis loss power coefficient for the frequency"""
    alpha_B: float | None = None
    """Hysteresis loss power coefficient for the flux density magnitude"""
    is_stacking_factor: bool = False
    """True to consider lamination stacking factor when calculating core losses"""

    _package: ClassVar[str] = "Loss"
    """Name of the package of the legacy class module"""

    # Inlined from Methods.Loss.LossModelSteinmetz.comp_coeff
    def comp_coeff(self, material: Material) -> None:
        """Enables to compute the coefficients of the loss model with a curve fitting
        on loss data stored in the material (Store result in self.k_hy, self.k_ed, self.alpha_f, self.alpha_B)

        Parameters
        ----------
        self : LossModelSteinmetz
            A LossModelSteinmetz object
        material : Material
            A material object, corresponding to the material used in the electrical machine.
            This material object must contain loss data as an ImportMatrixVal object.
            This matrix must contain 3 rows, corresponding to the excitation frequency (Hz),
            the peak magnetic flux density (T), and the loss density (W/kg) in this order.
        """

        parameter_names = ["k_hy", "k_ed", "alpha_f", "alpha_B"]
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
        xdata: np.ndarray, k_hy: float, k_ed: float, alpha_f: float, alpha_B: float
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
        alpha_f : float
            hysteresis frequency power
        alpha_B : float
            hysteresis flux density amplitude exponent

        Returns
        -------
        loss : ndarray
            loss for each value of f and B in the input array
        """

        f = xdata[0]
        B = xdata[1]

        return k_hy * f**alpha_f * B**alpha_B + k_ed * (f * B) ** 2

    # Inlined from Methods.Loss.LossModelSteinmetz.comp_loss
    def comp_loss(
        self,
        meshsol: MeshSolution | None = None,
        loss: Loss | None = None,
        output: Output | None = None,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Calculate loss density in iron core given by group "stator core" or "rotor core"
        assuming power density is given by a Steinmetz model:

            Pcore = Ph + Pe = k_hy * f^alpha_f * B^self.alpha_B + k_ed * f^2 * B^2

        Parameters
        ----------
        self: LossModelSteinmetz
            a LossModelSteinmetz object
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
            raise Exception("Cannot calculate core losses if simu is not in an Output")

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
        if None in [
            self.k_hy,
            self.k_ed,
            self.alpha_f,
            self.alpha_B,
        ]:
            material = lamination.mat_type
            self.comp_coeff(material)

        # Get loss coefficients
        # The loss data are given in W/kg, but the loss density in pyleecan are computed in W/m^3
        k_hy = self.k_hy / Kf * rho
        k_ed = self.k_ed / Kf * rho
        alpha_f = self.alpha_f
        alpha_B = self.alpha_B

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

        if meshsol.group is None:
            raise FieldMissingError(
                "MeshSolution.group is None: the mesh solution has no element groups"
            )
        group_list = list(meshsol.group.keys())

        if self.group not in group_list:
            raise ValueError("Cannot calculate core losses for group=" + self.group)

        # Extract solution
        try:
            solution_B = meshsol["B"]
        except ValueError:
            raise ValueError("Cannot calculate core losses if B is not in meshsolution")

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

        # Compute magnetic flux density FFT
        Bfft = Bvect.get_xyz_along("freqs", "indice=" + str(Igrp), "z=mean")
        freqs = Bfft["freqs"]
        Bfft_magnitude = np.sqrt(
            np.abs(Bfft["comp_x"]) ** 2 + np.abs(Bfft["comp_y"]) ** 2
        )

        # Compute the loss density for each element and each frequency
        Pcore_density = k_ed * freqs[:, None] ** 2 * Bfft_magnitude**2
        Pcore_density += k_hy * freqs[:, None] ** alpha_f * Bfft_magnitude**alpha_B

        if is_change_Time:
            # Change periodicity back to original periodicity
            for comp in Bvect.components.values():
                comp.axes[0] = Time_orig

        # Get frequency orders
        n = freqs / felec

        # Integrate loss density over group volume to get polynomial coefficients
        coeff = Lst * per_a * np.matmul(Bfft_magnitude**2, Se)
        A = np.sum(k_ed * coeff * n**2)
        coeff = Lst * per_a * np.matmul(Bfft_magnitude**alpha_B, Se)
        B = np.sum(k_hy * coeff * n**alpha_f)
        self.coeff_dict = {"2": A, str(alpha_f): B}

        return Pcore_density, freqs

    # Inlined from Methods.Loss.LossModelSteinmetz.comp_loss_freq
    def comp_loss_freq(
        self, loss: Loss | None = None, output: Output | None = None
    ) -> tuple[np.ndarray, dict[str, np.ndarray], np.ndarray]:
        """Calculate loss density in iron core given by group "stator core" or "rotor core"
        assuming power density is given by a Steinmetz model depending on frequency:

            Pcore = Ph + Pe = k_hy * f^alpha_f * B^alpha_B + k_ed * f^2 * B^2

        Parameters
        ----------
        self: LossModelSteinmetz
            a LossModelSteinmetz object
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
        if None in [self.k_hy, self.k_ed, self.alpha_f, self.alpha_B]:
            material = lamination.mat_type
            self.comp_coeff(material)

        # Get loss coefficients
        # The loss data are given in W/kg, but the loss density in pyleecan are computed in W/m^3
        k_hy = self.k_hy * rho
        k_ed = self.k_ed * rho
        alpha_f = self.alpha_f
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
        Pcore_density_hys = (
            k_hy / Kf * freqs[:, None] ** alpha_f * Bfft_square ** (alpha_B / 2)
        )
        Pcore_density_edd = k_ed / Kf * freqs[:, None] ** 2 * Bfft_square

        # Sum all core losses contribution and sum over frequencies to get average loss density value per element
        Pcore_density = np.sum(
            Pcore_density_hys + Pcore_density_edd, axis=0, keepdims=True
        )

        # Integrate volumic density over core volume to get loss value per contribution
        Pcore_hys = Lst * per_a * np.matmul(Pcore_density_hys, Se)
        Pcore_edd = Lst * per_a * np.matmul(Pcore_density_edd, Se)

        # Sum all core losses contributions
        Pcore = Pcore_hys + Pcore_edd

        # Store losses contribution for each frequency in dict
        Pcore_dict = {
            self.group + " losses": Pcore,
            self.group + " hysteresis": Pcore_hys,
            self.group + " eddy current": Pcore_edd,
        }

        # Get hysteresis loss polynomial coefficient
        A = np.sum(Pcore_hys) / felec**alpha_f

        # Get eddy-current loss polynomial coefficient
        B = np.sum(Pcore_edd) / felec**2

        # Store polynom coefficients in dict
        self.coeff_dict = {str(float(alpha_f)): A, "2.0": B}

        return Pcore_density, Pcore_dict, freqs

    # Inlined from Methods.Loss.LossModelSteinmetz.comp_loss_time
    def comp_loss_time(
        self,
        axes_dict: dict[str, Data],
        is_mirror: bool,
        loss: Loss | None = None,
        output: Output | None = None,
    ) -> tuple[np.ndarray, dict[str, np.ndarray]]:
        """Calculate loss density over time in iron core given by group "stator core" or "rotor core"
        assuming power density is given by a Steinmetz model

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
        if None in [self.k_hy, self.k_ed, self.alpha_f, self.alpha_B]:
            material = lamination.mat_type
            self.comp_coeff(material)

        # Get loss coefficients
        # The loss data are given in W/kg, but the loss density in pyleecan are computed in W/m^3
        k_hy = self.k_hy * rho  # Not used in Bertotti time-dependant model
        k_ed = self.k_ed * rho

        # B exponent in hysteresis loss model
        alpha_f = self.alpha_f
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
        Pcore_density_hys = (
            np.abs(H["comp_x"] * dB_dt["comp_x"]) ** (2 / alpha_B)
            + np.abs(H["comp_y"] * dB_dt["comp_y"]) ** (2 / alpha_B)
        ) ** (alpha_B / 2) / Kf

        Pcore_density_edd = (
            1
            / (2 * np.pi**2)
            * k_ed
            / Kf
            * (dB_dt["comp_x"] ** 2 + dB_dt["comp_y"] ** 2)
        )

        # Integrate volumic density over core volume
        Pcore_hys = Lst * per_a * np.matmul(Pcore_density_hys, Se)
        Pcore_edd = Lst * per_a * np.matmul(Pcore_density_edd, Se)

        # Sum all core losses contribution
        Pcore = Pcore_hys + Pcore_edd

        Pcore_density = Pcore_density_hys + Pcore_density_edd

        Pcore_dict = {
            self.group + " losses": Pcore,
            self.group + " hysteresis": Pcore_hys,
            self.group + " eddy current": Pcore_edd,
        }

        # Get fundamental frequency
        felec = output.elec.OP.get_felec()

        # Save coefficients to rebuild losses for same (Id,Iq) but at a different speed
        A = Pcore_hys.mean() / felec**alpha_f
        B = Pcore_edd.mean() / felec**2
        self.coeff_dict = {"2": A, str(alpha_f): B}

        return Pcore_density, Pcore_dict

    # Inlined from Methods.Loss.LossModelSteinmetz.plot_fitting
    def plot_fitting(self, material: Material, is_show_fig: bool = True) -> None:
        """Plot the fitted loss curves (from fitted coefficients k_hy, k_ed, k_ex, beta) and the loss data stored in the material

        Parameters
        ----------
        self : LossModelSteinmetz
            A loss model to compute Steinmetz losses
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
        fig = plt.figure("Curve fitting for Steinmetz iron loss model", figsize=(14, 7))
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
                x_check, self.k_hy, self.k_ed, self.alpha_f, self.alpha_B
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
            f"Curve fitting for the Steinmetz iron loss model of the {material.name} material"
        )

        txt = " $P_{{loss}}=k_{{hy}} f^{\\alpha} B^{\\beta} + k_{{ed}} (f B)^2 $\n"

        txt += "where:\n"
        txt += "$k_{{hy}}$ = " + format(self.k_hy, ".5E") + "\n"
        txt += "$k_{{ed}}$ = " + format(self.k_ed, ".5E") + "\n"
        txt += "$\\alpha_f$ = " + format(self.alpha_f, ".5E") + "\n"
        txt += "$\\alpha_B$ = " + format(self.alpha_B, ".5E") + "\n"

        fig.text(0.02, 0.5, txt, fontsize=12)
        plt.subplots_adjust(left=0.26)
        plt.legend()
        if is_show_fig:
            plt.show()
