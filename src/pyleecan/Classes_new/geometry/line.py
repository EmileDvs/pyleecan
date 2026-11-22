# Experimental dataclass generated from Generator/ClassesRef/Geometry/Line.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, ClassVar

import numpy as np

from .._legacy_class import LegacyClass


@dataclass(eq=False)
class Line(LegacyClass):
    """Abstract geometry class (A line between two points)

    Attributes
    ----------
    prop_dict : dict or None
        Property dictionary
        Default: None
    """

    LINE_NPOINT_D: ClassVar = 1

    prop_dict: dict[str, Any] | None = None
    """Property dictionary"""

    _package: ClassVar[str] = "Geometry"
    """Name of the package of the legacy class module"""

    if TYPE_CHECKING:
        # Members of the daughter classes, for the type checkers
        # (not defined at runtime: no field, no method)

        def split_line(self, *args: Any, **kwargs: Any) -> Any: ...

        def is_on_line(self, *args: Any, **kwargs: Any) -> bool: ...

        def is_arc(self, *args: Any, **kwargs: Any) -> bool: ...

        def get_begin(self, *args: Any, **kwargs: Any) -> complex: ...

        def get_end(self, *args: Any, **kwargs: Any) -> complex: ...

        def get_center(self, *args: Any, **kwargs: Any) -> complex: ...

    # Inlined from Methods.Geometry.Line.comp_normal
    def comp_normal(self) -> float:
        """Compute the normal direction of the Line
        Normal point is "on top" (begin=O and end on Ox)

        Parameters
        ----------
        self : Line
            a Line object

        Returns
        -------
        normal: float
            Angle of the vector between (Zbegin+Zend)/2 (even for arc) and the normal point [rad]
        """

        Zb = self.get_begin()
        Ze = self.get_end()
        Zm = (Zb + Ze) / 2  # "Middle" of the line
        L = self.comp_length() / 3

        # In ref begin=O and end on Ox
        Zm2 = (Zm - Zb) * np.exp(-1j * np.angle(Ze - Zb))
        Zn2 = Zm2 + 1j * L

        Zn = Zn2 * np.exp(1j * np.angle(Ze - Zb)) + Zb

        return np.angle(Zn - Zm)
