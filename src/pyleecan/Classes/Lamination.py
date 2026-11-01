# -*- coding: utf-8 -*-
# File generated according to Generator/ClassesRef/Machine/Lamination.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Machine/Lamination
"""

# Inline fallback report:
# These methods remain imported because their source or imports cannot be safely moved into this class.
# - check: module uses a wildcard import whose names cannot be resolved safely

from os import linesep
from sys import getsizeof
from logging import getLogger
from pyleecan.Classes._check import check_var, raise_
from pyleecan.Functions.get_logger import get_logger
from pyleecan.Functions.save import save
from pyleecan.Functions.load import load_init_dict
from pyleecan.Functions.Load.import_class import import_class
from copy import deepcopy
from pyleecan.Classes._frozen import FrozenClass

# Import all class method
# Try/catch to remove unnecessary dependencies in unused method
from pyleecan.Methods.Machine.Lamination.check import check
from pyleecan.Classes.SurfLine import SurfLine
from pyleecan.Classes.SurfRing import SurfRing
from pyleecan.Functions.labels import (
    LAM_LAB,
    BORE_LAB,
    YOKE_LAB,
    RADIUS_PROP_LAB,
    BOUNDARY_PROP_LAB,
    YS_LAB,
    YSR_LAB,
    YSL_LAB,
    STATOR_LAB,
    ROTOR_LAB,
    NOTCH_LAB,
    YSNR_LAB,
    YSNL_LAB,
)
from pyleecan.Functions.Geometry.transform_hole_surf import transform_hole_surf
import numpy as np, matplotlib.pyplot as plt
from pyleecan.Classes.Arc1 import Arc1
from pyleecan.Classes.Arc3 import Arc3
from pyleecan.Functions.Geometry.merge_notch_list import merge_notch_list
from pyleecan.Methods.Machine.Lamination.build_yoke_side_line import merge_line_list
from pyleecan.Classes.OutGeoLam import OutGeoLam
from math import gcd
from pyleecan.Functions.Winding.gen_phase_list import gen_name
from pyleecan.Classes.NotchEvenDist import NotchEvenDist
from pyleecan.Methods import NotImplementedYetError
from matplotlib.patches import Patch
from pyleecan.Functions.init_fig import init_fig
from pyleecan.Functions.Plot.get_color_legend_from_surface import (
    get_color_legend_from_surface,
)
from pyleecan.Functions.Load.import_class import import_class
from pyleecan.definitions import config_dict


from pyleecan.Classes._check import InitUnKnowClassError


class Lamination(FrozenClass):
    """abstract class for lamination"""

    VERSION = 1
    PATCH_COLOR_ALPHA = config_dict["PLOT"]["COLOR_DICT"]["PATCH_COLOR_ALPHA"]
    ROTOR_COLOR = config_dict["PLOT"]["COLOR_DICT"]["ROTOR_COLOR"]
    STATOR_COLOR = config_dict["PLOT"]["COLOR_DICT"]["STATOR_COLOR"]

    # cf Methods.Machine.Lamination.build_geometry
    def build_geometry(self, sym=1, alpha=0, delta=0, is_circular_radius=False):
        """Build the geometry of the Lamination

        Parameters
        ----------
        self : Lamination
            Lamination Object
        sym : int
            Symmetry factor (1= full machine, 2= half of the machine...)
        alpha : float
            Angle for rotation [rad]
        delta : complex
            Complex value for translation
        is_circular_radius : bool
            True to add surfaces to "close" the Lamination radii

        Returns
        surf_list : list
            list of surfaces needed to draw the lamination

        """
        # Label setup
        label = self.get_label()
        label_lam = label + "_" + LAM_LAB
        label_bore = label + "_" + LAM_LAB + BORE_LAB
        label_yoke = label + "_" + LAM_LAB + YOKE_LAB
        if self.is_internal:
            label_ext = label_bore
            label_int = label_yoke
        else:
            label_ext = label_yoke
            label_int = label_bore

        # Get Radius lines
        yoke_prop = {RADIUS_PROP_LAB: YOKE_LAB, BOUNDARY_PROP_LAB: label_yoke}
        if self.is_internal:
            if self.Rint > 0:
                int_line = self.build_radius_lines(
                    is_bore=False, sym=sym, is_reversed=True, prop_dict=yoke_prop
                )
            else:
                int_line = []
            ext_line = self.build_radius_lines(
                is_bore=True, sym=sym, prop_dict={RADIUS_PROP_LAB: BORE_LAB}
            )
        else:
            ext_line = self.build_radius_lines(
                is_bore=False, sym=sym, is_reversed=True, prop_dict=yoke_prop
            )
            int_line = self.build_radius_lines(
                is_bore=True, sym=sym, prop_dict={RADIUS_PROP_LAB: BORE_LAB}
            )

        # Add the ventilation ducts if there is any
        surf_list = list()
        vent_surf_list = list()
        if self.axial_vent not in [None, []]:
            for vent in self.axial_vent:
                kwargs = dict(alpha=0, delta=0)
                vent_list = vent.build_geometry(**kwargs)
                surf = transform_hole_surf(
                    hole_surf_list=vent_list,
                    Zh=vent.Zh,
                    sym=sym,
                    is_split=True,
                    **kwargs
                )
                vent_surf_list.extend(surf)
        surf_list.extend(vent_surf_list)

        # Add keys if any
        if self.notch is not None:
            for ii, notch in enumerate(self.notch):
                if notch.has_key():
                    surf_list.extend(notch.build_geometry_key(index=ii, sym=sym))

        # Add the closing surfaces if requested
        if is_circular_radius:
            surf_list.extend(self.get_surfaces_closing(sym=sym))

        # Create the Lamination surfaces
        point_ref = self.comp_point_ref(sym=sym)
        if sym == 1:  # Complete lamination
            ext_surf = SurfLine(
                label=label_ext, line_list=ext_line, point_ref=point_ref
            )
            int_surf = SurfLine(label=label_int, line_list=int_line, point_ref=0)
            if self.Rint > 0 and len(ext_line) > 0:
                surf_list.insert(
                    0,
                    SurfRing(
                        out_surf=ext_surf,
                        in_surf=int_surf,
                        label=label_lam,
                        point_ref=point_ref,
                    ),  # First in list for plot
                )
            elif self.Rint == 0 and len(ext_line) > 0:
                surf_list.insert(0, ext_surf)  # First in list for plot
            elif self.Rint == self.Rext:  # No lamination
                pass  # No surface to draw
            elif len(ext_line) == 0:  # (SlotM17)
                pass  # No surface to draw / No lamination
        # Part of the lamination by symmetry
        elif sym != 1 and len(ext_line) > 0 and self.Rint != self.Rext:
            # Get limit point of the yoke side
            if self.is_internal:
                ZTR = ext_line[0].get_begin()  # Top Right
                ZTL = ext_line[-1].get_end()  # Top Left
                if len(int_line) > 0:
                    ZBR = int_line[-1].get_end()  # Bot Right
                    ZBL = int_line[0].get_begin()  # Bot Left
                else:  # Machine without shaft for instance
                    ZBR = None
                    ZBL = None
            else:
                ZTR = ext_line[-1].get_end()  # Top Right
                ZTL = ext_line[0].get_begin()  # Top Left
                if len(int_line) > 0:
                    ZBL = int_line[-1].get_end()  # Bot Left
                    ZBR = int_line[0].get_begin()  # Bot Right
                else:  # Machine without shaft for instance
                    ZBR = None
                    ZBL = None
            right_list, left_list = self.build_yoke_side_line(
                sym=sym,
                vent_surf_list=vent_surf_list,
                ZBR=ZBR,
                ZTR=ZTR,
                ZBL=ZBL,
                ZTL=ZTL,
            )
            # Create lines
            curve_list = list()
            if self.is_internal:
                curve_list.extend(right_list)
            else:
                curve_list.extend(left_list)
            curve_list.extend(ext_line)
            if self.is_internal:
                curve_list.extend(left_list)
            else:
                curve_list.extend(right_list)
            if self.Rint > 0:
                curve_list.extend(int_line)

            surf_yoke = SurfLine(
                line_list=curve_list, label=label_lam, point_ref=point_ref
            )
            surf_list.insert(0, surf_yoke)  # First in list for plot

        # apply the transformation
        for surf in surf_list:
            surf.rotate(alpha)
            surf.translate(delta)

        return surf_list

    # cf Methods.Machine.Lamination.build_radius_desc
    def build_radius_desc(self, is_bore, sym=1):
        """This method returns an ordered description of the slot/notch
        that defines the bore/yoke radius of the lamination
        (Bore/Yoke shape not taken into account by this method, cf build_radius_lines)

        Parameters
        ----------
        self : Lamination
            A Lamination object
        is_bore : bool
            True generate description of bore, else yoke
        sym : int
            Symmetry factor (1= full machine, 2= half of the machine...)

        Returns
        -------
        radius_desc : list
            trigo ordered list of dictionary with key:
                "begin_angle" : float [rad]
                "end_angle" : float [rad]
                "obj" : Slot or None
                "lines : lines corresponding to the radius part
                "label" : Radius/Notch/Slot
        """

        # For readibility
        is_notch = self.has_notch(is_bore=is_bore)
        is_slot = self.has_slot(is_bore=is_bore)
        if is_bore:
            R = self.get_Rbo()
        else:
            R = self.get_Ryoke()

        radius_desc = list()
        if not is_notch and not is_slot:
            radius_lines = list()
            if sym == 1:  # Two arcs to avoid angle > 180 deg
                arc1 = Arc3(begin=R, end=-R, is_trigo_direction=True)
                arc2 = Arc3(begin=-R, end=R, is_trigo_direction=True)
                end_angle = 0
                radius_lines.append(arc1)
                radius_lines.append(arc2)
            else:
                end_angle = 2 * np.pi / sym
                rot = np.exp(1j * end_angle)
                arc = Arc1(begin=R, end=R * rot, radius=R, is_trigo_direction=True)
                radius_lines.append(arc)
            radius_desc.append(
                {
                    "begin_angle": 0,
                    "end_angle": end_angle,
                    "obj": None,
                    "lines": radius_lines,
                    "label": "Radius",
                }
            )
            return radius_desc

        # Notch/Slot case
        if is_notch:
            # Get all the notch on the selected radius
            notch_list = [
                notch for notch in self.notch if notch.notch_shape.is_bore == is_bore
            ]
            # Get description of first notch
            notch_desc_list = notch_list[0].get_notch_desc_list(sym=sym)
            # If more than one notch, we need to merge and order the description
            for ii in range(len(notch_list) - 1):
                notch_desc_list = merge_notch_list(
                    notch_desc_list, notch_list[ii + 1].get_notch_desc_list(sym=sym)
                )
        else:
            notch_desc_list = list()
        # Get slot description
        if is_slot:
            slot_desc_list = self.get_slot_desc_list(sym=sym, is_bore=is_bore)
        else:
            slot_desc_list = list()
        all_desc_list = merge_notch_list(notch_desc_list, slot_desc_list)

        # Add the radius between each notch/slot
        for ii in range(len(all_desc_list) - 1):
            radius_desc.append(all_desc_list[ii])
            begin = all_desc_list[ii]["end_angle"]
            end = all_desc_list[ii + 1]["begin_angle"]
            if begin != end:  # begin = end for "full slot / no tooth"
                radius_desc.append(
                    {
                        "begin_angle": begin,
                        "end_angle": end,
                        "obj": None,
                        "lines": [
                            Arc1(
                                begin=R * np.exp(1j * begin),
                                end=R * np.exp(1j * end),
                                radius=R,
                                is_trigo_direction=True,
                            )
                        ],
                        "label": "Radius",
                    }
                )
        # Add last notch/slot
        radius_desc.append(all_desc_list[-1])
        # Add first and last radius line if required
        if all_desc_list[0]["begin_angle"] > 0:
            if sym == 1 and all_desc_list[-1]["end_angle"] > 2 * np.pi:
                # Alpha >0, last notch cross Ox
                begin = all_desc_list[-1]["end_angle"] - 2 * np.pi
                radius_desc.insert(
                    0,
                    {
                        "begin_angle": begin,
                        "end_angle": all_desc_list[0]["begin_angle"],
                        "obj": None,
                        "lines": [
                            Arc1(
                                begin=R * np.exp(1j * begin),
                                end=R * np.exp(1j * all_desc_list[0]["begin_angle"]),
                                radius=R,
                                is_trigo_direction=True,
                            )
                        ],
                        "label": "Radius",
                    },
                )
            else:  # Add radius from Ox to first notch
                radius_desc.insert(
                    0,
                    {
                        "begin_angle": 0,
                        "end_angle": all_desc_list[0]["begin_angle"],
                        "obj": None,
                        "lines": [
                            Arc1(
                                begin=R * np.exp(1j * 0),
                                end=R * np.exp(1j * all_desc_list[0]["begin_angle"]),
                                radius=R,
                                is_trigo_direction=True,
                            )
                        ],
                        "label": "Radius",
                    },
                )
        if all_desc_list[-1]["end_angle"] < 2 * np.pi / sym:
            if all_desc_list[0]["begin_angle"] < 0 and sym == 1:
                # Full lamination with slot/notch on Ox
                radius_desc.append(
                    {
                        "begin_angle": all_desc_list[-1]["end_angle"],
                        "end_angle": 2 * np.pi + all_desc_list[0]["begin_angle"],
                        "obj": None,
                        "lines": [
                            Arc1(
                                begin=R * np.exp(1j * all_desc_list[-1]["end_angle"]),
                                end=R
                                * np.exp(
                                    1j * (2 * np.pi + all_desc_list[0]["begin_angle"])
                                ),
                                radius=R,
                                is_trigo_direction=True,
                            )
                        ],
                        "label": "Radius",
                    }
                )
            else:
                radius_desc.append(
                    {
                        "begin_angle": all_desc_list[-1]["end_angle"],
                        "end_angle": 2 * np.pi / sym,
                        "obj": None,
                        "lines": [
                            Arc1(
                                begin=R * np.exp(1j * all_desc_list[-1]["end_angle"]),
                                end=R * np.exp(1j * 2 * np.pi / sym),
                                radius=R,
                                is_trigo_direction=True,
                            )
                        ],
                        "label": "Radius",
                    }
                )
        return radius_desc

    # cf Methods.Machine.Lamination.build_radius_lines
    def build_radius_lines(self, is_bore, sym=1, is_reversed=False, prop_dict=None):
        """Create the lines need to draw the selected radius of the Lamination

        Parameters
        ----------
        self : Lamination
            a Lamination object
        is_bore : bool
            True generate lines of bore, else yoke
        is_reversed : bool
            True to return the lines in clockwise oder (reverse begin and end), False trigo
        sym : int
            Symmetry factor (1= full machine, 2= half of the machine...)
        prop_dict : dict
            Property dictionary to apply on the radius lines (not on slot/notch)

        Returns
        -------
        radius_lines : list
            list of bore/yoke lines
        """
        # For readibitlity
        is_notch = self.has_notch(is_bore=is_bore)
        is_slot = self.has_slot(is_bore=is_bore)
        if is_bore:
            R = self.get_Rbo()
            is_shape = self.bore is not None
            shape_obj = self.bore
        else:
            R = self.get_Ryoke()
            is_shape = self.yoke is not None
            shape_obj = self.yoke

        if not is_shape:  # Arc or Slot/Notch only
            radius_desc_list = self.build_radius_desc(is_bore=is_bore, sym=sym)
            # Cut lines for sym
            if sym != 1:
                # Cut first desc (if needed)
                if radius_desc_list[0]["begin_angle"] < 0:
                    lines = list()
                    for line in radius_desc_list[0]["lines"]:
                        top_split_list, _ = line.split_line(0, 1)
                        lines.extend(top_split_list)
                    radius_desc_list[0]["begin_angle"] = 0
                    radius_desc_list[0]["lines"] = lines
                # Cut last desc (if needed)
                if radius_desc_list[-1]["end_angle"] > 2 * np.pi / sym:
                    lines = list()
                    for line in radius_desc_list[-1]["lines"]:
                        _, bot_split_list = line.split_line(
                            0, np.exp(1j * 2 * np.pi / sym)
                        )
                        lines.extend(bot_split_list)
                    radius_desc_list[-1]["end_angle"] = 2 * np.pi / sym
                    radius_desc_list[-1]["lines"] = lines
            # Extract the line list
            radius_lines = list()
            for desc_dict in radius_desc_list:
                # Apply prop_dict on Radius only
                if prop_dict is not None and desc_dict["label"] == "Radius":
                    for line in desc_dict["lines"]:
                        if line.prop_dict is None:
                            line.prop_dict = dict()
                        line.prop_dict.update(prop_dict)
                radius_lines.extend(desc_dict["lines"])

        elif is_shape and not is_notch and not is_slot:
            # Bore/Yoke shape only
            radius_lines = shape_obj.get_bore_line()
            if sym > 1:  # Ox cut
                lines = list()
                for line in radius_lines:
                    top_split_list, _ = line.split_line(0, 1)
                    lines.extend(top_split_list)
                radius_lines = lines
            if sym > 2:
                lines = list()
                for line in radius_lines:
                    _, bot_split_list = line.split_line(0, np.exp(1j * 2 * np.pi / sym))
                    lines.extend(bot_split_list)
                radius_lines = lines
            # Only radius lines => prop_dict on all lines
            if prop_dict is not None:
                for line in radius_lines:
                    if line.prop_dict is None:
                        line.prop_dict = dict()
                    line.prop_dict.update(prop_dict)
        else:  # Bore/Yoke shape to merge with slot/notch
            radius_desc_list = self.build_radius_desc(is_bore=is_bore, sym=sym)
            radius_lines = shape_obj.merge_slot(
                radius_desc_list, prop_dict=prop_dict, sym=sym
            )

        # Reverse the lines
        if is_reversed:
            radius_lines = radius_lines[::-1]
            for line in radius_lines:
                line.reverse()

        return radius_lines

    # cf Methods.Machine.Lamination.build_yoke_side_line
    def build_yoke_side_line(
        self,
        sym,
        vent_surf_list,
        ZBR=None,
        ZTR=None,
        ZBL=None,
        ZTL=None,
        *,
        DELTA=1e-06
    ):
        """Define the Yoke Side lines of a Lamination by taking into account sym and vent

        Parameters
        ----------
        self: Lamination
            a Lamination object
        sym : int
            Symmetry factor (1= full machine, 2= half of the machine...)
        vent_surf_list :
            List of the ventilation surfaces
        ZBR : Complex
            Yoke Side Limit point Bottom Right
        ZTR : Complex
            Yoke Side Limit point Top Right
        ZBL : Complex
            Yoke Side Limit point Bottom Left
        ZTL : Complex
            Yoke Side Limit point Top Left

        Returns
        -------
        right_list, left_list: ([Line], [Line])
            List of the lines to draw the left and right side of the yoke
        """

        # Find the ventilation lines that collide with the Yoke Side
        inter_line_list_R, inter_line_list_L = list(), list()
        for surf in vent_surf_list:
            for line in surf.get_lines():
                if (
                    line.prop_dict is not None
                    and BOUNDARY_PROP_LAB in line.prop_dict
                    and YS_LAB in line.prop_dict[BOUNDARY_PROP_LAB]
                ):
                    # Find if the line collide on right or left
                    if abs(np.angle(line.get_middle())) < DELTA:
                        inter_line_list_R.append(line)
                    else:
                        inter_line_list_L.append(line)

        # Yoke Limit point
        if ZBR is None:
            alpha = 2 * np.pi / sym
            ZBR = self.Rint
            ZTR = self.Rext
            ZBL = ZBR * np.exp(1j * alpha)
            ZTL = ZTR * np.exp(1j * alpha)

        lam_lab = self.get_label()
        if self.is_internal:
            right_list = merge_line_list(
                ZBR, ZTR, lam_lab + "_" + YSR_LAB, inter_line_list_R
            )
            left_list = merge_line_list(
                ZTL, ZBL, lam_lab + "_" + YSL_LAB, inter_line_list_L
            )
        else:
            left_list = merge_line_list(
                ZBL, ZTL, lam_lab + "_" + YSL_LAB, inter_line_list_L
            )
            right_list = merge_line_list(
                ZTR, ZBR, lam_lab + "_" + YSR_LAB, inter_line_list_R
            )

        return right_list, left_list

    # cf Methods.Machine.Lamination.check
    check = check

    # cf Methods.Machine.Lamination.comp_angle_q_axis
    def comp_angle_q_axis(self):
        """Compute the angle between the X axis and the first q+ axis
        By convention a "Tooth" is centered on the X axis
        By convention the first magnet is +

        Parameters
        ----------
        self : Lamination
            A Lamination object

        Returns
        -------
        d_angle : float
            angle between the X axis and the first d+ axis
        """

        q_angle = self.comp_angle_d_axis()
        p = self.get_pole_pair_number()
        return q_angle + np.pi / p / 2

    # cf Methods.Machine.Lamination.comp_height_yoke
    def comp_height_yoke(self):
        """Compute the yoke height

        Parameters
        ----------
        self : Lamination
            A Lamination object

        Returns
        -------
        Hy: float
            yoke height [m]

        """
        return self.Rext - self.Rint

    # cf Methods.Machine.Lamination.comp_length
    def comp_length(self):
        """Compute the total length of the Lamination (including radial
        ventilations duct)

        Parameters
        ----------
        self : Lamination
            A Lamination object

        Returns
        -------
        Lt: float
            Total Lenght of the Lamination [m]

        """
        if self.Nrvd is None or self.Wrvd is None:
            return self.L1
        else:
            return self.L1 + self.Nrvd * self.Wrvd

    # cf Methods.Machine.Lamination.comp_masses
    def comp_masses(self):
        """Compute the masses of the Lamination

        Parameters
        ----------
        self : Lamination
            A Lamination object

        Returns
        -------
        M_dict: dict
            Lamination mass dictionary (Mtot, Mlam, Mteeth, Myoke) [kg]

        """
        rho = self.mat_type.struct.rho
        V_dict = self.comp_volumes()

        M_dict = dict()
        M_dict["Myoke"] = V_dict["Vyoke"] * self.Kf1 * rho
        M_dict["Mteeth"] = V_dict["Vteeth"] * self.Kf1 * rho
        M_dict["Mlam"] = V_dict["Vlam"] * self.Kf1 * rho
        M_dict["Mtot"] = M_dict["Mlam"]

        return M_dict

    # cf Methods.Machine.Lamination.comp_output_geo
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

        output = OutGeoLam()
        output.name_phase = self.get_name_phase()
        output.BH_curve = self.mat_type.mag.get_BH()

        return output

    # cf Methods.Machine.Lamination.comp_periodicity_duct_spatial
    def comp_periodicity_duct_spatial(self, per_a, is_antiper_a):
        """Compute the periodity of the axial cooling ducts

        Parameters
        ----------
        self : Lamination
            A Lamination object
        per_a : int
            Number of spatial periodicities of the lamination
        is_antiper_a : bool
            True if an spatial anti-periodicity is possible after the periodicities

        Returns
        -------
        per_a : int
            Spatial periodicity of the lamination including ducts
        is_antiper_a : bool
            Spatial antiperidicity of the lamination including ducts
        """

        # No duct => no impact on sym
        if self.axial_vent in [None, list()]:
            self.axial_vent = list()
            return per_a, is_antiper_a

        # Compute duct periodicity
        per_d = self.axial_vent[0].Zh
        for duct in self.axial_vent[1:]:
            per_d = int(gcd(per_d, duct.Zh))

        # "Merge" lamination and duct periodicity
        if is_antiper_a:
            per = int(gcd(per_d, per_a * 2))
            if per == per_a * 2:  # No impact of vent
                pass
            elif per == per_a:  # Anti per removed
                is_antiper_a = False
            elif per_a % per == 0:
                per_a = per
                is_antiper_a = False
            elif per % 2 == 0:
                per_a = int(per / 2)
                is_antiper_a = True
            else:
                per_a = per
                is_antiper_a = False
        else:
            per_a = int(gcd(per_d, per_a))

        # if hasattr(self, "get_Zs") and hasattr(self, "get_pole_pair_number"):
        #     Zs = self.get_Zs()
        #     p = self.get_pole_pair_number()
        #     if per_a == 1:
        #         is_antiper_a = bool(Zs % 2 == 0)
        #     else:
        #         is_antiper_a = bool(Zs / p % 2 == 0)

        return per_a, is_antiper_a

    # cf Methods.Machine.Lamination.comp_periodicity_geo
    def comp_periodicity_geo(self):
        """Compute the geometric periodicity factor of the lamination

        Parameters
        ----------
        self : lamination
            A lamination object

        Returns
        -------
        per_a : int
            Number of spatial periodicities of the lamination
        is_antiper_a : bool
            True if an spatial anti-periodicity is possible after the periodicities
        """

        if hasattr(self, "get_Zs"):
            Zs = self.get_Zs()

            nb_list = [Zs]
            # account for notches and bore
            if self.notch is not None:
                for notch in self.notch:
                    nb_list.append(notch.comp_periodicity_spatial()[0])

            if self.bore:
                nb_list.append(self.bore.comp_periodicity_spatial()[0])
            if self.yoke:
                nb_list.append(self.yoke.comp_periodicity_spatial()[0])

            # compute the gcd of the list
            if len(nb_list) == 1:
                per_a = nb_list[0]
            else:
                per_a = np.gcd(nb_list[0], nb_list[1])
                for ii in range(2, len(nb_list)):
                    per_a = np.gcd(per_a, nb_list[ii])

            nb_list.pop(0)
            is_antiper_a = False

            # Account for duct periodicity
            per_a, is_antiper_a = self.comp_periodicity_duct_spatial(
                per_a, is_antiper_a
            )
            per_a = int(per_a)

        else:
            per_a = None
            is_antiper_a = False

        return per_a, is_antiper_a

    # cf Methods.Machine.Lamination.comp_periodicity_spatial
    def comp_periodicity_spatial(self):
        """Compute the periodicity factor of the lamination

        Parameters
        ----------
        self : lamination
            A lamination object

        Returns
        -------
        per_a : int
            Number of spatial periodicities of the lamination
        is_antiper_a : bool
            True if an spatial anti-periodicity is possible after the periodicities
        """

        if hasattr(self, "get_Zs") and hasattr(self, "get_pole_pair_number"):
            Zs = self.get_Zs()
            p = self.get_pole_pair_number()

            nb_list = [p, Zs]
            # account for notches and bore
            if self.notch is not None:
                for notch in self.notch:
                    nb_list.append(notch.comp_periodicity_spatial()[0])

            if self.bore:
                nb_list.append(self.bore.comp_periodicity_spatial()[0])
            if self.yoke:
                nb_list.append(self.yoke.comp_periodicity_spatial()[0])

            # compute the gcd of the list
            per_a = np.gcd(nb_list[0], nb_list[1])
            for ii in range(2, len(nb_list)):
                per_a = np.gcd(per_a, nb_list[ii])

            nb_list.pop(0)
            is_antiper_a = all([nb / per_a % 2 == 0 for nb in nb_list])

            # Account for duct periodicity
            per_a, is_antiper_a = self.comp_periodicity_duct_spatial(
                per_a, is_antiper_a
            )
            per_a = int(per_a)

        else:
            per_a = None
            is_antiper_a = False

        return per_a, is_antiper_a

    # cf Methods.Machine.Lamination.comp_point_ref
    def comp_point_ref(self, sym=1):
        """Compute coordinates of a point in the lamination
        to assign property in FEA software
        Account for slot, notches and ventilations (TODO)

        Parameters
        ----------
        self : Lamination
            Lamination Object
        sym : int
            Symmetry factor (1= full machine, 2= half of the machine...)

        Returns
        point_ref : complex
            Reference point of the lamination

        """

        Rref = self.comp_radius_mid_yoke()

        # Find a radius that doesn't match any ventilation
        if self.axial_vent not in [None, list()]:
            R1, R2 = Rref, Rref
            for vent in self.axial_vent:
                (Rmin, Rmax) = vent.comp_radius()
                R1 = min(R1, Rmin)
                R2 = max(R2, Rmax)
            if self.is_internal:
                Rref = (self.Rint + R1) / 2
            else:
                Rref = (self.Rext + R2) / 2

        # Find an angle without notches on the yoke
        if not self.has_notch(is_bore=False):
            angle = np.pi / sym
        else:
            yoke_desc_list = self.build_radius_desc(sym=sym, is_bore=False)
            ii = 0
            while (
                ii < len(yoke_desc_list)
                and yoke_desc_list[ii]["label"] != "Radius"
                and (
                    yoke_desc_list[ii]["begin_angle"] < yoke_desc_list[ii]["end_angle"]
                )
            ):
                ii += 1
            angle = (
                yoke_desc_list[ii]["begin_angle"] + yoke_desc_list[ii]["end_angle"]
            ) / 2

        return Rref * np.exp(1j * angle)

    # cf Methods.Machine.Lamination.comp_radius_mec
    def comp_radius_mec(self):
        """Compute the mechanical radius of the Lamination [m]

        Parameters
        ----------
        self : Lamination
            A Lamination object

        Returns
        -------
        Rmec: float
            Mechanical radius [m]

        """

        if self.is_internal:
            return self.Rext
        else:
            return self.Rint

    # cf Methods.Machine.Lamination.comp_radius_mid_yoke
    def comp_radius_mid_yoke(self):
        """Compute the Lamination middle of the yoke radius

        Parameters
        ----------
        self : Lamination
            A Lamination object

        Returns
        -------
        Ry: float
            middle of the yoke radius [m]

        """

        Hyoke = self.comp_height_yoke()
        if self.is_internal:
            return self.Rint + Hyoke / 2
        else:
            return self.Rext - Hyoke / 2

    # cf Methods.Machine.Lamination.comp_surface_axial_vent
    def comp_surface_axial_vent(self):
        """Compute the Lamination axial vent

        Parameters
        ----------
        self : Lamination
            A Lamination object

        Returns
        -------
        Svent: float
            Surface of the Lamination's axial ventilation [m**2]

        """

        if len(self.axial_vent) > 0:
            return sum([vent.comp_surface() * vent.Zh for vent in self.axial_vent])
        else:
            return 0

    # cf Methods.Machine.Lamination.comp_surfaces
    def comp_surfaces(self):
        """Compute the Lamination surface (Total, Vent).

        Parameters
        ----------
        self : Lamination
            A Lamination object

        Returns
        -------
        S_dict: dict
            Lamination surface dictionary (Slam, Svent, Syoke, Steeth, Sslot) [m**2]

        """
        if self.is_internal:
            ext_shape = self.bore
            int_shape = self.yoke
        else:
            ext_shape = self.yoke
            int_shape = self.bore

        # Surface of the external disk
        if ext_shape is not None:
            S_ext = ext_shape.comp_surface()
        else:
            S_ext = (self.Rext**2) * np.pi
        # Surface of the internal disk
        if int_shape is not None:
            S_int = int_shape.comp_surface()
        else:
            S_int = (self.Rint**2) * np.pi

        # Surface of lamination without hole
        Slam = S_ext - S_int

        # Surface of the ventilation ducts on the yoke
        Svent = self.comp_surface_axial_vent()

        # Compute notches surfaces
        Snotch = 0
        if self.notch is not None and len(self.notch) > 0:
            for notch in self.notch:
                Snotch += notch.comp_surface()

        return {
            "Slam": Slam - Svent - Snotch,
            "Svent": Svent,
            "Syoke": Slam,
            "Steeth": 0,
            "Sslot": 0,
            "Snotch": Snotch,
        }

    # cf Methods.Machine.Lamination.comp_volumes
    def comp_volumes(self):
        """Compute the volumes of the Lamination

        Parameters
        ----------
        self : Lamination
            A Lamination object

        Returns
        -------
        V_dict: dict
            Volume of the Lamination (Vlam, Vvent, Vyoke, Vteeth) [m**3]

        """

        Lf = self.comp_length()  # Include radial ventilation ducts

        S_dict = self.comp_surfaces()
        Vvent = Lf * S_dict["Svent"]
        # L1 is without ventilation ducts (volume to compute masses)
        Vlam = self.L1 * S_dict["Slam"]
        Vyoke = self.L1 * S_dict["Syoke"]
        Vteeth = self.L1 * S_dict["Steeth"]
        return {"Vlam": Vlam, "Vvent": Vvent, "Vyoke": Vyoke, "Vteeth": Vteeth}

    # cf Methods.Machine.Lamination.get_label
    def get_label(self, is_add_id=True):
        """Return the label of the lamination (Stator-0 for instance)

        Parameters
        ----------
        self : Lamination
            a Lamination object
        is_add_id : bool
            True to add the "-X" part

        Returns
        -------
        label : str
            Label of the lamination

        """

        if self.is_stator:
            label = STATOR_LAB
        else:
            label = ROTOR_LAB

        if is_add_id:
            if self.parent is not None:
                try:
                    lam_list = self.parent.get_lam_list(is_int_to_ext=True, key=label)
                    label += "-" + str(lam_list.index(self))
                except:
                    pass
            # else:
            #     raise ParentMissingError("Error: The slot is not inside a Lamination")

        return label

    # cf Methods.Machine.Lamination.get_name_phase
    def get_name_phase(self):
        """Return the name of the winding phases

        Parameters
        ----------
        self : Lamination
            A Lamination object

        Returns
        -------
        name_phase: list
            Empty list

        """
        if (
            not hasattr(self, "winding")
            or self.winding is None
            # or self.winding.conductor is None
        ):
            return list()
        return gen_name(self.winding.qs)

    # cf Methods.Machine.Lamination.get_notches_surf
    def get_notches_surf(self, sym):
        """Return the list of surfaces for notches

        Parameters
        ----------
        self : Lamination
            A Lamination object
        sym : int
            Symmetry factor (1= full machine, 2= half of the machine...)

        Return
        ------
        surf_list : list
            list of surfaces needed for the notches
        """

        if self.notch is None:
            self.notch = list()

        # Get all the notch on the bore radius
        notch_list = [notch for notch in self.notch if notch.notch_shape.is_bore]
        if len(notch_list) == 0:
            return list()

        surf_list = list()
        for ii, notch in enumerate(notch_list):
            # Method used for symetry (for now) so only NotchEvenDist
            assert isinstance(notch, NotchEvenDist)
            if notch.has_key():
                continue  # Key surface overlap closing surface
            # Get the original surface
            Nsurf = notch.notch_shape.get_surface()
            Nsurf.label = self.get_label() + "_" + NOTCH_LAB + "_R" + str(ii) + "-T0-S0"
            Nsurf.rotate(angle=notch.alpha)
            # Label definition
            BC_prop_right = self.get_label() + "_" + YSNR_LAB
            BC_prop_left = self.get_label() + "_" + YSNL_LAB
            # Generate all the surfaces (handle cut on sym axis)
            surf_list.extend(
                transform_hole_surf(
                    hole_surf_list=[Nsurf],
                    Zh=notch.notch_shape.Zs,
                    sym=sym,
                    alpha=0,
                    delta=0,
                    is_split=True,
                    BC_prop_right=BC_prop_right,
                    BC_prop_left=BC_prop_left,
                )
            )

        return surf_list

    # cf Methods.Machine.Lamination.get_polar_eq
    def get_polar_eq(self):
        """Returns a polar equivalent of the lamination

        Parameters
        ----------
        self : Lamination
            Lamination object

        Returns
        -------
        polar_eq: Lamination
            The polar equivalent of the lamination
        """

        raise NotImplementedYetError(
            "get_polar_eq available only for LamSlotWind for now"
        )

    # cf Methods.Machine.Lamination.get_Rbo
    def get_Rbo(self):
        """Return the bore lamination radius

        Parameters
        ----------
        self : Lamination
            A Lamination object

        Returns
        -------
        Rbo: float
            The lamination bore radius [m]

        """

        if self.is_internal:
            return self.Rext
        else:
            return self.Rint

    # cf Methods.Machine.Lamination.get_Ryoke
    def get_Ryoke(self):
        """Return the yoke lamination radius

        Parameters
        ----------
        self : Lamination
            A Lamination object

        Returns
        -------
        Ryoke: float
            The lamination yoke radius [m]

        """

        if self.is_internal:
            return self.Rint
        else:
            return self.Rext

    # cf Methods.Machine.Lamination.get_surfaces_closing
    def get_surfaces_closing(self, sym=1):
        """Return the surfaces needed to close the radii of the Lamination

        Parameters
        ----------
        self : Lamination
            A Lamination object
        sym : int
            Symmetry factor (1= full machine, 2= half of the machine...)

        Returns
        -------
        surf_list : list
            List of the closing surfaces
        """

        # No notch when bore shape
        if self.bore is None:
            return self.get_notches_surf(sym=sym)
        else:
            return list()

    # cf Methods.Machine.Lamination.has_key
    def has_key(self):
        """Check if a there is key in the Lamination

        Parameters
        ----------
        self : Lamination
            A Lamination object

        Returns
        -------
        has_key : bool
            True if the Lamination has at least one key
        """

        if self.notch is None:
            return False
        return any([notch.has_key() for notch in self.notch])

    # cf Methods.Machine.Lamination.has_notch
    def has_notch(self, is_bore):
        """Check if notches are set on the requested radius

        Parameters
        ----------
        self : Lamination
            A Lamination object
        is_bore : bool
            True check notch on bore radius, else on yoke

        Returns
        -------
        has_notch : bool
            True if notches are set on the requested radius
        """

        if self.notch is None or len(self.notch) == 0:
            return False

        # notch_shape.is_bore = None => Default is True
        if is_bore:
            return any(
                [notch.notch_shape.is_bore in [True, None] for notch in self.notch]
            )
        else:
            return any([notch.notch_shape.is_bore == False for notch in self.notch])

    # cf Methods.Machine.Lamination.has_slot
    def has_slot(self, is_bore=True):
        """Return if the lamination has slot on the requested radius
        (notches not taken into account, cf has_notch)

        Parameters
        ----------
        self : Lamination
            A Lamination object
        is_bore : bool
            True check if there are slots on the bore, else yoke

        Returns
        -------
        has_slot : bool
            True if the lamination has slot on the requested radius
        """

        return False

    # cf Methods.Machine.Lamination.is_outwards
    def is_outwards(self):
        """Return if the slot is outwards (on an external lamination) or inwards
        (on an internal lamination)

        Parameters
        ----------
        self : Slot
            A Slot object

        Returns
        -------
        is_outwards: bool
            True if the Lamination is not internal and false if not
        """
        return not self.is_internal

    # cf Methods.Machine.Lamination.plot
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
        is_show_fig=True,
        save_path=None,
        is_winding_connection=False,
    ):
        """Plot the Lamination in a matplotlib fig

        Parameters
        ----------
        self : Lamination
            A Lamination object
        fig : Matplotlib.figure.Figure
            existing figure to use if None create a new one
        ax : Matplotlib.axes.Axes object
            Axis on which to plot the data
        is_lam_only: bool
            True to plot only the lamination (no effect for Lamination object)
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
        is_show_fig : bool
            To call show at the end of the method
        save_path : str
            full path including folder, name and extension of the file to save if save_path is not None
        is_winding_connection : bool
            True to display winding connections (not used)

        Returns
        -------
        fig : Matplotlib.figure.Figure
            Figure containing the plot
        ax : Matplotlib.axes.Axes object
            Axis containing the plot
        """
        (fig, ax, patch_leg, label_leg) = init_fig(fig=fig, ax=ax, shape="rectangle")

        surf_list = self.build_geometry(sym=sym, alpha=alpha, delta=delta)
        patches = list()

        # Color Selection for Surfaces
        for surf in surf_list:
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

        # Display the result
        ax.set_xlabel("(m)")
        ax.set_ylabel("(m)")
        for patch in patches:
            ax.add_patch(patch)

        # Axis Setup
        ax.axis("equal")

        # The Lamination is centered in the figure
        Lim = self.Rext * 1.5
        ax.set_xlim(-Lim, Lim)
        ax.set_ylim(-Lim, Lim)

        title = None

        # Adding legend
        if not is_edge_only:
            if self.is_stator:
                title = "Stator without slot"
            else:
                title = "Rotor without slot"
            ax.set_title(title)
            ax.legend(patch_leg, label_leg)
        if is_show_fig:
            fig.show()
        if save_path is not None:
            fig.savefig(save_path)
            plt.close(fig=fig)
        return fig, ax

    # cf Methods.Machine.Lamination.plot_preview_notch
    def plot_preview_notch(self, index, fig=None, ax=None):
        """Preview the position/shape of a notch on the lamination

        Parameters
        ----------
        self : Lamination
            Lamination object
        index : int
            Index of the notch to preview
        fig : Matplotlib.figure.Figure
            existing figure to use if None create a new one
        ax : Matplotlib.axes.Axes object
            Axis on which to plot the data

        Returns
        -------
        fig : Matplotlib.figure.Figure
            Figure containing the plot
        ax : Matplotlib.axes.Axes object
            Axis containing the plot
        """

        if self.notch is None:
            raise Exception("No notch set")
        if index > len(self.notch) - 1:
            raise Exception(
                "Requested notch index "
                + str(index)
                + ", "
                + str(len(self.notch))
                + " notches were set"
            )
        # Plot the original lamination without notches
        lam = self.copy()
        lam.notch = list()

        fig, ax = lam.plot(
            fig=fig,
            ax=ax,
            is_lam_only=True,
        )

        # Create equivalent LamSlot with notch as slot
        LamSlot = import_class("pyleecan.Classes", "LamSlot")
        lam_notch = LamSlot(
            is_stator=lam.is_stator,
            is_internal=lam.is_internal,
            Rint=lam.Rint,
            Rext=lam.Rext,
            slot=self.notch[index].notch_shape,
        )
        fig, ax = lam_notch.plot(
            fig=fig,
            ax=ax,
            is_edge_only=True,
            edgecolor="r--",
            alpha=-np.pi / self.notch[index].notch_shape.Zs + self.notch[index].alpha,
        )
        # Setup legend
        if self.is_stator:
            name = "Stator"
            color = self.STATOR_COLOR
        else:
            name = "Rotor"
            color = self.ROTOR_COLOR
        patch_leg = [
            Patch(facecolor=color, edgecolor="k"),
            Patch(facecolor=self.PATCH_COLOR_ALPHA, edgecolor="r", linestyle="--"),
        ]
        label_leg = ["Current " + name, "Notches"]
        ax.set_axis_off()
        ax.legend(patch_leg, label_leg)

        return fig, ax

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
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
        self.parent = None
        self.L1 = L1
        self.mat_type = mat_type
        self.Nrvd = Nrvd
        self.Wrvd = Wrvd
        self.Kf1 = Kf1
        self.is_internal = is_internal
        self.Rint = Rint
        self.Rext = Rext
        self.is_stator = is_stator
        self.axial_vent = axial_vent
        self.notch = notch
        self.skew = skew
        self.bore = bore
        self.yoke = yoke

        # The class is frozen, for now it's impossible to add new properties
        self._freeze()

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        Lamination_str = ""
        if self.parent is None:
            Lamination_str += "parent = None " + linesep
        else:
            Lamination_str += "parent = " + str(type(self.parent)) + " object" + linesep
        Lamination_str += "L1 = " + str(self.L1) + linesep
        if self.mat_type is not None:
            tmp = self.mat_type.__str__().replace(linesep, linesep + "\t").rstrip("\t")
            Lamination_str += "mat_type = " + tmp
        else:
            Lamination_str += "mat_type = None" + linesep + linesep
        Lamination_str += "Nrvd = " + str(self.Nrvd) + linesep
        Lamination_str += "Wrvd = " + str(self.Wrvd) + linesep
        Lamination_str += "Kf1 = " + str(self.Kf1) + linesep
        Lamination_str += "is_internal = " + str(self.is_internal) + linesep
        Lamination_str += "Rint = " + str(self.Rint) + linesep
        Lamination_str += "Rext = " + str(self.Rext) + linesep
        Lamination_str += "is_stator = " + str(self.is_stator) + linesep
        if len(self.axial_vent) == 0:
            Lamination_str += "axial_vent = []" + linesep
        for ii in range(len(self.axial_vent)):
            tmp = (
                self.axial_vent[ii].__str__().replace(linesep, linesep + "\t") + linesep
            )
            Lamination_str += "axial_vent[" + str(ii) + "] =" + tmp + linesep + linesep
        if len(self.notch) == 0:
            Lamination_str += "notch = []" + linesep
        for ii in range(len(self.notch)):
            tmp = self.notch[ii].__str__().replace(linesep, linesep + "\t") + linesep
            Lamination_str += "notch[" + str(ii) + "] =" + tmp + linesep + linesep
        if self.skew is not None:
            tmp = self.skew.__str__().replace(linesep, linesep + "\t").rstrip("\t")
            Lamination_str += "skew = " + tmp
        else:
            Lamination_str += "skew = None" + linesep + linesep
        if self.bore is not None:
            tmp = self.bore.__str__().replace(linesep, linesep + "\t").rstrip("\t")
            Lamination_str += "bore = " + tmp
        else:
            Lamination_str += "bore = None" + linesep + linesep
        if self.yoke is not None:
            tmp = self.yoke.__str__().replace(linesep, linesep + "\t").rstrip("\t")
            Lamination_str += "yoke = " + tmp
        else:
            Lamination_str += "yoke = None" + linesep + linesep
        return Lamination_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False
        if other.L1 != self.L1:
            return False
        if other.mat_type != self.mat_type:
            return False
        if other.Nrvd != self.Nrvd:
            return False
        if other.Wrvd != self.Wrvd:
            return False
        if other.Kf1 != self.Kf1:
            return False
        if other.is_internal != self.is_internal:
            return False
        if other.Rint != self.Rint:
            return False
        if other.Rext != self.Rext:
            return False
        if other.is_stator != self.is_stator:
            return False
        if other.axial_vent != self.axial_vent:
            return False
        if other.notch != self.notch:
            return False
        if other.skew != self.skew:
            return False
        if other.bore != self.bore:
            return False
        if other.yoke != self.yoke:
            return False
        return True

    def compare(self, other, name="self", ignore_list=None, is_add_value=False):
        """Compare two objects and return list of differences"""

        if ignore_list is None:
            ignore_list = list()
        if type(other) != type(self):
            return ["type(" + name + ")"]
        diff_list = list()
        if (
            other._L1 is not None
            and self._L1 is not None
            and np.isnan(other._L1)
            and np.isnan(self._L1)
        ):
            pass
        elif other._L1 != self._L1:
            if is_add_value:
                val_str = " (self=" + str(self._L1) + ", other=" + str(other._L1) + ")"
                diff_list.append(name + ".L1" + val_str)
            else:
                diff_list.append(name + ".L1")
        if (other.mat_type is None and self.mat_type is not None) or (
            other.mat_type is not None and self.mat_type is None
        ):
            diff_list.append(name + ".mat_type None mismatch")
        elif self.mat_type is not None:
            diff_list.extend(
                self.mat_type.compare(
                    other.mat_type,
                    name=name + ".mat_type",
                    ignore_list=ignore_list,
                    is_add_value=is_add_value,
                )
            )
        if other._Nrvd != self._Nrvd:
            if is_add_value:
                val_str = (
                    " (self=" + str(self._Nrvd) + ", other=" + str(other._Nrvd) + ")"
                )
                diff_list.append(name + ".Nrvd" + val_str)
            else:
                diff_list.append(name + ".Nrvd")
        if (
            other._Wrvd is not None
            and self._Wrvd is not None
            and np.isnan(other._Wrvd)
            and np.isnan(self._Wrvd)
        ):
            pass
        elif other._Wrvd != self._Wrvd:
            if is_add_value:
                val_str = (
                    " (self=" + str(self._Wrvd) + ", other=" + str(other._Wrvd) + ")"
                )
                diff_list.append(name + ".Wrvd" + val_str)
            else:
                diff_list.append(name + ".Wrvd")
        if (
            other._Kf1 is not None
            and self._Kf1 is not None
            and np.isnan(other._Kf1)
            and np.isnan(self._Kf1)
        ):
            pass
        elif other._Kf1 != self._Kf1:
            if is_add_value:
                val_str = (
                    " (self=" + str(self._Kf1) + ", other=" + str(other._Kf1) + ")"
                )
                diff_list.append(name + ".Kf1" + val_str)
            else:
                diff_list.append(name + ".Kf1")
        if other._is_internal != self._is_internal:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._is_internal)
                    + ", other="
                    + str(other._is_internal)
                    + ")"
                )
                diff_list.append(name + ".is_internal" + val_str)
            else:
                diff_list.append(name + ".is_internal")
        if (
            other._Rint is not None
            and self._Rint is not None
            and np.isnan(other._Rint)
            and np.isnan(self._Rint)
        ):
            pass
        elif other._Rint != self._Rint:
            if is_add_value:
                val_str = (
                    " (self=" + str(self._Rint) + ", other=" + str(other._Rint) + ")"
                )
                diff_list.append(name + ".Rint" + val_str)
            else:
                diff_list.append(name + ".Rint")
        if (
            other._Rext is not None
            and self._Rext is not None
            and np.isnan(other._Rext)
            and np.isnan(self._Rext)
        ):
            pass
        elif other._Rext != self._Rext:
            if is_add_value:
                val_str = (
                    " (self=" + str(self._Rext) + ", other=" + str(other._Rext) + ")"
                )
                diff_list.append(name + ".Rext" + val_str)
            else:
                diff_list.append(name + ".Rext")
        if other._is_stator != self._is_stator:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._is_stator)
                    + ", other="
                    + str(other._is_stator)
                    + ")"
                )
                diff_list.append(name + ".is_stator" + val_str)
            else:
                diff_list.append(name + ".is_stator")
        if (other.axial_vent is None and self.axial_vent is not None) or (
            other.axial_vent is not None and self.axial_vent is None
        ):
            diff_list.append(name + ".axial_vent None mismatch")
        elif self.axial_vent is None:
            pass
        elif len(other.axial_vent) != len(self.axial_vent):
            diff_list.append("len(" + name + ".axial_vent)")
        else:
            for ii in range(len(other.axial_vent)):
                diff_list.extend(
                    self.axial_vent[ii].compare(
                        other.axial_vent[ii],
                        name=name + ".axial_vent[" + str(ii) + "]",
                        ignore_list=ignore_list,
                        is_add_value=is_add_value,
                    )
                )
        if (other.notch is None and self.notch is not None) or (
            other.notch is not None and self.notch is None
        ):
            diff_list.append(name + ".notch None mismatch")
        elif self.notch is None:
            pass
        elif len(other.notch) != len(self.notch):
            diff_list.append("len(" + name + ".notch)")
        else:
            for ii in range(len(other.notch)):
                diff_list.extend(
                    self.notch[ii].compare(
                        other.notch[ii],
                        name=name + ".notch[" + str(ii) + "]",
                        ignore_list=ignore_list,
                        is_add_value=is_add_value,
                    )
                )
        if (other.skew is None and self.skew is not None) or (
            other.skew is not None and self.skew is None
        ):
            diff_list.append(name + ".skew None mismatch")
        elif self.skew is not None:
            diff_list.extend(
                self.skew.compare(
                    other.skew,
                    name=name + ".skew",
                    ignore_list=ignore_list,
                    is_add_value=is_add_value,
                )
            )
        if (other.bore is None and self.bore is not None) or (
            other.bore is not None and self.bore is None
        ):
            diff_list.append(name + ".bore None mismatch")
        elif self.bore is not None:
            diff_list.extend(
                self.bore.compare(
                    other.bore,
                    name=name + ".bore",
                    ignore_list=ignore_list,
                    is_add_value=is_add_value,
                )
            )
        if (other.yoke is None and self.yoke is not None) or (
            other.yoke is not None and self.yoke is None
        ):
            diff_list.append(name + ".yoke None mismatch")
        elif self.yoke is not None:
            diff_list.extend(
                self.yoke.compare(
                    other.yoke,
                    name=name + ".yoke",
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
        S += getsizeof(self.L1)
        S += getsizeof(self.mat_type)
        S += getsizeof(self.Nrvd)
        S += getsizeof(self.Wrvd)
        S += getsizeof(self.Kf1)
        S += getsizeof(self.is_internal)
        S += getsizeof(self.Rint)
        S += getsizeof(self.Rext)
        S += getsizeof(self.is_stator)
        if self.axial_vent is not None:
            for value in self.axial_vent:
                S += getsizeof(value)
        if self.notch is not None:
            for value in self.notch:
                S += getsizeof(value)
        S += getsizeof(self.skew)
        S += getsizeof(self.bore)
        S += getsizeof(self.yoke)
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

        Lamination_dict = dict()
        Lamination_dict["L1"] = self.L1
        if self.mat_type is None:
            Lamination_dict["mat_type"] = None
        else:
            Lamination_dict["mat_type"] = self.mat_type.as_dict(
                type_handle_ndarray=type_handle_ndarray,
                keep_function=keep_function,
                **kwargs
            )
        Lamination_dict["Nrvd"] = self.Nrvd
        Lamination_dict["Wrvd"] = self.Wrvd
        Lamination_dict["Kf1"] = self.Kf1
        Lamination_dict["is_internal"] = self.is_internal
        Lamination_dict["Rint"] = self.Rint
        Lamination_dict["Rext"] = self.Rext
        Lamination_dict["is_stator"] = self.is_stator
        if self.axial_vent is None:
            Lamination_dict["axial_vent"] = None
        else:
            Lamination_dict["axial_vent"] = list()
            for obj in self.axial_vent:
                if obj is not None:
                    Lamination_dict["axial_vent"].append(
                        obj.as_dict(
                            type_handle_ndarray=type_handle_ndarray,
                            keep_function=keep_function,
                            **kwargs
                        )
                    )
                else:
                    Lamination_dict["axial_vent"].append(None)
        if self.notch is None:
            Lamination_dict["notch"] = None
        else:
            Lamination_dict["notch"] = list()
            for obj in self.notch:
                if obj is not None:
                    Lamination_dict["notch"].append(
                        obj.as_dict(
                            type_handle_ndarray=type_handle_ndarray,
                            keep_function=keep_function,
                            **kwargs
                        )
                    )
                else:
                    Lamination_dict["notch"].append(None)
        if self.skew is None:
            Lamination_dict["skew"] = None
        else:
            Lamination_dict["skew"] = self.skew.as_dict(
                type_handle_ndarray=type_handle_ndarray,
                keep_function=keep_function,
                **kwargs
            )
        if self.bore is None:
            Lamination_dict["bore"] = None
        else:
            Lamination_dict["bore"] = self.bore.as_dict(
                type_handle_ndarray=type_handle_ndarray,
                keep_function=keep_function,
                **kwargs
            )
        if self.yoke is None:
            Lamination_dict["yoke"] = None
        else:
            Lamination_dict["yoke"] = self.yoke.as_dict(
                type_handle_ndarray=type_handle_ndarray,
                keep_function=keep_function,
                **kwargs
            )
        # The class name is added to the dict for deserialisation purpose
        Lamination_dict["__class__"] = "Lamination"
        return Lamination_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
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

        self.L1 = None
        if self.mat_type is not None:
            self.mat_type._set_None()
        self.Nrvd = None
        self.Wrvd = None
        self.Kf1 = None
        self.is_internal = None
        self.Rint = None
        self.Rext = None
        self.is_stator = None
        self.axial_vent = None
        self.notch = None
        if self.skew is not None:
            self.skew._set_None()
        if self.bore is not None:
            self.bore._set_None()
        if self.yoke is not None:
            self.yoke._set_None()

    def _get_L1(self):
        """getter of L1"""
        return self._L1

    def _set_L1(self, value):
        """setter of L1"""
        check_var("L1", value, "float", Vmin=0)
        self._L1 = value

    L1 = property(
        fget=_get_L1,
        fset=_set_L1,
        doc="""Lamination stack active length without radial ventilation airducts but including insulation layers between lamination sheets

        :Type: float
        :min: 0
        """,
    )

    def _get_mat_type(self):
        """getter of mat_type"""
        return self._mat_type

    def _set_mat_type(self, value):
        """setter of mat_type"""
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
                "pyleecan.Classes", value.get("__class__"), "mat_type"
            )
            value = class_obj(init_dict=value)
        elif type(value) is int and value == -1:  # Default constructor
            Material = import_class("pyleecan.Classes", "Material", "mat_type")
            value = Material()
        check_var("mat_type", value, "Material")
        self._mat_type = value

        if self._mat_type is not None:
            self._mat_type.parent = self

    mat_type = property(
        fget=_get_mat_type,
        fset=_set_mat_type,
        doc="""Lamination's material

        :Type: Material
        """,
    )

    def _get_Nrvd(self):
        """getter of Nrvd"""
        return self._Nrvd

    def _set_Nrvd(self, value):
        """setter of Nrvd"""
        check_var("Nrvd", value, "int", Vmin=0)
        self._Nrvd = value

    Nrvd = property(
        fget=_get_Nrvd,
        fset=_set_Nrvd,
        doc="""number of radial air ventilation ducts in lamination

        :Type: int
        :min: 0
        """,
    )

    def _get_Wrvd(self):
        """getter of Wrvd"""
        return self._Wrvd

    def _set_Wrvd(self, value):
        """setter of Wrvd"""
        check_var("Wrvd", value, "float", Vmin=0)
        self._Wrvd = value

    Wrvd = property(
        fget=_get_Wrvd,
        fset=_set_Wrvd,
        doc="""axial width of ventilation ducts in lamination

        :Type: float
        :min: 0
        """,
    )

    def _get_Kf1(self):
        """getter of Kf1"""
        return self._Kf1

    def _set_Kf1(self, value):
        """setter of Kf1"""
        check_var("Kf1", value, "float", Vmin=0, Vmax=1)
        self._Kf1 = value

    Kf1 = property(
        fget=_get_Kf1,
        fset=_set_Kf1,
        doc="""lamination stacking / packing factor

        :Type: float
        :min: 0
        :max: 1
        """,
    )

    def _get_is_internal(self):
        """getter of is_internal"""
        return self._is_internal

    def _set_is_internal(self, value):
        """setter of is_internal"""
        check_var("is_internal", value, "bool")
        self._is_internal = value

    is_internal = property(
        fget=_get_is_internal,
        fset=_set_is_internal,
        doc="""1 for internal lamination topology, 0 for external lamination

        :Type: bool
        """,
    )

    def _get_Rint(self):
        """getter of Rint"""
        return self._Rint

    def _set_Rint(self, value):
        """setter of Rint"""
        check_var("Rint", value, "float", Vmin=0)
        self._Rint = value

    Rint = property(
        fget=_get_Rint,
        fset=_set_Rint,
        doc="""To fill

        :Type: float
        :min: 0
        """,
    )

    def _get_Rext(self):
        """getter of Rext"""
        return self._Rext

    def _set_Rext(self, value):
        """setter of Rext"""
        check_var("Rext", value, "float", Vmin=0)
        self._Rext = value

    Rext = property(
        fget=_get_Rext,
        fset=_set_Rext,
        doc="""To fill

        :Type: float
        :min: 0
        """,
    )

    def _get_is_stator(self):
        """getter of is_stator"""
        return self._is_stator

    def _set_is_stator(self, value):
        """setter of is_stator"""
        check_var("is_stator", value, "bool")
        self._is_stator = value

    is_stator = property(
        fget=_get_is_stator,
        fset=_set_is_stator,
        doc="""To fill

        :Type: bool
        """,
    )

    def _get_axial_vent(self):
        """getter of axial_vent"""
        if self._axial_vent is not None:
            for obj in self._axial_vent:
                if obj is not None:
                    obj.parent = self
        return self._axial_vent

    def _set_axial_vent(self, value):
        """setter of axial_vent"""
        if type(value) is list:
            for ii, obj in enumerate(value):
                if isinstance(obj, str):  # Load from file
                    try:
                        obj = load_init_dict(obj)[1]
                    except Exception as e:
                        self.get_logger().error(
                            "Error while loading " + obj + ", setting None instead"
                        )
                        obj = None
                        value[ii] = None
                if type(obj) is dict:
                    class_obj = import_class(
                        "pyleecan.Classes", obj.get("__class__"), "axial_vent"
                    )
                    value[ii] = class_obj(init_dict=obj)
                if value[ii] is not None:
                    value[ii].parent = self
        if value == -1:
            value = list()
        check_var("axial_vent", value, "[Hole]")
        self._axial_vent = value

    axial_vent = property(
        fget=_get_axial_vent,
        fset=_set_axial_vent,
        doc="""Axial ventilation ducts

        :Type: [Hole]
        """,
    )

    def _get_notch(self):
        """getter of notch"""
        if self._notch is not None:
            for obj in self._notch:
                if obj is not None:
                    obj.parent = self
        return self._notch

    def _set_notch(self, value):
        """setter of notch"""
        if type(value) is list:
            for ii, obj in enumerate(value):
                if isinstance(obj, str):  # Load from file
                    try:
                        obj = load_init_dict(obj)[1]
                    except Exception as e:
                        self.get_logger().error(
                            "Error while loading " + obj + ", setting None instead"
                        )
                        obj = None
                        value[ii] = None
                if type(obj) is dict:
                    class_obj = import_class(
                        "pyleecan.Classes", obj.get("__class__"), "notch"
                    )
                    value[ii] = class_obj(init_dict=obj)
                if value[ii] is not None:
                    value[ii].parent = self
        if value == -1:
            value = list()
        check_var("notch", value, "[Notch]")
        self._notch = value

    notch = property(
        fget=_get_notch,
        fset=_set_notch,
        doc="""Lamination bore notches

        :Type: [Notch]
        """,
    )

    def _get_skew(self):
        """getter of skew"""
        return self._skew

    def _set_skew(self, value):
        """setter of skew"""
        if isinstance(value, str):  # Load from file
            try:
                value = load_init_dict(value)[1]
            except Exception as e:
                self.get_logger().error(
                    "Error while loading " + value + ", setting None instead"
                )
                value = None
        if isinstance(value, dict) and "__class__" in value:
            class_obj = import_class("pyleecan.Classes", value.get("__class__"), "skew")
            value = class_obj(init_dict=value)
        elif type(value) is int and value == -1:  # Default constructor
            Skew = import_class("pyleecan.Classes", "Skew", "skew")
            value = Skew()
        check_var("skew", value, "Skew")
        self._skew = value

        if self._skew is not None:
            self._skew.parent = self

    skew = property(
        fget=_get_skew,
        fset=_set_skew,
        doc="""Skew object

        :Type: Skew
        """,
    )

    def _get_bore(self):
        """getter of bore"""
        return self._bore

    def _set_bore(self, value):
        """setter of bore"""
        if isinstance(value, str):  # Load from file
            try:
                value = load_init_dict(value)[1]
            except Exception as e:
                self.get_logger().error(
                    "Error while loading " + value + ", setting None instead"
                )
                value = None
        if isinstance(value, dict) and "__class__" in value:
            class_obj = import_class("pyleecan.Classes", value.get("__class__"), "bore")
            value = class_obj(init_dict=value)
        elif type(value) is int and value == -1:  # Default constructor
            Bore = import_class("pyleecan.Classes", "Bore", "bore")
            value = Bore()
        check_var("bore", value, "Bore")
        self._bore = value

        if self._bore is not None:
            self._bore.parent = self

    bore = property(
        fget=_get_bore,
        fset=_set_bore,
        doc="""Bore Shape

        :Type: Bore
        """,
    )

    def _get_yoke(self):
        """getter of yoke"""
        return self._yoke

    def _set_yoke(self, value):
        """setter of yoke"""
        if isinstance(value, str):  # Load from file
            try:
                value = load_init_dict(value)[1]
            except Exception as e:
                self.get_logger().error(
                    "Error while loading " + value + ", setting None instead"
                )
                value = None
        if isinstance(value, dict) and "__class__" in value:
            class_obj = import_class("pyleecan.Classes", value.get("__class__"), "yoke")
            value = class_obj(init_dict=value)
        elif type(value) is int and value == -1:  # Default constructor
            Bore = import_class("pyleecan.Classes", "Bore", "yoke")
            value = Bore()
        check_var("yoke", value, "Bore")
        self._yoke = value

        if self._yoke is not None:
            self._yoke.parent = self

    yoke = property(
        fget=_get_yoke,
        fset=_set_yoke,
        doc="""Yoke Shape

        :Type: Bore
        """,
    )
