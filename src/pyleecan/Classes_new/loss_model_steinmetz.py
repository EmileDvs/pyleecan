# Experimental dataclass generated from Generator/ClassesRef/Loss/LossModelSteinmetz.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass
from itertools import groupby

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit

from .loss_model import LossModel


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
    """

    k_hy: float | None = None
    """Hysteresis loss coefficient"""
    k_ed: float | None = None
    """Eddy current loss coefficient"""
    alpha_f: float | None = None
    """Hysteresis loss power coefficient for the frequency"""
    alpha_B: float | None = None
    """Hysteresis loss power coefficient for the flux density magnitude"""

    # Inlined from Methods.Loss.LossModelSteinmetz.comp_coeff
    def comp_coeff(self, material):
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

        def group_by_frequency(loss_data):
            """This function enables to group the loss data (computed or experimental) by frequency, to plot the curve-fitting figure

            Parameters
            ----------
            loss_data : ndarray
                Array containing
                - f in the first line
                - B in the second line
                - loss value in the third line

            Returns
            -------
            tuple
                The first element is a list of ndarray with f in the first column (all the values are the same in each array), B in the
                second column and the loss value in the third one, for each frequency.
                The second element is the list of unique frequencies in the loss data.
            """
            groups = []
            uniquekeys = []
            loss_data_T = loss_data.T
            for k, g in groupby(loss_data_T, lambda x: x[0]):
                groups.append(list(g))  # Store group iterator as a list
                uniquekeys.append(k)
            return groups, uniquekeys

        def test_frequency_dependance(f, B):
            """Function that tests if the experimental data provides several values of f. If not, the comp_loss function
            is simplified to depend only on B.

            Parameters
            ----------
            f : ndarray
                array containing values of f
            B : ndarray
                array containing values of B

            Returns
            -------
            tuple
                The first element is the comp_loss function that will be used to compute the loss
                The second element is the input data that should be used to compute te losses
                The third element is e bolean telling whether the function depends on frequency or not
            """
            if np.all(f == f[0]):
                is_frequency_dependant = False
                f = f[0]
                returned_xdata = B

                def comp_loss(xdata, Ch, Ce, alpha_f, alpha_B):
                    """A function that compute the loss with respect to the maximum value and the frequency of the magnetic flux density

                    Parameters
                    ----------
                    xdata : ndarray
                        input array with the values of B
                    Ch : float
                        hysteresis loss coefficient
                    Ce : float
                        Eddy current loss coefficient
                    alpha_f : float
                        hysteresis frequency power
                    alpha_B : float
                        hysteresis flux density amplitude power

                    Returns
                    -------
                    ndarray
                        loss for each value of f and B in the input array
                    """
                    B = xdata
                    return Ch * f**alpha_f * B**alpha_B + Ce * (f * B) ** 2

            else:
                is_frequency_dependant = True
                returned_xdata = np.array([f, B])

                def comp_loss(xdata, Ch, Ce, alpha_f, alpha_B):
                    """A function that compute the loss with respect to the maximum value and the frequency of the magnetic flux density

                    Parameters
                    ----------
                    xdata : ndarray
                        input matrix with f in the first line and B in the second line
                    Ch : float
                        hysteresis loss coefficient
                    Ce : float
                        Eddy current loss coefficient
                    alpha_f : float
                        hysteresis frequency power
                    alpha_B : float
                        hysteresis flux density amplitude power

                    Returns
                    -------
                    ndarray
                        loss for each value of f and B in the input array
                    """
                    f = xdata[0]
                    B = xdata[1]
                    return Ch * f**alpha_f * B**alpha_B + Ce * (f * B) ** 2

            return comp_loss, returned_xdata, is_frequency_dependant

        loss_data = material.mag.LossData.get_data()
        f = loss_data[0]
        B = loss_data[1]
        loss = loss_data[2]
        comp_loss, xdata, is_frequency_dependant = test_frequency_dependance(f, B)

        ydata = np.array(loss)
        popt, _ = curve_fit(
            comp_loss,
            xdata,
            ydata,
            bounds=([0, 0, 0, 0], [np.inf, np.inf, np.inf, np.inf]),
        )

        if self.is_show_fig:
            groups, uniquekeys = group_by_frequency(loss_data)
            fig = plt.figure("Curve fitting for iron losses", figsize=(14, 7))
            B_check = np.linspace(0, 2, 1000)
            ax = plt.gca()
            R_list = []
            for index, key in enumerate(uniquekeys):
                if is_frequency_dependant:
                    f_check = np.ones((1000,)) * key
                    x_check = np.array([f_check, B_check])
                else:
                    x_check = B_check
                values = np.array(groups[index])
                B_experimental = values[:, 1]
                loss_experimental = values[:, 2]
                x_experimental = values[:, :2].T
                fitted_loss = comp_loss(x_experimental, *popt)
                R_list.append(
                    (key, (np.corrcoef(fitted_loss, loss_experimental)[0, 1]) ** 2)
                )
                color = next(ax._get_lines.prop_cycler)["color"]
                plt.plot(
                    B_experimental,
                    loss_experimental,
                    color=color,
                    label=f"measurements with f={key}Hz",
                    marker="o",
                )
                plt.plot(
                    B_check,
                    comp_loss(x_check, *popt),
                    color=color,
                    linestyle="dashed",
                    label=f"fitting with f={key}Hz",
                )
            plt.xlabel("Peak magnetic flux density (T)")
            plt.ylabel("Iron loss (W/kg)")
            plt.title(
                "Curve fitting for the iron loss of the {} material".format(
                    material.name
                )
            )
            txt = "$P_{{loss}}=k_{{hy}} f^{{\\alpha_f}} B^{{\\alpha_B}} + k_{{ed}} (fB)^2$\n"
            txt += "where:\n"
            txt += "$k_{{hy}}$ = " + format(popt[0], ".5E") + "\n"
            txt += "$k_{{ed}}$ = " + format(popt[1], ".5E") + "\n"
            txt += "$\\alpha_f$ = " + format(popt[2], ".5E") + "\n"
            txt += "$\\alpha_B$ = " + format(popt[3], ".5E") + "\n"
            fig.text(0.02, 0.5, txt, fontsize=12)
            plt.subplots_adjust(left=0.23)
            plt.legend()
            plt.show()

        self.k_hy = popt[0]  # Hysteresis loss coefficient [W/kg]
        self.k_ed = popt[1]  # Eddy current loss coefficient [W/kg]
        self.alpha_f = popt[2]  # Hysteresis loss power coefficient for the frequency
        # Hysteresis loss power coefficient for the flux density magnitude
        self.alpha_B = popt[3]

    # Inlined from Methods.Loss.LossModelSteinmetz.comp_loss
    def comp_loss(self):
        """Calculate loss density in iron core given by group "stator core" or "rotor core"
        assuming power density is given by a Steinmetz model:

            Pcore = Ph + Pe = k_hy * f^alpha_f * B^self.alpha_B + k_ed * f^2 * B^2

        Parameters
        ----------
        self: LossModelSteinmetz
            a LossModelSteinmetz object

        Returns
        -------
        Pcore_density : ndarray
            Core loss density function of frequency and elements [W/m3]
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

        if output.mag.meshsolution is None:
            raise ValueError(
                "Cannot calculate core losses if OutMag.meshsolution is None"
            )
        else:
            meshsol = output.mag.meshsolution

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
