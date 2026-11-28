# Experimental pydantic model generated from Generator/ClassesRef/Slot/SlotUD2.csv
"""Generated experimental pydantic model; do not edit by hand."""

from typing import TYPE_CHECKING, Any, ClassVar

from pydantic import Field

from ...classes_common.check import check_var
from ...classes_common.errors import SlotCheckError
from .._import import import_class
from ..geometry.line import Line
from ..geometry.surface import Surface
from .slot import Slot

if TYPE_CHECKING:
    from ..geometry.surface import Surface
    from ..machine.lamination import Lamination
    from ..machine.notch import Notch


class SlotUD2(Slot):
    """ "User defined" Slot from a line list and a surface

    Attributes
    ----------
    line_list : [Line] or None
        list of line to draw the edges of the slot
        Default: []
    active_surf : Surface or None
        Active surface of the Slot
        Default: Surface()
    split_active_surf_dict : dict or None
        Dictionary to enforced the split active surface (key="Nrad=1, Ntan=2"). Labels set according to list order (loop on Nrad then Ntan)
        Default: None
    name : str
        Name of the slot (for save)
        Default: ""
    """

    line_list: list[Line] = Field(default_factory=list)
    """list of line to draw the edges of the slot"""
    active_surf: Surface = Field(default_factory=lambda: import_class("Surface")())
    """Active surface of the Slot"""
    split_active_surf_dict: dict[str, Any] | None = None
    """Dictionary to enforced the split active surface (key="Nrad=1, Ntan=2"). Labels set according to list order (loop on Nrad then Ntan)"""
    name: str = ""
    """Name of the slot (for save)"""

    _custom_setters: ClassVar[tuple[str, ...]] = ("split_active_surf_dict",)
    """Fields set by a legacy custom setter (_set_<field>)"""
    _package: ClassVar[str] = "Slot"
    """Name of the package of the legacy class module"""

    # Inlined from Methods.Slot.SlotUD2._set_split_active_surf_dict
    def _set_split_active_surf_dict(self, value) -> None:
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
        self.split_active_surf_dict = value

    # Inlined from Methods.Slot.SlotUD2.build_geometry
    def build_geometry(self, lam: Lamination | Notch | None = None) -> list:
        """Compute the curve (Line) needed to plot the object.
        The ending point of a curve is the starting point of the next curve
        in the list

        Parameters
        ----------
        self : SlotUD2
            A SlotUD2 object
        lam : Lamination or Notch, optional
            Lamination (or notch) holding the slot (default: the parent)

        Returns
        -------
        curve_list: list
            A list of Segments

        """

        return [line.copy() for line in self.line_list]

    # Inlined from Methods.Slot.SlotUD2.build_geometry_active
    def build_geometry_active(
        self,
        Nrad: int,
        Ntan: int,
        is_simplified: bool = False,
        alpha: float = 0,
        delta: complex = 0,
        lam: Lamination | Notch | None = None,
        lam_label: str | None = None,
    ):
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
        lam : Lamination or Notch, optional
            Lamination (or notch) holding the slot (default: the parent)
        lam_label : str, optional
            Label of the lamination (default: lam.get_label(), which reads
            the machine holding the lamination)

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
            self.set_label(
                surf_list, Nrad, Ntan, self.get_name_lam(lam=lam, lam_label=lam_label)
            )
            return surf_list
        else:
            return Slot.build_geometry_active(
                self,
                Nrad=Nrad,
                Ntan=Ntan,
                alpha=alpha,
                delta=delta,
                lam=lam,
                lam_label=lam_label,
            )

    # Inlined from Methods.Slot.SlotUD2.check
    def check(self, lam: Lamination | Notch | None = None) -> None:
        """Check that the SlotUD2 is correctly defined

        Parameters
        ----------
        lam : Lamination or Notch, optional
            Lamination (or notch) holding the slot (default: the parent)
        """

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
    def get_surface_active(
        self,
        alpha: float = 0,
        delta: complex = 0,
        lam: Lamination | Notch | None = None,
        lam_label: str | None = None,
    ) -> Surface:
        """Return the full winding surface

        Parameters
        ----------
        self : SlotUD2
            A SlotUD2 object
        alpha : float
            float number for rotation (Default value = 0) [rad]
        delta : complex
            complex number for translation (Default value = 0)
        lam : Lamination or Notch, optional
            Lamination (or notch) holding the slot (default: the parent)
        lam_label : str, optional
            Label of the lamination (default: lam.get_label(), which reads
            the machine holding the lamination)

        Returns
        -------
        surf_wind: Surface
            Surface corresponding to the Winding Area
        """
        st = self.get_name_lam(lam=lam, lam_label=lam_label)
        surface = self.active_surf.copy()

        surface.label = "Wind_" + st + "_R0_T0_S0"

        # Apply transformation
        surface.rotate(alpha)
        surface.translate(delta)

        return surface
