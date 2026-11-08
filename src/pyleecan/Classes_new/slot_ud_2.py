# Experimental dataclass generated from Generator/ClassesRef/Slot/SlotUD2.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass, field
from typing import Any

from ._check import check_var
from ._error import SlotCheckError
from ._import import import_class
from .line import Line
from .slot import Slot
from .surface import Surface


@dataclass(eq=False)
class SlotUD2(Slot):
    """ "User defined" Slot from a line list and a surface

    Attributes
    ----------
    line_list : [Line] or None
        list of line to draw the edges of the slot
        Default: None
    active_surf : Surface or None
        Active surface of the Slot
        Default: None
    split_active_surf_dict : dict or None
        Dictionary to enforced the split active surface (key="Nrad=1, Ntan=2"). Labels set according to list order (loop on Nrad then Ntan)
        Default: {}
    name : str or None
        Name of the slot (for save)
        Default: None
    """

    line_list: list[Line] | None = None
    """list of line to draw the edges of the slot"""
    active_surf: Surface | None = None
    """Active surface of the Slot"""
    split_active_surf_dict: dict[str, Any] | None = field(default_factory=dict)
    """Dictionary to enforced the split active surface (key="Nrad=1, Ntan=2"). Labels set according to list order (loop on Nrad then Ntan)"""
    name: str | None = None
    """Name of the slot (for save)"""

    # Inlined from Methods.Slot.SlotUD2._set_split_active_surf_dict
    def _set_split_active_surf_dict(self, value):
        """setter of split_active_surf_dict"""
        if type(value) is dict:
            for key, obj_list in value.items():
                if type(obj_list) is list:
                    for ii, obj in enumerate(obj_list):
                        if type(obj) is dict and "__class__" in obj:
                            class_obj = import_class(
                                obj["__class__"], "split_active_surf_dict"
                            )
                            value[key][ii] = class_obj(init_dict=obj)
        if value == -1:
            value = {}
        check_var("split_active_surf_dict", value, "dict")
        self._split_active_surf_dict = value

    # Inlined from Methods.Slot.SlotUD2.build_geometry
    def build_geometry(self):
        """Compute the curve (Line) needed to plot the object.
        The ending point of a curve is the starting point of the next curve
        in the list

        Parameters
        ----------
        self : SlotUD2
            A SlotUD2 object

        Returns
        -------
        curve_list: list
            A list of Segments

        """

        return [line.copy() for line in self.line_list]

    # Inlined from Methods.Slot.SlotUD2.build_geometry_active
    def build_geometry_active(self, Nrad, Ntan, is_simplified=False, alpha=0, delta=0):
        """Split the slot active area in several zone
        This method assume that the active area is centered on X axis and symetrical
        Otherwise a dedicated build_geometry_active method must be provided

        Parameters
        ----------
        self : SlotUD2
            A SlotUD2 object
        Nrad : int
            Number of radial layer
        Ntan : int
            Number of tangentiel layer
        is_simplified : bool
            boolean to specify if coincident lines are considered as one or different lines (Default value = False)
        alpha : float
            Angle for rotation (Default value = 0) [rad]
        delta : Complex
            complex for translation (Default value = 0)

        Returns
        -------
        surf_list:
            List of surface delimiting the active zone
        """

        key = "Nrad=" + str(Nrad) + ", Ntan=" + str(Ntan)

        if (
            self.split_active_surf_dict is not None
            and key in self.split_active_surf_dict
        ):
            surf_list = [surf.copy() for surf in self.split_active_surf_dict[key]]
            self.set_label(surf_list, Nrad, Ntan, self.get_name_lam())
            return surf_list
        else:
            return Slot.build_geometry_active(
                self,
                Nrad=Nrad,
                Ntan=Ntan,
                is_simplified=is_simplified,
                alpha=alpha,
                delta=delta,
            )

    # Inlined from Methods.Slot.SlotUD2.check
    def check(self):
        """Check that the SlotUD2 is correctly defined"""

        if self.line_list is None:
            self.line_list = []

        if len(self.line_list) == 0:
            raise SlotCheckError("SlotUD2 must have at least one line")

        for ii in range(len(self.line_list) - 1):
            if (
                abs(self.line_list[ii].get_end() - self.line_list[ii + 1].get_begin())
                > 1e-6
            ):
                raise SlotCheckError(
                    "SlotUD line "
                    + str(ii)
                    + " and line "
                    + str(ii + 1)
                    + " doesn't match"
                )

    # Inlined from Methods.Slot.SlotUD2.get_surface_active
    def get_surface_active(self, alpha=0, delta=0):
        """Return the full winding surface

        Parameters
        ----------
        self : SlotUD2
            A SlotUD2 object
        alpha : float
            float number for rotation (Default value = 0) [rad]
        delta : complex
            complex number for translation (Default value = 0)

        Returns
        -------
        surf_wind: Surface
            Surface corresponding to the Winding Area
        """
        st = self.get_name_lam()
        surface = self.active_surf.copy()

        surface.label = "Wind_" + st + "_R0_T0_S0"

        # Apply transformation
        surface.rotate(alpha)
        surface.translate(delta)

        return surface
