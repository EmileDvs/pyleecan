# -*- coding: utf-8 -*-
# File generated according to Generator/ClassesRef/Loss/LossModelBertotti.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Loss/LossModelBertotti
"""

from os import linesep
from sys import getsizeof
from logging import getLogger
from pyleecan.Classes._check import check_var, raise_
from pyleecan.Functions.get_logger import get_logger
from pyleecan.Functions.save import save
from pyleecan.Functions.load import load_init_dict
from pyleecan.Functions.Load.import_class import import_class
from copy import deepcopy
from pyleecan.Classes.LossModel import LossModel

# Import all class method
# Try/catch to remove unnecessary dependencies in unused method
import matplotlib.pyplot as plt, numpy as np
from scipy.optimize import curve_fit
from itertools import groupby


from pyleecan.Classes._check import InitUnKnowClassError


class LossModelBertotti(LossModel):
    """Bertotti Loss Model Class"""

    VERSION = 1

    # cf Methods.Loss.LossModelBertotti.comp_coeff
    def comp_coeff(self, material):
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

                def comp_loss(xdata, k_hy, k_ed, k_ex):
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

                    Returns
                    -------
                    ndarray
                        loss for each value of f and B in the input array
                    """
                    B = xdata
                    return k_hy * f * B**2 + k_ed * (f * B) ** 2 + k_ex * (f * B) ** 1.5

            else:
                is_frequency_dependant = True
                returned_xdata = np.array([f, B])

                def comp_loss(xdata, k_hy, k_ed, k_ex):
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

                    Returns
                    -------
                    ndarray
                        loss for each value of f and B in the input array
                    """
                    f = xdata[0]
                    B = xdata[1]
                    return k_hy * f * B**2 + k_ed * (f * B) ** 2 + k_ex * (f * B) ** 1.5

            return comp_loss, returned_xdata, is_frequency_dependant

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

        loss_data = material.mag.LossData.get_data()
        f = loss_data[0]
        B = loss_data[1]
        loss = loss_data[2]
        comp_loss, xdata, is_frequency_dependant = test_frequency_dependance(f, B)

        ydata = np.array(loss)
        popt, _ = curve_fit(
            comp_loss, xdata, ydata, bounds=([0, 0, 0], [np.inf, np.inf, np.inf])
        )

        if self.is_show_fig:
            groups, uniquekeys = group_by_frequency(loss_data)
            fig = plt.figure("Curve fitting for Iron losses", figsize=(14, 7))
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
            txt = " $P_{{loss}}=k_{{hy}} f B^2 + k_{{ed}} (f B)^2 + k_{{ex}} (f B)^{{1.5}}$\n"
            txt += "where:\n"
            txt += "$k_{{hy}}$ = " + format(popt[0], ".5E") + "\n"
            txt += "$k_{{ed}}$ = " + format(popt[1], ".5E") + "\n"
            txt += "$k_{{ex}}$ = " + format(popt[2], ".5E") + "\n"
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
            plt.show()

        self.k_hy = popt[0]  # Hysteresis loss coefficient [W/kg]
        self.k_ed = popt[1]  # Eddy current loss coefficient [W/kg]
        self.k_ex = popt[2]  # Excess loss coefficient [W/kg]

    # cf Methods.Loss.LossModelBertotti.comp_loss
    def comp_loss(self):
        """Calculate loss density in iron core given by group "stator core" or "rotor core"
        assuming power density is given by a Bertotti model

            Pcore = k_hy * f * B^2 + k_ed * (f B)^2 + k_ex * (f B)^1.5

        Parameters
        ----------
        self: LossModelBertotti
            a LossModelBertotti object

        Returns
        -------
        Pcore_density : ndarray
            Core loss density function of frequency and elements [W/m3]
        freqs: ndarray
            frequency vector [Hz]
        """

        if self.parent.parent.parent is None:
            raise ValueError("Cannot calculate core losses if simu is not in an Output")
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
            self.k_ex,
        ]:
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

        if output.mag.meshsolution is None:
            raise ValueError(
                "Cannot calculate core losses if OutMag.meshsolution is None"
            )
        else:
            meshsol = output.mag.meshsolution

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

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
        k_hy=None,
        k_ed=None,
        k_ex=None,
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
            if "k_hy" in list(init_dict.keys()):
                k_hy = init_dict["k_hy"]
            if "k_ed" in list(init_dict.keys()):
                k_ed = init_dict["k_ed"]
            if "k_ex" in list(init_dict.keys()):
                k_ex = init_dict["k_ex"]
            if "name" in list(init_dict.keys()):
                name = init_dict["name"]
            if "group" in list(init_dict.keys()):
                group = init_dict["group"]
            if "is_show_fig" in list(init_dict.keys()):
                is_show_fig = init_dict["is_show_fig"]
            if "coeff_dict" in list(init_dict.keys()):
                coeff_dict = init_dict["coeff_dict"]
        # Set the properties (value check and convertion are done in setter)
        self.k_hy = k_hy
        self.k_ed = k_ed
        self.k_ex = k_ex
        # Call LossModel init
        super(LossModelBertotti, self).__init__(
            name=name, group=group, is_show_fig=is_show_fig, coeff_dict=coeff_dict
        )
        # The class is frozen (in LossModel init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        LossModelBertotti_str = ""
        # Get the properties inherited from LossModel
        LossModelBertotti_str += super(LossModelBertotti, self).__str__()
        LossModelBertotti_str += "k_hy = " + str(self.k_hy) + linesep
        LossModelBertotti_str += "k_ed = " + str(self.k_ed) + linesep
        LossModelBertotti_str += "k_ex = " + str(self.k_ex) + linesep
        return LossModelBertotti_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from LossModel
        if not super(LossModelBertotti, self).__eq__(other):
            return False
        if other.k_hy != self.k_hy:
            return False
        if other.k_ed != self.k_ed:
            return False
        if other.k_ex != self.k_ex:
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
            super(LossModelBertotti, self).compare(
                other, name=name, ignore_list=ignore_list, is_add_value=is_add_value
            )
        )
        if (
            other._k_hy is not None
            and self._k_hy is not None
            and np.isnan(other._k_hy)
            and np.isnan(self._k_hy)
        ):
            pass
        elif other._k_hy != self._k_hy:
            if is_add_value:
                val_str = (
                    " (self=" + str(self._k_hy) + ", other=" + str(other._k_hy) + ")"
                )
                diff_list.append(name + ".k_hy" + val_str)
            else:
                diff_list.append(name + ".k_hy")
        if (
            other._k_ed is not None
            and self._k_ed is not None
            and np.isnan(other._k_ed)
            and np.isnan(self._k_ed)
        ):
            pass
        elif other._k_ed != self._k_ed:
            if is_add_value:
                val_str = (
                    " (self=" + str(self._k_ed) + ", other=" + str(other._k_ed) + ")"
                )
                diff_list.append(name + ".k_ed" + val_str)
            else:
                diff_list.append(name + ".k_ed")
        if (
            other._k_ex is not None
            and self._k_ex is not None
            and np.isnan(other._k_ex)
            and np.isnan(self._k_ex)
        ):
            pass
        elif other._k_ex != self._k_ex:
            if is_add_value:
                val_str = (
                    " (self=" + str(self._k_ex) + ", other=" + str(other._k_ex) + ")"
                )
                diff_list.append(name + ".k_ex" + val_str)
            else:
                diff_list.append(name + ".k_ex")
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object

        # Get size of the properties inherited from LossModel
        S += super(LossModelBertotti, self).__sizeof__()
        S += getsizeof(self.k_hy)
        S += getsizeof(self.k_ed)
        S += getsizeof(self.k_ex)
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
        LossModelBertotti_dict = super(LossModelBertotti, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs,
        )
        LossModelBertotti_dict["k_hy"] = self.k_hy
        LossModelBertotti_dict["k_ed"] = self.k_ed
        LossModelBertotti_dict["k_ex"] = self.k_ex
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        LossModelBertotti_dict["__class__"] = "LossModelBertotti"
        return LossModelBertotti_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        k_hy_val = self.k_hy
        k_ed_val = self.k_ed
        k_ex_val = self.k_ex
        name_val = self.name
        group_val = self.group
        is_show_fig_val = self.is_show_fig
        if self.coeff_dict is None:
            coeff_dict_val = None
        else:
            coeff_dict_val = self.coeff_dict.copy()
        # Creates new object of the same type with the copied properties
        obj_copy = type(self)(
            k_hy=k_hy_val,
            k_ed=k_ed_val,
            k_ex=k_ex_val,
            name=name_val,
            group=group_val,
            is_show_fig=is_show_fig_val,
            coeff_dict=coeff_dict_val,
        )
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        self.k_hy = None
        self.k_ed = None
        self.k_ex = None
        # Set to None the properties inherited from LossModel
        super(LossModelBertotti, self)._set_None()

    def _get_k_hy(self):
        """getter of k_hy"""
        return self._k_hy

    def _set_k_hy(self, value):
        """setter of k_hy"""
        check_var("k_hy", value, "float")
        self._k_hy = value

    k_hy = property(
        fget=_get_k_hy,
        fset=_set_k_hy,
        doc="""Hysteresis loss coefficient

        :Type: float
        """,
    )

    def _get_k_ed(self):
        """getter of k_ed"""
        return self._k_ed

    def _set_k_ed(self, value):
        """setter of k_ed"""
        check_var("k_ed", value, "float")
        self._k_ed = value

    k_ed = property(
        fget=_get_k_ed,
        fset=_set_k_ed,
        doc="""Eddy current loss coefficient

        :Type: float
        """,
    )

    def _get_k_ex(self):
        """getter of k_ex"""
        return self._k_ex

    def _set_k_ex(self, value):
        """setter of k_ex"""
        check_var("k_ex", value, "float")
        self._k_ex = value

    k_ex = property(
        fget=_get_k_ex,
        fset=_set_k_ex,
        doc="""Excess loss coefficient

        :Type: float
        """,
    )
