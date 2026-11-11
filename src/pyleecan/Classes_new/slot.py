# Experimental dataclass generated from Generator/ClassesRef/Slot/Slot.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass, field

import numpy as np
from matplotlib.patches import Patch, Polygon

from ..definitions import config_dict
from ..Functions_new.init_fig import init_fig
from ..Functions_new.labels import (
    BORE_LAB,
    BOUNDARY_PROP_LAB,
    DRAW_PROP_LAB,
    NO_LAM_LAB,
    TOOTH_LAB,
    WEDGE_LAB,
    WIND_LAB,
    YOKE_LAB,
    YSL_LAB,
    YSR_LAB,
)
from ..Functions_new.Plot import dict_2D
from ..Functions_new.Winding.gen_phase_list import gen_name
from ._error import ParentMissingError
from ._import import import_class
from ._pyleecan_class import PyleecanClass
from .arc_1 import Arc1
from .material import Material
from .segment import Segment
from .surf_line import SurfLine


@dataclass(eq=False)
class Slot(PyleecanClass):
    """Generic class for slot (abstract)

    Attributes
    ----------
    Zs : int
        slot number
        Default: 36; Minimum: 0
    wedge_mat : Material or None
        Material for the wedge, if None no wedge
        Default: None
    is_bore : bool
        True if the Slot is on the bore radius, False for yoke
        Default: True
    """

    ROTOR_COLOR = config_dict["PLOT"]["COLOR_DICT"]["ROTOR_COLOR"]
    STATOR_COLOR = config_dict["PLOT"]["COLOR_DICT"]["STATOR_COLOR"]
    PHASE_COLORS = config_dict["PLOT"]["COLOR_DICT"]["PHASE_COLORS"]
    WEDGE_COLOR = config_dict["PLOT"]["COLOR_DICT"]["WEDGE_COLOR"]
    Zs: int = 36
    """slot number"""
    wedge_mat: Material | None = field(
        default=None, metadata={"default_class": "Material"}
    )
    """Material for the wedge, if None no wedge"""
    is_bore: bool = True
    """True if the Slot is on the bore radius, False for yoke"""

    # Inlined from Methods.Slot.Slot.build_geometry_active
    def build_geometry_active(self, Nrad, Ntan, alpha=0, delta=0):
        """Split the slot active area in several zone
        This method assume that the active area is centered on X axis and symetrical
        Otherwise a dedicated build_geometry_active method must be provided

        Parameters
        ----------
        self : Slot
            A Slot object
        Nrad : int
            Number of radial layer
        Ntan : int
            Number of tangentiel layer
        alpha : float
            Angle for rotation (Default value = 0) [rad]
        delta : Complex
            complex for translation (Default value = 0)

        Returns
        -------
        surf_list:
            List of surface delimiting the active zone

        """

        assert Ntan in [1, 2]

        surf_act = self.get_surface_active()

        # Find the two intersection point with Ox axis
        inter_list = []
        for line in surf_act.get_lines():
            inter_list.extend(line.intersect_line(0, 100))
        # Remove/Merge intersection that are too close
        duplicate_list = []
        for ii in range(len(inter_list)):
            for jj in range(ii + 1, len(inter_list)):  # Avoid comparing twice
                if (
                    jj not in duplicate_list
                    and abs(inter_list[ii] - inter_list[jj]) < 1e-6
                ):
                    duplicate_list.append(jj)
        for duplicate in duplicate_list[::-1]:
            inter_list.pop(duplicate)

        assert len(inter_list) == 2, (
            "Can't find the two points of the intersection with 0x axis"
        )

        # Sort the intersection points (Ztan1 is closest to the bore)
        if abs(inter_list[0]) < abs(inter_list[1]) and self.is_outwards():
            Ztan1 = inter_list[0]
            Ztan2 = inter_list[1]
        elif abs(inter_list[0]) > abs(inter_list[1]) and self.is_outwards():
            Ztan1 = inter_list[1]
            Ztan2 = inter_list[0]
        elif abs(inter_list[0]) < abs(inter_list[1]) and not self.is_outwards():
            Ztan1 = inter_list[1]
            Ztan2 = inter_list[0]
        elif abs(inter_list[0]) > abs(inter_list[1]) and not self.is_outwards():
            Ztan1 = inter_list[0]
            Ztan2 = inter_list[1]

        # First Tan split
        tan_list = []
        if Ntan == 2:
            top_surf, bot_surf = surf_act.split_line(
                0, 100, is_join=True, prop_dict_join=None
            )
            tan_list.append(bot_surf)
            tan_list.append(top_surf)
        else:
            tan_list = [surf_act]

        # Rad split
        surf_list = []
        X_list = np.linspace(Ztan1, Ztan2, Nrad + 1, True).tolist()[1:-1]
        for ii in range(Ntan):
            surf = tan_list[ii]
            if Nrad > 1:
                for jj in range(Nrad - 1):
                    X = X_list[jj]
                    top_surf, bot_surf = surf.split_line(
                        X - 100j,
                        X + 100j,
                        is_join=True,
                        prop_dict_join=None,
                    )
                    if self.is_outwards():
                        surf_list.append(top_surf)
                        surf = bot_surf
                    else:
                        surf_list.append(bot_surf)
                        surf = top_surf
                # Add the last surface
                surf_list.append(surf)
            else:  # add the radial surfaces without any other cut
                surf_list.append(surf.copy())

        # Set all label
        self.set_label(surf_list, Nrad, Ntan, self.parent.get_label())

        # Apply transformation
        for surf in surf_list:
            surf.rotate(alpha)
            surf.translate(delta)

        return surf_list

    # Inlined from Methods.Slot.Slot.build_geometry_half_tooth
    def build_geometry_half_tooth(self, is_top=False, alpha=0, delta=0):
        """Build the geometry of a Half Tooth

        Parameters
        ----------
        self : LamSlot
            a LamSlot object
        is_top : bool
            To select the part of the tooth (X>0 or X <0)
        alpha : float
            Angle for rotation [rad]
        delta : complex
            Complex value for translation

        Returns
        -------
        surf_list : list
            list of surfaces needed to draw the half tooth including slot base

        """

        # getting Number of Slot
        Zs = self.Zs
        Rbo = self.get_Rbo()

        slot_list = self.build_geometry()
        top_list = []
        bot_list = []

        for line in slot_list:
            Zbegin = line.get_begin()
            Zend = line.get_end()
            # append line
            if np.imag(Zbegin) <= 0 and np.imag(Zend) <= 0:
                top_list.append(line)
            elif np.imag(Zbegin) >= 0 and np.imag(Zend) >= 0:
                bot_list.append(line)
            else:  # The line cross the X axis => split
                # Copy the line (split_half modify the object)
                line2 = type(line)(init_dict=line.as_dict())
                # Split the lines
                line.split_half(is_begin=True)
                line2.split_half(is_begin=False)
                if np.imag(Zbegin) < 0:
                    top_list.append(line)
                    bot_list.append(line2)
                else:
                    top_list.append(line2)
                    bot_list.append(line)

        # add bore lines
        Zbo = Rbo * np.exp(-1j * np.pi / Zs)
        if np.abs(Zbo - top_list[0].get_begin()) > 1e-6:
            top_list.insert(
                0,
                Arc1(
                    begin=Zbo,
                    end=top_list[0].get_begin(),
                    radius=Rbo,
                    prop_dict={BOUNDARY_PROP_LAB: BORE_LAB},
                ),
            )
        Zbo = Rbo * np.exp(1j * np.pi / Zs)
        if np.abs(Zbo - bot_list[-1].get_end()) > 1e-6:
            bot_list.append(
                Arc1(
                    begin=bot_list[-1].get_end(),
                    end=Zbo,
                    radius=Rbo,
                    prop_dict={BOUNDARY_PROP_LAB: BORE_LAB},
                )
            )

        # Select the lines to return
        if is_top:
            tooth_list = top_list
            T_angle = np.pi / Zs
        else:
            tooth_list = bot_list
            T_angle = -np.pi / Zs

        # rotate
        for line in tooth_list:
            line.rotate(alpha + T_angle)

        # translate
        for line in tooth_list:
            line.translate(delta)

        return tooth_list

    # Inlined from Methods.Slot.Slot.check
    def check(self):
        """Check that the Slot object is correct

        Parameters
        ----------
        self : Slot
            A Slot object

        Returns
        -------
        None
        """
        pass

    # Inlined from Methods.Slot.Slot.comp_angle_active_eq
    def comp_angle_active_eq(self):
        """Compute the equivalent angle of the active part of the slot
        (Ideal polar shape with the same surface and height)

        Parameters
        ----------
        self : Slot
            A Slot object

        Returns
        -------
        alpha: float
            Average angle of the slot [rad]

        """

        Swind = self.comp_surface_active()
        Hwind = self.comp_height_active()
        Rmw = self.comp_radius_mid_active()
        Rext = Rmw + Hwind / 2
        Rint = Rmw - Hwind / 2

        return Swind * 2 * np.pi / (np.pi * Rext**2 - np.pi * Rint**2)

    # Inlined from Methods.Slot.Slot.comp_angle_opening
    def comp_angle_opening(self):
        """Compute the average opening angle of the Slot

        Parameters
        ----------
        self : Slot
            A Slot object

        Returns
        -------
        alpha: float
            Average opening angle of the slot [rad]

        """

        line_list = self.build_geometry()
        Z1 = line_list[0].get_begin()
        Z2 = line_list[-1].get_end()

        return np.angle(Z2) - np.angle(Z1)

    # Inlined from Methods.Slot.Slot.comp_height
    def comp_height(self, Ndisc=200):
        """Compute the height of the Slot.
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : Slot
            A Slot object
        Ndisc : int
            Number of point to discretize the lines

        Returns
        -------
        Htot: float
            Height of the slot [m]

        """

        Rbo = self.get_Rbo()

        surf = self.get_surface()

        point_list = surf.discretize(Ndisc)
        point_list = np.array(point_list)
        if self.is_outwards():
            return max(abs(point_list)) - Rbo
        else:
            return Rbo - min(abs(point_list))

    # Inlined from Methods.Slot.Slot.comp_height_active
    def comp_height_active(self, Ndisc=200):
        """Compute the height of the active area

        Parameters
        ----------
        self : Slot
            A Slot object
        Ndisc : int
            Number of point to discretize the lines

        Returns
        -------
        Hwind: float
            Height of the active area [m]

        """

        surf = self.get_surface_active()

        point_list = surf.discretize(Ndisc)
        point_list = abs(np.array(point_list))

        return max(point_list) - min(point_list)

    # Inlined from Methods.Slot.Slot.comp_height_opening
    def comp_height_opening(self, Ndisc=200):
        """Compute the height of the opening area (Hslot - Hactive)

        Parameters
        ----------
        self : Slot
            A Slot object
        Ndisc : int
            Number of point to discretize the lines

        Returns
        -------
        Hwind: float
            Height of the opening area [m]

        """

        return self.comp_height(Ndisc=Ndisc) - self.comp_height_active(Ndisc=Ndisc)

    # Inlined from Methods.Slot.Slot.comp_radius
    def comp_radius(self):
        """Compute the radius of the min and max circle that contains the slot

        Parameters
        ----------
        self : Slot
            A Slot object

        Returns
        -------
        (Rmin,Rmax): tuple
            Radius of the circle that contains the slot [m]

        """

        Rbo = self.get_Rbo()

        H = self.comp_height()
        Hmag = self.comp_height_active()

        if H < Hmag:
            if self.is_outwards():
                return (Rbo - Hmag + H, Rbo + H)
            else:
                return (Rbo - H, Rbo + Hmag - H)
        else:
            if self.is_outwards():
                return (Rbo, Rbo + H)
            else:
                return (Rbo - H, Rbo)

    # Inlined from Methods.Slot.Slot.comp_radius_mid_active
    def comp_radius_mid_active(self):
        """Compute the radius at the middle of the active part of the slot

        Parameters
        ----------
        self : Slot
            A Slot object

        Returns
        -------
        Rmw: float
            Mid active radius [m]

        """

        Rbo = self.get_Rbo()
        Hslot = self.comp_height()
        Hwind = self.comp_height_active()
        if self.is_outwards():
            return Rbo + Hslot - Hwind / 2
        else:
            return Rbo - Hslot + Hwind / 2

    # Inlined from Methods.Slot.Slot.comp_surface
    def comp_surface(self, Ndisc=200):
        """Compute the Slot total surface (by numerical computation).
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : Slot
            A Slot object
        Ndisc : int
            Number of point to discretize the lines

        Returns
        -------
        S: float
            Slot total surface [m**2]
        """

        surf = self.get_surface()
        return surf.comp_surface(Ndisc=Ndisc)

    # Inlined from Methods.Slot.Slot.comp_surface_active
    def comp_surface_active(self, Ndisc=200):
        """Compute the Slot active surface (by numerical computation).
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : Slot
            A Slot object
        Ndisc : int
            Number of point to discretize the lines

        Returns
        -------
        S: float
            Slot active surface [m**2]

        """

        surf = self.get_surface_active()

        return surf.comp_surface(Ndisc=Ndisc)

    # Inlined from Methods.Slot.Slot.comp_surface_opening
    def comp_surface_opening(self, Ndisc=200):
        """Compute the Slot opening surface (by numerical computation).
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : Slot
            A Slot object
        Ndisc : int
            Number of point to discretize the lines

        Returns
        -------
        S: float
            Slot opening surface [m**2]

        """

        surf_list = self.get_surface_opening()

        S = 0
        for surf in surf_list:
            S += surf.comp_surface(Ndisc=Ndisc)
        return S

    # Inlined from Methods.Slot.Slot.comp_surface_wedges
    def comp_surface_wedges(self, Ndisc=200):
        """Compute the Slot wedges surface (by numerical computation).
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : Slot
            A Slot object
        Ndisc : int
            Number of point to discretize the lines

        Returns
        -------
        S: float
            Slot wedges surface [m**2]

        """

        surf_list = self.get_surface_wedges()

        S = 0
        for surf in surf_list:
            S += surf.comp_surface(Ndisc=Ndisc)
        return S

    # Inlined from Methods.Slot.Slot.comp_width
    def comp_width(self):
        """Compute the average width of the Slot by dividing its surface by its height

        Parameters
        ----------
        self : Slot
            A Slot object

        Returns
        -------
        W2: float
            Average width of the slot [m]
        """

        S = self.comp_surface()

        H = self.comp_height()

        return S / H

    # Inlined from Methods.Slot.Slot.comp_width_opening
    def comp_width_opening(self, is_curved=False):
        """Compute the average opening width of the Slot

        Parameters
        ----------
        self : Slot
            A Slot object
        is_curved : bool
            width opening curved or straight

        Returns
        -------
        W0: float
            Average opening width of the slot [m] or [rad]
        """

        if is_curved:
            R = self.get_Rbo()
            alpha = self.comp_angle_opening()
            Zs = self.parent.get_Zs()
            return 2 * np.pi * R / Zs - alpha * R
        else:
            line_list = self.build_geometry()
            Z1 = line_list[0].get_begin()
            Z2 = line_list[-1].get_end()
            return abs(Z2 - Z1)

    # Inlined from Methods.Slot.Slot.convert_to_SlotUD2
    def convert_to_SlotUD2(self):
        """Convert the slot to the equivalent SlotUD2

        Parameters
        ----------
        self : Slot
            a Slot object

        Returns
        -------
        new_slot : SlotUD2
            SlotUD2 version of the Slot
        """
        SlotUD2 = import_class("SlotUD2")
        new_slot = SlotUD2()
        new_slot.Zs = self.Zs
        new_slot.line_list = self.build_geometry()
        new_slot.active_surf = self.get_surface_active()
        new_slot.split_active_surf_dict = None

        return new_slot

    # Inlined from Methods.Slot.Slot.get_is_stator
    def get_is_stator(self):
        """Return True if the parent lamination is stator and False if is a rotor

        Parameters
        ----------
        self : Slot
            A Slot object

        Returns
        -------
        is_stator: bool
            True if the Lamination is a stator and False if not

        """

        if self.parent is not None:
            return self.parent.is_stator
        else:
            raise ParentMissingError("Error: The slot is not inside a Lamination")

    # Inlined from Methods.Slot.Slot.get_name_lam
    def get_name_lam(self):
        """Return the name of the parent lamination

        Parameters
        ----------
        self : Slot
            A Slot object

        Returns
        -------
        name: string
            The name of the parent lamination

        """

        if self.parent is not None:
            return self.parent.get_label()
        else:
            return "NoLam"

    # Inlined from Methods.Slot.Slot.get_Rbo
    def get_Rbo(self):
        """Return the parent lamination bore radius

        Parameters
        ----------
        self : Slot
            A Slot object

        Returns
        -------
        Rbo: float
            The parent lamination bore radius [m]

        """

        if self.parent is not None:
            if self.is_bore in [True, None]:
                return self.parent.get_Rbo()
            else:
                return self.parent.get_Ryoke()
        else:
            raise ParentMissingError("Error: The slot is not inside a Lamination")

    # Inlined from Methods.Slot.Slot.get_surface
    def get_surface(self):
        """Returns the surface delimiting the slot

        Parameters
        ----------
        self : Slot
            A Slot object

        Returns
        -------
        surface: SurfLine
            A SurfLine object representing the slot

        """
        Rbo = self.get_Rbo()
        curve_list = self.build_geometry()

        # Remove line overlapping with bore/yoke lines (for FEMM)
        for line in curve_list:
            if line.prop_dict is None:
                line.prop_dict = {}
            line.prop_dict[DRAW_PROP_LAB] = False

        # Add closing Arc
        Zbegin = curve_list[-1].get_end()
        Zend = curve_list[0].get_begin()
        curve_list.append(
            Arc1(begin=Zbegin, end=Zend, radius=-Rbo, is_trigo_direction=False)
        )

        surf = SurfLine(line_list=curve_list, label="Slot")
        surf.comp_point_ref(is_set=True)
        return surf

    # Inlined from Methods.Slot.Slot.get_surface_tooth
    def get_surface_tooth(self):
        """Returns the surface delimiting the tooth (including yoke part)

        Parameters
        ----------
        self : Slot
            A Slot object

        Returns
        -------
        surface: SurfLine
            A SurfLine object representing the slot

        """

        if self.parent is not None:
            Ryoke = self.parent.get_Ryoke()
        else:
            raise ParentMissingError("Error: The slot is not inside a Lamination")

        curve_list = []
        # tooth lines
        top_list = self.build_geometry_half_tooth(is_top=True)
        bot_list = self.build_geometry_half_tooth(is_top=False)
        # Yoke lines
        Z1 = Ryoke * np.exp(1j * np.pi / self.Zs)
        Z2 = Ryoke * np.exp(-1j * np.pi / self.Zs)
        curve_list.append(
            Segment(
                begin=top_list[-1].get_end(),
                end=Z1,
                prop_dict={BOUNDARY_PROP_LAB: YSL_LAB},
            )
        )
        if Ryoke > 0:
            curve_list.append(
                Arc1(
                    begin=Z1,
                    end=Z2,
                    radius=-Ryoke,
                    is_trigo_direction=False,
                    prop_dict={BOUNDARY_PROP_LAB: YOKE_LAB},
                )
            )
        curve_list.append(
            Segment(
                begin=Z2,
                end=bot_list[0].get_begin(),
                prop_dict={BOUNDARY_PROP_LAB: YSR_LAB},
            )
        )
        # Second half of the tooth
        curve_list.extend(bot_list)
        curve_list.extend(top_list)

        if self.parent is not None:
            lam_label = self.parent.get_label()
        else:
            lam_label = NO_LAM_LAB
        label = lam_label + "_" + TOOTH_LAB
        return SurfLine(line_list=curve_list, label=label)

    # Inlined from Methods.Slot.Slot.get_surface_wedges
    def get_surface_wedges(self, alpha=0, delta=0):
        """Return the list of surfaces defining the wedges area of the Slot

        Parameters
        ----------
        self : Slot
            A Slot object
        alpha : float
            float number for rotation (Default value = 0) [rad]
        delta : complex
            complex number for translation (Default value = 0)

        Returns
        -------
        surf_list : list
            list of surfaces objects
        """

        if hasattr(self, "wedge_type"):
            wedge_type = self.wedge_type
        else:
            wedge_type = 0

        if self.wedge_mat is None:
            return []  # No wedges

        # By default Wedge is the full opening surface
        if wedge_type == 0:
            surf_list = self.get_surface_opening()

        elif wedge_type == 1:
            surf_list = self.get_surface_wedge()

        else:
            raise NotImplementedError

        if self.parent is not None:
            # Adapt label
            lam_lab = self.parent.get_label()
            for surf in surf_list:
                surf.label = lam_lab + "_" + WEDGE_LAB + "_R0-T0-S0"

        # Apply transformation
        for surf in surf_list:
            surf.rotate(alpha)
            surf.translate(delta)

        return surf_list

    # Inlined from Methods.Slot.Slot.is_airgap_active
    def is_airgap_active(self):
        """Return True if a part or the full active surface is in the airgap

        Parameters
        ----------
        self : Slot
            A Slot object

        Returns
        -------
        is_airgap_active : bool
            True if a part or the full active surface is in the airgap
        """

        return False

    # Inlined from Methods.Slot.Slot.is_full_pitch_active
    def is_full_pitch_active(self):
        """Returns True if the active surface angular width
        matches the slot pitch (like SlotM17 or SlotM18)
        (used to set Boundary conditions in FEMM airgap)

        Parameters
        ----------
        self : Slot
            A Slot object

        Returns
        -------
        is_full_pitch_active : bool
            True if the active surface angular width matches the slot pitch
        """

        return False

    # Inlined from Methods.Slot.Slot.is_outwards
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
        if self.parent is not None:
            if self.is_bore in [True, None]:
                return self.parent.is_outwards()
            else:
                return not self.parent.is_outwards()
        else:
            raise ParentMissingError(
                "Error: The slot is not inside a Lamination or a Notch"
            )

    # Inlined from Methods.Slot.Slot.plot
    def plot(self, fig=None, ax=None, is_show_fig=True):
        """Plot the Slot in a matplotlib fig

        Parameters
        ----------
        self : Slot
            A Slot object
        fig :
            if None, open a new fig and plot, else add to the current
            one (Default value = None)

        Returns
        -------
        fig : Matplotlib.figure.Figure
            Figure containing the plot
        ax : Matplotlib.axes.Axes object
            Axis containing the plot
        """
        surf = self.get_surface()

        # Display the result
        (fig, ax, patch_leg, label_leg) = init_fig(fig, ax)
        ax.set_xlabel("[m]")
        ax.set_ylabel("[m]")
        ax.set_title("Slot")

        # Add the slot to the fig
        if self.get_is_stator:
            patches = surf.get_patches(color=self.STATOR_COLOR)
        else:
            patches = surf.get_patch(color=self.ROTOR_COLOR)
        for patch in patches:
            ax.add_patch(patch)

        # Axis Setup
        ax.axis("equal")
        if is_show_fig:
            fig.show()
        return fig, ax

    # Inlined from Methods.Slot.Slot.plot_active
    def plot_active(
        self,
        wind_mat=None,
        fig=None,
        ax=None,
        is_bar=False,
        is_show_fig=True,
        enforced_default_color=None,
        alpha=0,
        delta=0,
        is_add_wedge=False,
    ):
        """Plot the active area of the lamination according to the wind_mat

        Parameters
        ----------
        self : Slot
            A Slot object
        wind_mat : numpy.ndarray
            A matrix [Nrad,Ntan,Zs,qs] representing the active (Default value = None)
        fig :
            if None, open a new fig and plot, else add to the current
            one (Default value = None)
        is_bar : bool
            To adapt the legend text for squirrel cage bar (Default value = False)
        is_show_fig : bool
            To call show at the end of the method
        enforced_default_color : str
            If not None enforce the active color (when wind_mat is None)
        alpha : float
            Angle for rotation (Default value = 0) [rad]
        delta : Complex
            complex for translation (Default value = 0)
        is_add_wedge : bool
            True to add the wedges surfaces

        Returns
        -------
        None
        """

        if enforced_default_color is None:
            enforced_default_color = self.PHASE_COLORS[0]

        if wind_mat is None:  # Default : Only one zone monocolor
            Nrad, Ntan, qs = 1, 1, 1
            Zs = self.Zs
        else:
            (Nrad, Ntan, Zs, qs) = wind_mat.shape
        qs_name = gen_name(qs)

        surf_list = self.build_geometry_active(Nrad, Ntan, alpha=alpha, delta=delta)

        patches = []
        for ii in range(len(surf_list)):
            # Compute the coordinate for one zone
            point_list = []
            for curve in surf_list[ii].get_lines():
                point_list.extend(curve.discretize().tolist())
            point_list = np.array(point_list)

            for jj in range(Zs):
                if wind_mat is None or len(surf_list) != Ntan * Nrad:
                    x, y = point_list.real, point_list.imag
                    patches.append(
                        Polygon(list(zip(x, y)), color=enforced_default_color)
                    )
                else:
                    # print "Nrad, Ntan, Zs : "+str((ii%Nrad,ii/Nrad,jj))
                    color = self.get_color(wind_mat, ii % Nrad, ii // Nrad, jj)
                    x, y = point_list.real, point_list.imag
                    patches.append(Polygon(list(zip(x, y)), color=color))
                point_list = point_list * np.exp(1j * (2 * np.pi) / self.Zs)

        # Display the result
        (fig, ax, patch_leg, label_leg) = init_fig(fig, ax=ax)
        ax.set_xlabel("[m]")
        ax.set_ylabel("[m]")
        ax.set_title("Winding Pattern")

        # Add wedges
        if is_add_wedge:
            # Add mp blanck wedge wedge for plot
            to_clean = False
            if self.wedge_mat is None:
                self.wedge_mat = Material()
                to_clean = True
            wedge_surf_list = self.get_surface_wedges()
            for surf in wedge_surf_list:
                for ii in range(Zs):
                    surf2 = surf.copy()
                    surf2.rotate(angle=ii * (2 * np.pi) / self.Zs)
                    surf2.plot(
                        fig=fig, ax=ax, color=self.WEDGE_COLOR, is_show_fig=False
                    )
            # Remove tmp blanck wedge
            if to_clean:
                self.wedge_mat = None

        # Add the magnet to the fig
        for patch in patches:
            ax.add_patch(patch)

        # Axis Setup
        ax.axis("equal")
        Rbo = self.get_Rbo()

        Lim = Rbo * 1.2
        ax.set_xlim(-Lim, Lim)
        ax.set_ylim(-Lim, Lim)

        # Legend setup
        if wind_mat is None or len(surf_list) != Ntan * Nrad:
            # No winding matrix => Only one zone
            if not is_bar and not ("Winding" in label_leg):
                # Avoid adding twice the same label
                patch_leg.append(Patch(color=self.PHASE_COLORS[0]))
                label_leg.append("Winding")
            elif is_bar and not ("Rotor bar" in label_leg):
                # Avoid adding twice the same label
                patch_leg.append(Patch(color=self.PHASE_COLORS[0]))
                label_leg.append("Rotor bar")
        else:  # Add every phase to the legend
            for ii in range(qs):
                if not ("Phase " + qs_name[ii] in label_leg):
                    # Avoid adding twice the same label
                    index = ii % len(self.PHASE_COLORS)
                    patch_leg.append(Patch(color=self.PHASE_COLORS[index]))
                    label_leg.append("Phase " + qs_name[ii])

        ax.legend(
            patch_leg,
            label_leg,
            prop={"family": dict_2D["font_name"], "size": dict_2D["font_size_legend"]},
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

        if is_show_fig:
            fig.show()
        return fig, ax

    @staticmethod
    def get_color(wind_mat, Nrad, Ntan, Zs):
        """Return the color (corresponding phase) for the zone (Nrad,Ntan,Zs)

        Parameters
        ----------
        wind_mat :
            A matrix [Nrad,Ntan,Zs,qs] representing the winding
        Nrad :
            Zone radial coordinate
        Ntan :
            Zone tagential coordinate
        Zs :
            Zone slot number coordinate

        Returns
        -------
        str
            color: Color of the zone

        """
        A = wind_mat[Nrad, Ntan, Zs, :]
        for zz in range(len(A)):
            if A[zz] != 0:
                return Slot.PHASE_COLORS[zz]
        return "w"  # If all the phase are at 0 : the zone is empty => white

    # Inlined from Methods.Slot.Slot.set_label
    def set_label(self, surf_list, Nrad, Ntan, lam_label):
        """Set the normalized label on the active surface
        (internal method of build_geometry_active)

        Parameters
        ----------
        self : Slot
            A Slot object
        surf_list : [Surface]
            List of split active surface of the winding (for one slot)
        Nrad : int
            Number of radial layer
        Ntan : int
            Number of tangential layer
        lam_label : str
            Label of the lamination containing the slot
        """

        index = 0
        for jj in range(Ntan):
            for ii in range(Nrad):
                surf_list[index].label = (
                    lam_label + "_" + WIND_LAB + "_R" + str(ii) + "-T" + str(jj) + "-S0"
                )
                index += 1
