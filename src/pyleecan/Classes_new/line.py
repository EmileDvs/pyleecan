# Experimental dataclass generated from Generator/ClassesRef/Geometry/Line.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass, field
from typing import Any, ClassVar

import numpy as np

from ._pyleecan_class import PyleecanClass


@dataclass(eq=False)
class Line(PyleecanClass):
    """Abstract geometry class (A line between two points)

    Attributes
    ----------
    prop_dict : dict or None
        Property dictionary
        Default: {}
    """

    LINE_NPOINT_D: ClassVar = 1
    prop_dict: dict[str, Any] | None = field(default_factory=dict)
    """Property dictionary"""

    # Inlined from Methods.Geometry.Line.comp_normal
    def comp_normal(self):
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
