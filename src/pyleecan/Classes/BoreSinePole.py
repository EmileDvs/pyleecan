# -*- coding: utf-8 -*-
# File generated according to Generator/ClassesRef/Machine/BoreSinePole.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Machine/BoreSinePole
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
from pyleecan.Classes.Bore import Bore

# Import all class method
# Try/catch to remove unnecessary dependencies in unused method
from pyleecan.Classes.Segment import Segment
from pyleecan.Classes import ParentMissingError
import numpy as np, matplotlib.pyplot as plt
from scipy.optimize import fmin
from pyleecan.Classes.Arc1 import Arc1
from pyleecan.Classes.Lamination import Lamination
from pyleecan.definitions import config_dict
from pyleecan.Functions.Plot import (
    ARROW_COLOR,
    ARROW_WIDTH,
    MAIN_LINE_COLOR,
    MAIN_LINE_STYLE,
    MAIN_LINE_WIDTH,
    SC_FONT_SIZE,
)


from pyleecan.Classes._check import InitUnKnowClassError


class BoreSinePole(Bore):
    """Class for Sine Field Pole Bore shape adapted from 'Muller, Germar, et al. Berechnung Elektrischer Maschinen. Hoboken, NJ, United States, Wiley, 2008.'"""

    VERSION = 1
    MAGNET_COLOR = config_dict["PLOT"]["COLOR_DICT"]["MAGNET_COLOR"]

    # cf Methods.Machine.BoreSinePole.comp_periodicity_spatial
    def comp_periodicity_spatial(self):
        """Compute the periodicity factor of the Bore

        Parameters
        ----------
        self : BoreSinePole
            A BoreSinePole object

        Returns
        -------
        per_a : int
            Number of spatial periodicities of the bore
        is_antiper_a : bool
            True if an spatial anti-periodicity is possible after the periodicities
        """

        return self.N, False

    # cf Methods.Machine.BoreSinePole.get_bore_line
    def get_bore_line(self, prop_dict=None, *, NN=30):
        """Return the bore line description
        adapted sine field pole geometry from the text book:
        "Müller, Germar, et al. Berechnung Elektrischer Maschinen. Hoboken, NJ, United States, Wiley, 2008."
        ("Calculation of electric machines")

        Parameters
        ----------
        self : BoreSinePole
            A BoreSinePole object
        prop_dict : dict
            Property dictionary to apply on the lines

        Returns
        -------
        bore_list : list
            List of bore lines
        """

        if self.parent is not None:
            Rbo = self.parent.get_Rbo()
        else:
            raise ParentMissingError("Error: The slot is not inside a Lamination")

        logger = self.get_logger()

        # Compute the shape
        alpha1 = np.pi / self.N  # Half bore pitch [rad]

        # Checking max width and W0
        w_max = self._get_pole_width_max(self)  # [m]
        if self.W0 is not None and self.W0 < w_max:
            w_max = self.W0
        elif self.W0 is not None and self.W0 > w_max:
            logger.warning("Enforcing permissible pole width (W0).")

        phi_max = self._get_phi(self, w_max)
        phi = np.linspace(-phi_max, phi_max, 2 * NN + 1)

        Zedge = self.get_pole_shape(-phi_max)
        xedge = (Zedge * np.exp(1j * alpha1)).real
        Rq = Rbo + self.delta_d - self.delta_q

        # Create the first pole bore line
        Z = [self.get_pole_shape(p) for p in phi]

        if self.delta_q is not None and Rq < xedge:
            line = Segment(
                Zedge * np.exp(1j * alpha1), 1j * Zedge.imag * np.exp(1j * alpha1)
            )
            inter = line.intersect_line(Rq, Rq + 1j * Rq)
            if len(inter) != 1:
                raise ()  # TODO

            if inter[0].imag <= 0:
                inter = line.intersect_line(0, Rq)
                if len(inter) != 1:
                    raise ()  # TODO

                logger.warning("Enforcing permissible q axis air gap (delta_q).")
                Z.insert(0, inter[0] * np.exp(-1j * alpha1))
                Z.append(Z[0].conjugate())

            else:
                Z.insert(0, inter[0] * np.exp(-1j * alpha1))
                Z.append(Z[0].conjugate())
                Z.insert(0, Rq * np.exp(-1j * alpha1))
                Z.append(Z[0].conjugate())

        else:
            Z.append(xedge * np.exp(1j * alpha1))
            Z.insert(0, Z[-1].conjugate())

        # Create the lines
        bore_list = list()
        for ii in range(self.N):
            for jj in range(len(Z) - 1):
                bore_list.append(
                    Segment(
                        Z[jj] * np.exp(1j * (2 * alpha1 * (ii - 1 / 2) + self.alpha)),
                        Z[jj + 1]
                        * np.exp(1j * (2 * alpha1 * (ii - 1 / 2) + self.alpha)),
                        prop_dict=prop_dict,
                    )
                )

        return bore_list

    @staticmethod
    def _get_phi(obj, w):
        """Return the angle of the pole width

        Parameters
        ----------
        obj : BoreSinePole
            a BoreSinePole object

        Returns
        -------
        phi : float
            angle of the pole width [rad]
        """
        phi_max = BoreSinePole._get_phi_max(obj)
        phi = fmin(
            lambda x: abs(obj.get_pole_shape(x).imag - w / 2) + max(x - phi_max, 0),
            0,
            disp=False,
        )[0]
        return phi

    @staticmethod
    def _get_phi_max(obj):
        """ "Internal method to get max. pole angle."""
        phi_max = fmin(lambda x: -obj.get_pole_shape(x).imag, 0, disp=False)[0]
        return min(np.pi / 2, phi_max)

    @staticmethod
    def _get_pole_width_max(obj):
        """Return the max. pole width and the angle of the max. pole width

        Parameters
        ----------
        obj : BoreSinePole
            a BoreSinePole object

        Returns
        -------
        w_max : float
            max. pole width [m]
        """
        phi_max = BoreSinePole._get_phi_max(obj)
        w_max = 2 * obj.get_pole_shape(phi_max).imag

        return w_max

    # cf Methods.Machine.BoreSinePole.get_pole_shape
    def get_pole_shape(self, phi):
        """Return the complex coordinates of the point at phi

        Parameters
        ----------
        self : BoreSinePole
            A BoreSinePole object
        phi : float
            Angle where to compute the point [rad]

        Returns
        -------
        Z : complex
            Coordinates of the requested point
        """

        if self.parent is not None:
            Rbo = self.parent.get_Rbo()
        else:
            raise ParentMissingError("Error: The slot is not inside a Lamination")

        # limit phi to valid values
        phi_max = np.arccos(self.delta_d / (self.delta_d + Rbo)) / self.k
        phi = max(-phi_max, phi)
        phi = min(phi_max, phi)

        # compute the point on the bore radius arc
        delta = self.delta_d / np.cos(phi * self.k)
        r = Rbo + self.delta_d - delta
        x = r * np.cos(2 * phi / self.N)
        y = r * np.sin(2 * phi / self.N)

        return x + 1j * y

    # cf Methods.Machine.BoreSinePole.plot_schematics
    def plot_schematics(
        self,
        is_default=False,
        is_add_schematics=True,
        is_add_main_line=True,
        save_path=None,
        is_show_fig=True,
        fig=None,
        ax=None,
    ):
        """Plot the schematics of the slot

        Parameters
        ----------
        self : BoreSinePole
            A BoreSinePole object
        is_default : bool
            True: plot default schematics, else use current slot values
        is_add_schematics : bool
            True to display the schematics information (W0, H0...)
        is_add_main_line : bool
            True to display "main lines" (slot opening and 0x axis)
        save_path : str
            full path including folder, name and extension of the file to save if save_path is not None
        is_show_fig : bool
            To call show at the end of the method
        fig : Matplotlib.figure.Figure
            existing figure to use if None create a new one
        ax : Matplotlib.axes.Axes object
            Axis on which to plot the data

        Returns
        -------
        fig : Matplotlib.figure.Figure
            Figure containing the schematics
        ax : Matplotlib.axes.Axes object
            Axis containing the schematics
        """

        # Use some default parameter
        if is_default:
            bore = type(self)(N=8, delta_d=10e-3, delta_q=50e-3, W0=165e-3, alpha=0)
            lam = Lamination(
                Rint=0.135, Rext=0.3, is_internal=True, is_stator=False, bore=bore
            )
            return bore.plot_schematics(
                is_default=False,
                is_add_schematics=is_add_schematics,
                is_add_main_line=is_add_main_line,
                save_path=save_path,
                is_show_fig=is_show_fig,
                fig=fig,
                ax=ax,
            )
        else:
            # Getting the main plot
            if self.parent is None:
                raise ParentMissingError("Error: The bore is not inside a Lamination")
            lam = self.parent
            fig, ax = lam.plot(is_show_fig=False, fig=fig, ax=ax)

            # Comp point coordinates
            lines = self.get_bore_line()
            Zq1 = lines[0].get_end()
            Zq2 = lines[-1].get_begin()
            Rbo = self.parent.get_Rbo()
            alpha = np.pi / self.N
            # H = self.Rarc / 8  # Small distance for label placement

            # Adding schematics
            if is_add_schematics:
                # delta_q
                p1 = Rbo + self.delta_d - self.delta_q
                p2 = Rbo + self.delta_d
                line = Segment(p1 * np.exp(2j * alpha), p2 * np.exp(2j * alpha))
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="delta_q",
                    offset_label=self.delta_q / 2,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # W0
                line = Segment(
                    Zq1 * np.exp(2 * 1j * alpha), Zq2 * np.exp(4 * 1j * alpha)
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="W0",
                    offset_label=0,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # Rbo + delta_d
                line = Segment(0, Rbo + self.delta_d)
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="Rbo + delta_d",
                    offset_label=-Rbo / 4,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )

            if is_add_main_line:
                plot_args = dict(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                # Ox axis
                # line = Segment(0, lam.Rext * 1.5)
                # line.plot(**plot_args)
                # Rarc
                # line = Segment(Zc, Z1)
                # line.plot(
                #     fig=fig,
                #     ax=ax,
                #     color=MAIN_LINE_COLOR,
                #     linestyle=MAIN_LINE_STYLE,
                #     linewidth=MAIN_LINE_WIDTH,
                # )
                # line = Segment(Zc, Z2)
                # line.plot(
                #     fig=fig,
                #     ax=ax,
                #     color=MAIN_LINE_COLOR,
                #     linestyle=MAIN_LINE_STYLE,
                #     linewidth=MAIN_LINE_WIDTH,
                # )
                # Machine center
                line = Segment(0, Rbo * np.exp(1j * alpha))
                line.plot(**plot_args)
                # Rbo circle arc
                Z1 = Rbo * np.exp(-1j * np.pi / 2)
                Z2 = Rbo * np.exp(1j * np.pi / 2)
                line = Arc1(begin=Z1, end=Z2, radius=Rbo, is_trigo_direction=True)
                line.plot(**plot_args)
                line = Arc1(begin=Z2, end=Z1, radius=Rbo, is_trigo_direction=True)
                line.plot(**plot_args)
                # Rbo + delta_d circle arc
                R = Rbo + self.delta_d
                Z1 = R * np.exp(-1j * np.pi / 2)
                Z2 = R * np.exp(1j * np.pi / 2)
                line = Arc1(begin=Z1, end=Z2, radius=R, is_trigo_direction=True)
                line.plot(**plot_args)
                line = Arc1(begin=Z2, end=Z1, radius=R, is_trigo_direction=True)
                line.plot(**plot_args)

            # Zooming and cleaning

            ax.axis("equal")
            ax.set_xlim(0, Rbo)
            ax.set_ylim(-Rbo / 10, Rbo * 1.1)
            manager = plt.get_current_fig_manager()
            if manager is not None:
                manager.set_window_title(type(self).__name__ + " Schematics")
            ax.set_title("")
            ax.get_legend().remove()
            ax.set_axis_off()

            # Save / Show
            if save_path is not None:
                fig.savefig(save_path)
                plt.close(fig=fig)

            if is_show_fig:
                fig.show()
            return fig, ax

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
        N=8,
        k=1,
        delta_d=0.001,
        delta_q=None,
        W0=None,
        type_merge_slot=1,
        alpha=0,
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
            if "N" in list(init_dict.keys()):
                N = init_dict["N"]
            if "k" in list(init_dict.keys()):
                k = init_dict["k"]
            if "delta_d" in list(init_dict.keys()):
                delta_d = init_dict["delta_d"]
            if "delta_q" in list(init_dict.keys()):
                delta_q = init_dict["delta_q"]
            if "W0" in list(init_dict.keys()):
                W0 = init_dict["W0"]
            if "type_merge_slot" in list(init_dict.keys()):
                type_merge_slot = init_dict["type_merge_slot"]
            if "alpha" in list(init_dict.keys()):
                alpha = init_dict["alpha"]
        # Set the properties (value check and convertion are done in setter)
        self.N = N
        self.k = k
        self.delta_d = delta_d
        self.delta_q = delta_q
        self.W0 = W0
        # Call Bore init
        super(BoreSinePole, self).__init__(type_merge_slot=type_merge_slot, alpha=alpha)
        # The class is frozen (in Bore init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        BoreSinePole_str = ""
        # Get the properties inherited from Bore
        BoreSinePole_str += super(BoreSinePole, self).__str__()
        BoreSinePole_str += "N = " + str(self.N) + linesep
        BoreSinePole_str += "k = " + str(self.k) + linesep
        BoreSinePole_str += "delta_d = " + str(self.delta_d) + linesep
        BoreSinePole_str += "delta_q = " + str(self.delta_q) + linesep
        BoreSinePole_str += "W0 = " + str(self.W0) + linesep
        return BoreSinePole_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from Bore
        if not super(BoreSinePole, self).__eq__(other):
            return False
        if other.N != self.N:
            return False
        if other.k != self.k:
            return False
        if other.delta_d != self.delta_d:
            return False
        if other.delta_q != self.delta_q:
            return False
        if other.W0 != self.W0:
            return False
        return True

    def compare(self, other, name="self", ignore_list=None, is_add_value=False):
        """Compare two objects and return list of differences"""

        if ignore_list is None:
            ignore_list = list()
        if type(other) != type(self):
            return ["type(" + name + ")"]
        diff_list = list()

        # Check the properties inherited from Bore
        diff_list.extend(
            super(BoreSinePole, self).compare(
                other, name=name, ignore_list=ignore_list, is_add_value=is_add_value
            )
        )
        if other._N != self._N:
            if is_add_value:
                val_str = " (self=" + str(self._N) + ", other=" + str(other._N) + ")"
                diff_list.append(name + ".N" + val_str)
            else:
                diff_list.append(name + ".N")
        if (
            other._k is not None
            and self._k is not None
            and np.isnan(other._k)
            and np.isnan(self._k)
        ):
            pass
        elif other._k != self._k:
            if is_add_value:
                val_str = " (self=" + str(self._k) + ", other=" + str(other._k) + ")"
                diff_list.append(name + ".k" + val_str)
            else:
                diff_list.append(name + ".k")
        if (
            other._delta_d is not None
            and self._delta_d is not None
            and np.isnan(other._delta_d)
            and np.isnan(self._delta_d)
        ):
            pass
        elif other._delta_d != self._delta_d:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._delta_d)
                    + ", other="
                    + str(other._delta_d)
                    + ")"
                )
                diff_list.append(name + ".delta_d" + val_str)
            else:
                diff_list.append(name + ".delta_d")
        if (
            other._delta_q is not None
            and self._delta_q is not None
            and np.isnan(other._delta_q)
            and np.isnan(self._delta_q)
        ):
            pass
        elif other._delta_q != self._delta_q:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._delta_q)
                    + ", other="
                    + str(other._delta_q)
                    + ")"
                )
                diff_list.append(name + ".delta_q" + val_str)
            else:
                diff_list.append(name + ".delta_q")
        if (
            other._W0 is not None
            and self._W0 is not None
            and np.isnan(other._W0)
            and np.isnan(self._W0)
        ):
            pass
        elif other._W0 != self._W0:
            if is_add_value:
                val_str = " (self=" + str(self._W0) + ", other=" + str(other._W0) + ")"
                diff_list.append(name + ".W0" + val_str)
            else:
                diff_list.append(name + ".W0")
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object

        # Get size of the properties inherited from Bore
        S += super(BoreSinePole, self).__sizeof__()
        S += getsizeof(self.N)
        S += getsizeof(self.k)
        S += getsizeof(self.delta_d)
        S += getsizeof(self.delta_q)
        S += getsizeof(self.W0)
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

        # Get the properties inherited from Bore
        BoreSinePole_dict = super(BoreSinePole, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs
        )
        BoreSinePole_dict["N"] = self.N
        BoreSinePole_dict["k"] = self.k
        BoreSinePole_dict["delta_d"] = self.delta_d
        BoreSinePole_dict["delta_q"] = self.delta_q
        BoreSinePole_dict["W0"] = self.W0
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        BoreSinePole_dict["__class__"] = "BoreSinePole"
        return BoreSinePole_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        N_val = self.N
        k_val = self.k
        delta_d_val = self.delta_d
        delta_q_val = self.delta_q
        W0_val = self.W0
        type_merge_slot_val = self.type_merge_slot
        alpha_val = self.alpha
        # Creates new object of the same type with the copied properties
        obj_copy = type(self)(
            N=N_val,
            k=k_val,
            delta_d=delta_d_val,
            delta_q=delta_q_val,
            W0=W0_val,
            type_merge_slot=type_merge_slot_val,
            alpha=alpha_val,
        )
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        self.N = None
        self.k = None
        self.delta_d = None
        self.delta_q = None
        self.W0 = None
        # Set to None the properties inherited from Bore
        super(BoreSinePole, self)._set_None()

    def _get_N(self):
        """getter of N"""
        return self._N

    def _set_N(self, value):
        """setter of N"""
        check_var("N", value, "int", Vmin=0)
        self._N = value

    N = property(
        fget=_get_N,
        fset=_set_N,
        doc="""Number of Poles

        :Type: int
        :min: 0
        """,
    )

    def _get_k(self):
        """getter of k"""
        return self._k

    def _set_k(self, value):
        """setter of k"""
        check_var("k", value, "float", Vmin=0)
        self._k = value

    k = property(
        fget=_get_k,
        fset=_set_k,
        doc="""pole width modifier

        :Type: float
        :min: 0
        """,
    )

    def _get_delta_d(self):
        """getter of delta_d"""
        return self._delta_d

    def _set_delta_d(self, value):
        """setter of delta_d"""
        check_var("delta_d", value, "float", Vmin=0)
        self._delta_d = value

    delta_d = property(
        fget=_get_delta_d,
        fset=_set_delta_d,
        doc="""d-axis air gap width

        :Type: float
        :min: 0
        """,
    )

    def _get_delta_q(self):
        """getter of delta_q"""
        return self._delta_q

    def _set_delta_q(self, value):
        """setter of delta_q"""
        check_var("delta_q", value, "float", Vmin=0)
        self._delta_q = value

    delta_q = property(
        fget=_get_delta_q,
        fset=_set_delta_q,
        doc="""q-axis air gap width

        :Type: float
        :min: 0
        """,
    )

    def _get_W0(self):
        """getter of W0"""
        return self._W0

    def _set_W0(self, value):
        """setter of W0"""
        check_var("W0", value, "float", Vmin=0)
        self._W0 = value

    W0 = property(
        fget=_get_W0,
        fset=_set_W0,
        doc="""Width of the pole

        :Type: float
        :min: 0
        """,
    )
