# -*- coding: utf-8 -*-
# File generated according to Generator/ClassesRef/Slot/HoleM57.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Slot/HoleM57
"""

# Inline fallback report:
# These methods remain imported because their source or imports cannot be safely moved into this class.
# - check: module uses a wildcard import whose names cannot be resolved safely
# - comp_magnetization_dict: import name 'Segment' refers to different sources (..Methods.Slot.HoleM57.build_geometry.Segment and .Segment.Segment)
# - plot_schematics: import name 'Segment' refers to different sources (..Methods.Slot.HoleM57.build_geometry.Segment and ..Methods.Slot.HoleM57.plot_schematics.Segment)

from os import linesep
from sys import getsizeof
from logging import getLogger
from ._check import check_var, raise_
from ..Functions.get_logger import get_logger
from ..Functions.save import save
from ..Functions.load import load_init_dict
from ..Functions.Load.import_class import import_class
from copy import deepcopy
from .HoleMag import HoleMag

# Import all class method
# Try/catch to remove unnecessary dependencies in unused method
from ..Methods.Slot.HoleM57.check import check
from ..Methods.Slot.HoleM57.comp_magnetization_dict import comp_magnetization_dict
from ..Methods.Slot.HoleM57.plot_schematics import plot_schematics
from numpy import arcsin, cos, exp, angle, pi, sin, tan
from ..Functions.Geometry.inter_line_line import inter_line_line
from ..Methods.Slot.HoleM57.build_geometry import HOLEM_LAB, Segment, SurfLine

from numpy import isnan
from ._check import InitUnKnowClassError


class HoleM57(HoleMag):
    """V shape slot for buried magnet"""

    VERSION = 1
    IS_SYMMETRICAL = 1

    # cf Methods.Slot.HoleM57._comp_point_coordinate
    def _comp_point_coordinate(self):
        """Compute the point coordinates needed to plot the Slot.

        Parameters
        ----------
        self : HoleM53
            A HoleM53 object

        Returns
        -------
        point_dict: dict
            A dict of the slot coordinates
        """
        Rext = self.get_Rext()

        # "Tooth" angle (P1',0,P1)
        alpha_T = 2 * arcsin(self.W3 / (2 * (Rext - self.H1)))
        # magnet pole pitch angle (Z1,0,Z1')
        alpha_S = (2 * pi / self.Zh) - alpha_T
        # Angle (P1,P1',P4') and (P5',P4', )
        alpha = (pi - self.W0) / 2
        # Half slot pitch
        hssp = pi / self.Zh

        Z1 = (Rext - self.H1) * exp(-1j * alpha_S / 2)
        x11 = 2 * sin(alpha_S / 2) * (Rext - self.H1)  # Distance from P1 to P1'
        # In rect triangle P4, P1, perp (P1,P1') with P4
        H = tan(alpha) * (x11 / 2 - self.W1 / 2)
        Z4 = Z1.real - H - 1j * self.W1 / 2

        x45 = self.H2 / cos(alpha)  # distance from P4 to P5
        Z5 = Z4 - x45

        # Get coordinates of "random" points on (P5,P8) and (P1,P8)
        # In ref P4 center and P1 on X+ axis
        Z58 = (self.W4 - 1j * self.H2) * exp(1j * angle(Z1 - Z4)) + Z4
        # In the tooth ref
        Z18 = (Rext - self.H1 - self.H2 + 1j * self.W3 / 2) * exp(-1j * hssp)
        Z8 = inter_line_line(Z5, Z58, Z1, Z18)[0]

        # In ref "b" P4 center and P1 on X+ axis
        Z8b = (Z8 - Z4) * exp(-1j * angle(Z1 - Z4))
        Z9 = (Z8b + 1j * self.H2) * exp(1j * angle(Z1 - Z4)) + Z4
        Z2 = (Z8b + 1j * self.H2 - self.W2) * exp(1j * angle(Z1 - Z4)) + Z4
        Z3 = (Z8b + 1j * self.H2 - self.W2 - self.W4) * exp(1j * angle(Z1 - Z4)) + Z4
        Z7 = (Z8b - self.W2) * exp(1j * angle(Z1 - Z4)) + Z4
        Z6 = (Z8b - self.W2 - self.W4) * exp(1j * angle(Z1 - Z4)) + Z4

        point_dict = dict()
        point_dict["Z1"] = Z1
        point_dict["Z2"] = Z2
        point_dict["Z3"] = Z3
        point_dict["Z4"] = Z4
        point_dict["Z5"] = Z5
        point_dict["Z6"] = Z6
        point_dict["Z7"] = Z7
        point_dict["Z8"] = Z8
        point_dict["Z9"] = Z9

        # Symmetry
        point_dict["Z1s"] = Z1.conjugate()
        point_dict["Z2s"] = Z2.conjugate()
        point_dict["Z3s"] = Z3.conjugate()
        point_dict["Z4s"] = Z4.conjugate()
        point_dict["Z5s"] = Z5.conjugate()
        point_dict["Z6s"] = Z6.conjugate()
        point_dict["Z7s"] = Z7.conjugate()
        point_dict["Z8s"] = Z8.conjugate()
        point_dict["Z9s"] = Z9.conjugate()
        point_dict["Zc0"] = inter_line_line(
            Z3, Z2, point_dict["Z3s"], point_dict["Z2s"]
        )[0]
        return point_dict

    # cf Methods.Slot.HoleM57.build_geometry
    def build_geometry(self, alpha=0, delta=0, is_simplified=False):
        """Compute the curve (Segment) needed to plot the Slot.
        The ending point of a curve is the starting point of the next curve in
        the list

        Parameters
        ----------
        self : HoleM57
            A HoleM57 object
        alpha : float
            Angle to rotate the slot (Default value = 0) [rad]
        delta : complex
            Complex to translate the slot (Default value = 0)
        is_simplified : bool
           True to avoid line superposition

        Returns
        -------
        surf_list: list
            List of SurfLine needed to draw the HoleM57

        """

        # Get correct label for surfaces
        lam_label = self.parent.get_label()
        R_id, surf_type = self.get_R_id()
        vent_label = lam_label + "_" + surf_type + "_R" + str(R_id) + "-"
        mag_label = lam_label + "_" + HOLEM_LAB + "_R" + str(R_id) + "-"

        # Get all the points
        point_dict = self._comp_point_coordinate()
        Z1 = point_dict["Z1"]
        Z2 = point_dict["Z2"]
        Z3 = point_dict["Z3"]
        Z4 = point_dict["Z4"]
        Z5 = point_dict["Z5"]
        Z6 = point_dict["Z6"]
        Z7 = point_dict["Z7"]
        Z8 = point_dict["Z8"]

        Z1s = point_dict["Z1s"]
        Z2s = point_dict["Z2s"]
        Z3s = point_dict["Z3s"]
        Z4s = point_dict["Z4s"]
        Z5s = point_dict["Z5s"]
        Z6s = point_dict["Z6s"]
        Z7s = point_dict["Z7s"]
        Z8s = point_dict["Z8s"]

        surf_list = list()
        # Z_list = array([Z1, Z2, Z3, Z4, Z5, Z6, Z7, Z8])
        # plt.plot(Z_list.real, Z_list.imag, "x r")
        # for ii in range(8):
        #     plt.text(Z_list[ii].real, Z_list[ii].imag, "Z" + str(ii + 1))
        # plt.show()
        # Check schematics:
        assert abs(abs(Z7 - Z8) - self.W2) < 1e-6
        assert abs(abs(Z6 - Z7) - self.W4) < 1e-6
        assert abs(abs(Z2 - Z3) - self.W4) < 1e-6
        assert abs(abs(Z2 - Z7) - self.H2) < 1e-6
        assert abs(abs(Z4 - Z4s) - self.W1) < 1e-6
        assert abs(abs(Z5 - Z5s) - self.W1) < 1e-6
        # TODO: Create all the surfaces for all the cases
        # (with/without magnet W1>0 or W1=0)
        # Air surface (W3) with magnet_0
        curve_list = list()
        curve_list.append(Segment(Z1, Z2))
        curve_list.append(Segment(Z2, Z7))
        if self.W2 > 0:
            curve_list.append(Segment(Z7, Z8))
        curve_list.append(Segment(Z8, Z1))

        # initiating the label of the line on the air surface
        # curve_list = set_name_line(curve_list, "hole_1_line")
        point_ref = (Z1 + Z2 + Z7 + Z8) / 4
        S1 = SurfLine(
            line_list=curve_list, label=vent_label + "T0-S0", point_ref=point_ref
        )

        # Magnet_0 surface
        curve_list = list()
        if is_simplified:
            curve_list.append(Segment(Z7, Z2))
            curve_list.append(Segment(Z3, Z6))
        else:
            curve_list.append(Segment(Z2, Z3))
            curve_list.append(Segment(Z3, Z6))
            curve_list.append(Segment(Z6, Z7))
            curve_list.append(Segment(Z7, Z2))

        # initiating the label of the line of the magnet surface
        # curve_list = set_name_line(curve_list, "magnet_1_line")
        point_ref = (Z2 + Z3 + Z6 + Z7) / 4
        S2 = SurfLine(
            line_list=curve_list,
            label=mag_label + "T0-S0",
            point_ref=point_ref,
        )

        # Air surface with magnet_0 and W1 > 0
        curve_list = list()
        curve_list.append(Segment(Z4, Z5))
        curve_list.append(Segment(Z5, Z6))
        curve_list.append(Segment(Z6, Z3))
        if abs(Z4 - Z3) > 1e-6:
            curve_list.append(Segment(Z3, Z4))

        # initiating the label of the line on the air surface
        # curve_list = set_name_line(curve_list, "hole_2_line")
        point_ref = (Z6 + Z5 + Z4) / 3

        S3 = SurfLine(
            line_list=curve_list, label=vent_label + "T1-S0", point_ref=point_ref
        )

        # Symmetry Air surface (W3) with magnet_1
        curve_list = list()
        curve_list.append(Segment(Z2s, Z1s))
        curve_list.append(Segment(Z1s, Z8s))
        if self.W2 > 0:
            curve_list.append(Segment(Z8s, Z7s))
        curve_list.append(Segment(Z7s, Z2s))
        point_ref = (Z1s + Z2s + Z8s + Z7s) / 4
        # initiating the label of the line on the air surface
        # curve_list = set_name_line(curve_list, "hole_3_line")
        S4 = SurfLine(
            line_list=curve_list, label=vent_label + "T2-S0", point_ref=point_ref
        )

        # magnet_1 surface
        curve_list = list()
        if is_simplified:
            curve_list.append(Segment(Z2s, Z7s))
            curve_list.append(Segment(Z6s, Z3s))
        else:
            curve_list.append(Segment(Z3s, Z2s))
            curve_list.append(Segment(Z2s, Z7s))
            curve_list.append(Segment(Z7s, Z6s))
            curve_list.append(Segment(Z6s, Z3s))
        point_ref = (Z3s + Z2s + Z7s + Z6s) / 4

        # initiating the label of the line on the magnet surface
        # curve_list = set_name_line(curve_list, "magnet_2_line")
        S5 = SurfLine(
            line_list=curve_list,
            label=mag_label + "T1-S0",
            point_ref=point_ref,
        )

        # Air surface with magnet_1 and W1 > 0
        curve_list = list()
        curve_list.append(Segment(Z3s, Z6s))
        curve_list.append(Segment(Z6s, Z5s))
        curve_list.append(Segment(Z5s, Z4s))
        if abs(Z4 - Z3) > 1e-6:
            curve_list.append(Segment(Z4s, Z3s))

        point_ref = (Z3s + Z6s + Z5s) / 3

        # initiating the label of the line on the air surface
        # curve_list = set_name_line(curve_list, "hole_4_line")
        S6 = SurfLine(
            line_list=curve_list, label=vent_label + "T1-S0", point_ref=point_ref
        )

        # Air surface between magnet_0 and magnet_1 with W1 == 0
        curve_list = list()
        curve_list.append(Segment(Z3, Z4))
        curve_list.append(Segment(Z4, Z3s))
        curve_list.append(Segment(Z3s, Z6s))
        curve_list.append(Segment(Z6s, Z5))
        curve_list.append(Segment(Z5, Z6))
        curve_list.append(Segment(Z6, Z3))

        # initiating the label of the line on the air surface
        # curve_list = set_name_line(curve_list, "hole_2_line")
        point_ref = (Z5 + Z4) / 2

        S7 = SurfLine(
            line_list=curve_list, label=vent_label + "T2-S0", point_ref=point_ref
        )

        # Air surface without magnet_0 and W1 > 0
        curve_list = list()
        curve_list.append(Segment(Z1, Z8))
        curve_list.append(Segment(Z8, Z5))
        curve_list.append(Segment(Z5, Z4))
        curve_list.append(Segment(Z4, Z1))

        # initiating the label of the line on the air surface
        # curve_list = set_name_line(curve_list, "hole_1_line")
        point_ref = (Z5 + Z1) / 2

        S8 = SurfLine(
            line_list=curve_list, label=vent_label + "T1-S0", point_ref=point_ref
        )

        # Air surface without magnet_1 and W1 > 0
        curve_list = list()
        curve_list.append(Segment(Z1s, Z8s))
        curve_list.append(Segment(Z8s, Z5s))
        curve_list.append(Segment(Z5s, Z4s))
        curve_list.append(Segment(Z4s, Z1s))

        # initiating the label of the line on the air surface
        # curve_list = set_name_line(curve_list, "hole_2_line")
        point_ref = (Z5s + Z1s) / 2

        S9 = SurfLine(
            line_list=curve_list, label=vent_label + "T0-S0", point_ref=point_ref
        )

        # Air surface No magnet and W1 == 0
        curve_list = list()
        curve_list.append(Segment(Z4, Z1))
        curve_list.append(Segment(Z1, Z8))
        curve_list.append(Segment(Z8, Z5))
        curve_list.append(Segment(Z5, Z8s))
        curve_list.append(Segment(Z8s, Z1s))
        curve_list.append(Segment(Z1s, Z4))

        # initiating the label of the line on the air surface
        # curve_list = set_name_line(curve_list, "hole_1_line")
        point_ref = (Z4 + Z5) / 2

        S12 = SurfLine(
            line_list=curve_list, label=vent_label + "T0-S0", point_ref=point_ref
        )

        # TODO correct vent_label TX id
        # Create the surface list by selecting the correct ones
        if self.magnet_0 and self.magnet_1 and self.W1 > 0:
            surf_list = [S1, S2, S3, S6, S5, S4]
        elif self.magnet_0 and self.magnet_1 and self.W1 == 0:
            surf_list = [S1, S2, S7, S5, S4]
        # elif self.magnet_0 and not self.magnet_1 and self.W1 > 0:
        #     surf_list = [S1, S2, S3, S9]
        # elif self.magnet_0 and not self.magnet_1 and self.W1 == 0:
        #     surf_list = [S1, S2, S10]
        # elif not self.magnet_0 and self.magnet_1 and self.W1 > 0:
        #     surf_list = [S8, S6, S5, S4]
        # elif not self.magnet_0 and self.magnet_1 and self.W1 == 0:
        #     surf_list = [S11, S5, S4]
        elif not self.magnet_0 and not self.magnet_1 and self.W1 > 0:
            surf_list = [S8, S9]
        elif not self.magnet_0 and not self.magnet_1 and self.W1 == 0:
            surf_list = [S12]
        else:
            raise Exception("Not implemented Yet")

        # Apply the transformations
        for surf in surf_list:
            surf.rotate(alpha)
            surf.translate(delta)

        return surf_list

    # cf Methods.Slot.HoleM57.check
    check = check
    # cf Methods.Slot.HoleM57.comp_magnetization_dict
    comp_magnetization_dict = comp_magnetization_dict

    # cf Methods.Slot.HoleM57.comp_radius
    def comp_radius(self):
        """Compute the radius of the min and max circle that contains the slot

        Parameters
        ----------
        self : HoleM57
            A HoleM57 object

        Returns
        -------
        (Rmin,Rmax): tuple
            Radius of the circle that contains the slot [m]
        """
        Rext = self.get_Rext()

        Rmax = Rext - self.H1
        Rmin = abs(self._comp_point_coordinate()["Z5"])

        return (Rmin, Rmax)

    # cf Methods.Slot.HoleM57.comp_surface_magnet_id
    def comp_surface_magnet_id(self, index):
        """Compute the surface of the hole magnet of the corresponding index

        Parameters
        ----------
        self : HoleM57
            A HoleM57 object
        index : int
            Index of the magnet to compute the surface

        Returns
        -------
        Smag: float
            Surface of the Magnet [m**2]
        """

        # all magnet has the same surface
        label = "magnet_" + str(index)
        if index in [0, 1] and getattr(self, label) is not None:
            return self.H2 * self.W4
        return 0

    # cf Methods.Slot.HoleM57.has_magnet
    def has_magnet(self):
        """Return if the Hole has magnets

        Parameters
        ----------
        self : HoleM57
            A HoleM57 object

        Returns
        -------
        has_magnet : bool
            True if the magnets are not None
        """

        return self.magnet_0 is not None or self.magnet_1 is not None

    # cf Methods.Slot.HoleM57.plot_schematics
    plot_schematics = plot_schematics

    # cf Methods.Slot.HoleM57.remove_magnet
    def remove_magnet(self):
        """Remove the magnet (set to None) of the Hole

        Parameters
        ----------
        self : HoleM57
            a HoleM57 object
        """

        self.magnet_0 = None
        self.magnet_1 = None

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
        W0=0.2,
        H1=0,
        W1=0.013,
        H2=0.02,
        W2=0.01,
        W3=0.01,
        W4=0.01,
        magnet_0=-1,
        magnet_1=-1,
        Zh=36,
        mat_void=-1,
        magnetization_dict_offset=None,
        Alpha0=0,
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
            if "W0" in list(init_dict.keys()):
                W0 = init_dict["W0"]
            if "H1" in list(init_dict.keys()):
                H1 = init_dict["H1"]
            if "W1" in list(init_dict.keys()):
                W1 = init_dict["W1"]
            if "H2" in list(init_dict.keys()):
                H2 = init_dict["H2"]
            if "W2" in list(init_dict.keys()):
                W2 = init_dict["W2"]
            if "W3" in list(init_dict.keys()):
                W3 = init_dict["W3"]
            if "W4" in list(init_dict.keys()):
                W4 = init_dict["W4"]
            if "magnet_0" in list(init_dict.keys()):
                magnet_0 = init_dict["magnet_0"]
            if "magnet_1" in list(init_dict.keys()):
                magnet_1 = init_dict["magnet_1"]
            if "Zh" in list(init_dict.keys()):
                Zh = init_dict["Zh"]
            if "mat_void" in list(init_dict.keys()):
                mat_void = init_dict["mat_void"]
            if "magnetization_dict_offset" in list(init_dict.keys()):
                magnetization_dict_offset = init_dict["magnetization_dict_offset"]
            if "Alpha0" in list(init_dict.keys()):
                Alpha0 = init_dict["Alpha0"]
        # Set the properties (value check and convertion are done in setter)
        self.W0 = W0
        self.H1 = H1
        self.W1 = W1
        self.H2 = H2
        self.W2 = W2
        self.W3 = W3
        self.W4 = W4
        self.magnet_0 = magnet_0
        self.magnet_1 = magnet_1
        # Call HoleMag init
        super(HoleM57, self).__init__(
            Zh=Zh,
            mat_void=mat_void,
            magnetization_dict_offset=magnetization_dict_offset,
            Alpha0=Alpha0,
        )
        # The class is frozen (in HoleMag init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        HoleM57_str = ""
        # Get the properties inherited from HoleMag
        HoleM57_str += super(HoleM57, self).__str__()
        HoleM57_str += "W0 = " + str(self.W0) + linesep
        HoleM57_str += "H1 = " + str(self.H1) + linesep
        HoleM57_str += "W1 = " + str(self.W1) + linesep
        HoleM57_str += "H2 = " + str(self.H2) + linesep
        HoleM57_str += "W2 = " + str(self.W2) + linesep
        HoleM57_str += "W3 = " + str(self.W3) + linesep
        HoleM57_str += "W4 = " + str(self.W4) + linesep
        if self.magnet_0 is not None:
            tmp = self.magnet_0.__str__().replace(linesep, linesep + "\t").rstrip("\t")
            HoleM57_str += "magnet_0 = " + tmp
        else:
            HoleM57_str += "magnet_0 = None" + linesep + linesep
        if self.magnet_1 is not None:
            tmp = self.magnet_1.__str__().replace(linesep, linesep + "\t").rstrip("\t")
            HoleM57_str += "magnet_1 = " + tmp
        else:
            HoleM57_str += "magnet_1 = None" + linesep + linesep
        return HoleM57_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from HoleMag
        if not super(HoleM57, self).__eq__(other):
            return False
        if other.W0 != self.W0:
            return False
        if other.H1 != self.H1:
            return False
        if other.W1 != self.W1:
            return False
        if other.H2 != self.H2:
            return False
        if other.W2 != self.W2:
            return False
        if other.W3 != self.W3:
            return False
        if other.W4 != self.W4:
            return False
        if other.magnet_0 != self.magnet_0:
            return False
        if other.magnet_1 != self.magnet_1:
            return False
        return True

    def compare(self, other, name="self", ignore_list=None, is_add_value=False):
        """Compare two objects and return list of differences"""

        if ignore_list is None:
            ignore_list = list()
        if type(other) != type(self):
            return ["type(" + name + ")"]
        diff_list = list()

        # Check the properties inherited from HoleMag
        diff_list.extend(
            super(HoleM57, self).compare(
                other, name=name, ignore_list=ignore_list, is_add_value=is_add_value
            )
        )
        if (
            other._W0 is not None
            and self._W0 is not None
            and isnan(other._W0)
            and isnan(self._W0)
        ):
            pass
        elif other._W0 != self._W0:
            if is_add_value:
                val_str = " (self=" + str(self._W0) + ", other=" + str(other._W0) + ")"
                diff_list.append(name + ".W0" + val_str)
            else:
                diff_list.append(name + ".W0")
        if (
            other._H1 is not None
            and self._H1 is not None
            and isnan(other._H1)
            and isnan(self._H1)
        ):
            pass
        elif other._H1 != self._H1:
            if is_add_value:
                val_str = " (self=" + str(self._H1) + ", other=" + str(other._H1) + ")"
                diff_list.append(name + ".H1" + val_str)
            else:
                diff_list.append(name + ".H1")
        if (
            other._W1 is not None
            and self._W1 is not None
            and isnan(other._W1)
            and isnan(self._W1)
        ):
            pass
        elif other._W1 != self._W1:
            if is_add_value:
                val_str = " (self=" + str(self._W1) + ", other=" + str(other._W1) + ")"
                diff_list.append(name + ".W1" + val_str)
            else:
                diff_list.append(name + ".W1")
        if (
            other._H2 is not None
            and self._H2 is not None
            and isnan(other._H2)
            and isnan(self._H2)
        ):
            pass
        elif other._H2 != self._H2:
            if is_add_value:
                val_str = " (self=" + str(self._H2) + ", other=" + str(other._H2) + ")"
                diff_list.append(name + ".H2" + val_str)
            else:
                diff_list.append(name + ".H2")
        if (
            other._W2 is not None
            and self._W2 is not None
            and isnan(other._W2)
            and isnan(self._W2)
        ):
            pass
        elif other._W2 != self._W2:
            if is_add_value:
                val_str = " (self=" + str(self._W2) + ", other=" + str(other._W2) + ")"
                diff_list.append(name + ".W2" + val_str)
            else:
                diff_list.append(name + ".W2")
        if (
            other._W3 is not None
            and self._W3 is not None
            and isnan(other._W3)
            and isnan(self._W3)
        ):
            pass
        elif other._W3 != self._W3:
            if is_add_value:
                val_str = " (self=" + str(self._W3) + ", other=" + str(other._W3) + ")"
                diff_list.append(name + ".W3" + val_str)
            else:
                diff_list.append(name + ".W3")
        if (
            other._W4 is not None
            and self._W4 is not None
            and isnan(other._W4)
            and isnan(self._W4)
        ):
            pass
        elif other._W4 != self._W4:
            if is_add_value:
                val_str = " (self=" + str(self._W4) + ", other=" + str(other._W4) + ")"
                diff_list.append(name + ".W4" + val_str)
            else:
                diff_list.append(name + ".W4")
        if (other.magnet_0 is None and self.magnet_0 is not None) or (
            other.magnet_0 is not None and self.magnet_0 is None
        ):
            diff_list.append(name + ".magnet_0 None mismatch")
        elif self.magnet_0 is not None:
            diff_list.extend(
                self.magnet_0.compare(
                    other.magnet_0,
                    name=name + ".magnet_0",
                    ignore_list=ignore_list,
                    is_add_value=is_add_value,
                )
            )
        if (other.magnet_1 is None and self.magnet_1 is not None) or (
            other.magnet_1 is not None and self.magnet_1 is None
        ):
            diff_list.append(name + ".magnet_1 None mismatch")
        elif self.magnet_1 is not None:
            diff_list.extend(
                self.magnet_1.compare(
                    other.magnet_1,
                    name=name + ".magnet_1",
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

        # Get size of the properties inherited from HoleMag
        S += super(HoleM57, self).__sizeof__()
        S += getsizeof(self.W0)
        S += getsizeof(self.H1)
        S += getsizeof(self.W1)
        S += getsizeof(self.H2)
        S += getsizeof(self.W2)
        S += getsizeof(self.W3)
        S += getsizeof(self.W4)
        S += getsizeof(self.magnet_0)
        S += getsizeof(self.magnet_1)
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

        # Get the properties inherited from HoleMag
        HoleM57_dict = super(HoleM57, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs
        )
        HoleM57_dict["W0"] = self.W0
        HoleM57_dict["H1"] = self.H1
        HoleM57_dict["W1"] = self.W1
        HoleM57_dict["H2"] = self.H2
        HoleM57_dict["W2"] = self.W2
        HoleM57_dict["W3"] = self.W3
        HoleM57_dict["W4"] = self.W4
        if self.magnet_0 is None:
            HoleM57_dict["magnet_0"] = None
        else:
            HoleM57_dict["magnet_0"] = self.magnet_0.as_dict(
                type_handle_ndarray=type_handle_ndarray,
                keep_function=keep_function,
                **kwargs
            )
        if self.magnet_1 is None:
            HoleM57_dict["magnet_1"] = None
        else:
            HoleM57_dict["magnet_1"] = self.magnet_1.as_dict(
                type_handle_ndarray=type_handle_ndarray,
                keep_function=keep_function,
                **kwargs
            )
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        HoleM57_dict["__class__"] = "HoleM57"
        return HoleM57_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        W0_val = self.W0
        H1_val = self.H1
        W1_val = self.W1
        H2_val = self.H2
        W2_val = self.W2
        W3_val = self.W3
        W4_val = self.W4
        if self.magnet_0 is None:
            magnet_0_val = None
        else:
            magnet_0_val = self.magnet_0.copy()
        if self.magnet_1 is None:
            magnet_1_val = None
        else:
            magnet_1_val = self.magnet_1.copy()
        Zh_val = self.Zh
        if self.mat_void is None:
            mat_void_val = None
        else:
            mat_void_val = self.mat_void.copy()
        if self.magnetization_dict_offset is None:
            magnetization_dict_offset_val = None
        else:
            magnetization_dict_offset_val = self.magnetization_dict_offset.copy()
        Alpha0_val = self.Alpha0
        # Creates new object of the same type with the copied properties
        obj_copy = type(self)(
            W0=W0_val,
            H1=H1_val,
            W1=W1_val,
            H2=H2_val,
            W2=W2_val,
            W3=W3_val,
            W4=W4_val,
            magnet_0=magnet_0_val,
            magnet_1=magnet_1_val,
            Zh=Zh_val,
            mat_void=mat_void_val,
            magnetization_dict_offset=magnetization_dict_offset_val,
            Alpha0=Alpha0_val,
        )
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        self.W0 = None
        self.H1 = None
        self.W1 = None
        self.H2 = None
        self.W2 = None
        self.W3 = None
        self.W4 = None
        if self.magnet_0 is not None:
            self.magnet_0._set_None()
        if self.magnet_1 is not None:
            self.magnet_1._set_None()
        # Set to None the properties inherited from HoleMag
        super(HoleM57, self)._set_None()

    def _get_W0(self):
        """getter of W0"""
        return self._W0

    def _set_W0(self, value):
        """setter of W0"""
        check_var("W0", value, "float", Vmin=0, Vmax=3.15)
        self._W0 = value

    W0 = property(
        fget=_get_W0,
        fset=_set_W0,
        doc="""V angle

        :Type: float
        :min: 0
        :max: 3.15
        """,
    )

    def _get_H1(self):
        """getter of H1"""
        return self._H1

    def _set_H1(self, value):
        """setter of H1"""
        check_var("H1", value, "float", Vmin=0)
        self._H1 = value

    H1 = property(
        fget=_get_H1,
        fset=_set_H1,
        doc="""Distance from the lamination Bore

        :Type: float
        :min: 0
        """,
    )

    def _get_W1(self):
        """getter of W1"""
        return self._W1

    def _set_W1(self, value):
        """setter of W1"""
        check_var("W1", value, "float", Vmin=0)
        self._W1 = value

    W1 = property(
        fget=_get_W1,
        fset=_set_W1,
        doc="""Tooth width (at V bottom)

        :Type: float
        :min: 0
        """,
    )

    def _get_H2(self):
        """getter of H2"""
        return self._H2

    def _set_H2(self, value):
        """setter of H2"""
        check_var("H2", value, "float", Vmin=0)
        self._H2 = value

    H2 = property(
        fget=_get_H2,
        fset=_set_H2,
        doc="""Magnet height

        :Type: float
        :min: 0
        """,
    )

    def _get_W2(self):
        """getter of W2"""
        return self._W2

    def _set_W2(self, value):
        """setter of W2"""
        check_var("W2", value, "float", Vmin=0)
        self._W2 = value

    W2 = property(
        fget=_get_W2,
        fset=_set_W2,
        doc="""Distance Magnet to top of the V

        :Type: float
        :min: 0
        """,
    )

    def _get_W3(self):
        """getter of W3"""
        return self._W3

    def _set_W3(self, value):
        """setter of W3"""
        check_var("W3", value, "float", Vmin=0)
        self._W3 = value

    W3 = property(
        fget=_get_W3,
        fset=_set_W3,
        doc="""Tooth width (at V top)

        :Type: float
        :min: 0
        """,
    )

    def _get_W4(self):
        """getter of W4"""
        return self._W4

    def _set_W4(self, value):
        """setter of W4"""
        check_var("W4", value, "float", Vmin=0)
        self._W4 = value

    W4 = property(
        fget=_get_W4,
        fset=_set_W4,
        doc="""Magnet Width

        :Type: float
        :min: 0
        """,
    )

    def _get_magnet_0(self):
        """getter of magnet_0"""
        return self._magnet_0

    def _set_magnet_0(self, value):
        """setter of magnet_0"""
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
                "pyleecan.Classes", value.get("__class__"), "magnet_0"
            )
            value = class_obj(init_dict=value)
        elif type(value) is int and value == -1:  # Default constructor
            Magnet = import_class("pyleecan.Classes", "Magnet", "magnet_0")
            value = Magnet()
        check_var("magnet_0", value, "Magnet")
        self._magnet_0 = value

        if self._magnet_0 is not None:
            self._magnet_0.parent = self

    magnet_0 = property(
        fget=_get_magnet_0,
        fset=_set_magnet_0,
        doc="""First Magnet

        :Type: Magnet
        """,
    )

    def _get_magnet_1(self):
        """getter of magnet_1"""
        return self._magnet_1

    def _set_magnet_1(self, value):
        """setter of magnet_1"""
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
                "pyleecan.Classes", value.get("__class__"), "magnet_1"
            )
            value = class_obj(init_dict=value)
        elif type(value) is int and value == -1:  # Default constructor
            Magnet = import_class("pyleecan.Classes", "Magnet", "magnet_1")
            value = Magnet()
        check_var("magnet_1", value, "Magnet")
        self._magnet_1 = value

        if self._magnet_1 is not None:
            self._magnet_1.parent = self

    magnet_1 = property(
        fget=_get_magnet_1,
        fset=_set_magnet_1,
        doc="""Second Magnet

        :Type: Magnet
        """,
    )
