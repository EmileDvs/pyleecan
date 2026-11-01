# -*- coding: utf-8 -*-
# File generated according to Generator/ClassesRef/Loss/LossModelSteinmetz.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Loss/LossModelSteinmetz
"""

from os import linesep
from sys import getsizeof
from logging import getLogger
from ._check import check_var, raise_
from ..Functions.get_logger import get_logger
from ..Functions.save import save
from ..Functions.load import load_init_dict
from ..Functions.Load.import_class import import_class
from copy import deepcopy
from .LossModel import LossModel

# Import all class method
# Try/catch to remove unnecessary dependencies in unused method
import matplotlib.pyplot as plt, numpy as np
from scipy.optimize import curve_fit
from itertools import groupby
from numpy import abs as np_abs, matmul, sqrt as np_sqrt, sum as np_sum

from numpy import isnan
from ._check import InitUnKnowClassError


class LossModelSteinmetz(LossModel):
    """Steinmetz Loss Model Class"""

    VERSION = 1

    # cf Methods.Loss.LossModelSteinmetz.comp_coeff
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

    # cf Methods.Loss.LossModelSteinmetz.comp_loss
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
        Bfft_magnitude = np_sqrt(
            np_abs(Bfft["comp_x"]) ** 2 + np_abs(Bfft["comp_y"]) ** 2
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
        coeff = Lst * per_a * matmul(Bfft_magnitude**2, Se)
        A = np_sum(k_ed * coeff * n**2)
        coeff = Lst * per_a * matmul(Bfft_magnitude**alpha_B, Se)
        B = np_sum(k_hy * coeff * n**alpha_f)
        self.coeff_dict = {"2": A, str(alpha_f): B}

        return Pcore_density, freqs

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
        k_hy=None,
        k_ed=None,
        alpha_f=None,
        alpha_B=None,
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
            if "alpha_f" in list(init_dict.keys()):
                alpha_f = init_dict["alpha_f"]
            if "alpha_B" in list(init_dict.keys()):
                alpha_B = init_dict["alpha_B"]
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
        self.alpha_f = alpha_f
        self.alpha_B = alpha_B
        # Call LossModel init
        super(LossModelSteinmetz, self).__init__(
            name=name, group=group, is_show_fig=is_show_fig, coeff_dict=coeff_dict
        )
        # The class is frozen (in LossModel init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        LossModelSteinmetz_str = ""
        # Get the properties inherited from LossModel
        LossModelSteinmetz_str += super(LossModelSteinmetz, self).__str__()
        LossModelSteinmetz_str += "k_hy = " + str(self.k_hy) + linesep
        LossModelSteinmetz_str += "k_ed = " + str(self.k_ed) + linesep
        LossModelSteinmetz_str += "alpha_f = " + str(self.alpha_f) + linesep
        LossModelSteinmetz_str += "alpha_B = " + str(self.alpha_B) + linesep
        return LossModelSteinmetz_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from LossModel
        if not super(LossModelSteinmetz, self).__eq__(other):
            return False
        if other.k_hy != self.k_hy:
            return False
        if other.k_ed != self.k_ed:
            return False
        if other.alpha_f != self.alpha_f:
            return False
        if other.alpha_B != self.alpha_B:
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
            super(LossModelSteinmetz, self).compare(
                other, name=name, ignore_list=ignore_list, is_add_value=is_add_value
            )
        )
        if (
            other._k_hy is not None
            and self._k_hy is not None
            and isnan(other._k_hy)
            and isnan(self._k_hy)
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
            and isnan(other._k_ed)
            and isnan(self._k_ed)
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
            other._alpha_f is not None
            and self._alpha_f is not None
            and isnan(other._alpha_f)
            and isnan(self._alpha_f)
        ):
            pass
        elif other._alpha_f != self._alpha_f:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._alpha_f)
                    + ", other="
                    + str(other._alpha_f)
                    + ")"
                )
                diff_list.append(name + ".alpha_f" + val_str)
            else:
                diff_list.append(name + ".alpha_f")
        if (
            other._alpha_B is not None
            and self._alpha_B is not None
            and isnan(other._alpha_B)
            and isnan(self._alpha_B)
        ):
            pass
        elif other._alpha_B != self._alpha_B:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._alpha_B)
                    + ", other="
                    + str(other._alpha_B)
                    + ")"
                )
                diff_list.append(name + ".alpha_B" + val_str)
            else:
                diff_list.append(name + ".alpha_B")
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object

        # Get size of the properties inherited from LossModel
        S += super(LossModelSteinmetz, self).__sizeof__()
        S += getsizeof(self.k_hy)
        S += getsizeof(self.k_ed)
        S += getsizeof(self.alpha_f)
        S += getsizeof(self.alpha_B)
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
        LossModelSteinmetz_dict = super(LossModelSteinmetz, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs,
        )
        LossModelSteinmetz_dict["k_hy"] = self.k_hy
        LossModelSteinmetz_dict["k_ed"] = self.k_ed
        LossModelSteinmetz_dict["alpha_f"] = self.alpha_f
        LossModelSteinmetz_dict["alpha_B"] = self.alpha_B
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        LossModelSteinmetz_dict["__class__"] = "LossModelSteinmetz"
        return LossModelSteinmetz_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        k_hy_val = self.k_hy
        k_ed_val = self.k_ed
        alpha_f_val = self.alpha_f
        alpha_B_val = self.alpha_B
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
            alpha_f=alpha_f_val,
            alpha_B=alpha_B_val,
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
        self.alpha_f = None
        self.alpha_B = None
        # Set to None the properties inherited from LossModel
        super(LossModelSteinmetz, self)._set_None()

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

    def _get_alpha_f(self):
        """getter of alpha_f"""
        return self._alpha_f

    def _set_alpha_f(self, value):
        """setter of alpha_f"""
        check_var("alpha_f", value, "float")
        self._alpha_f = value

    alpha_f = property(
        fget=_get_alpha_f,
        fset=_set_alpha_f,
        doc="""Hysteresis loss power coefficient for the frequency

        :Type: float
        """,
    )

    def _get_alpha_B(self):
        """getter of alpha_B"""
        return self._alpha_B

    def _set_alpha_B(self, value):
        """setter of alpha_B"""
        check_var("alpha_B", value, "float")
        self._alpha_B = value

    alpha_B = property(
        fget=_get_alpha_B,
        fset=_set_alpha_B,
        doc="""Hysteresis loss power coefficient for the flux density magnitude

        :Type: float
        """,
    )
