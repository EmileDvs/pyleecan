# Experimental dataclass generated from Generator/ClassesRef/Machine/EndWinding.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

from ._pyleecan_class import PyleecanClass
from .winding import Winding


@dataclass(eq=False)
class EndWinding(PyleecanClass):
    """Abstract Class of the machine's end winding

    Attributes
    ----------
    Lew_enforced : float
        Enforced end-winding lekage inductance
        Unit: H; Default: 0; Minimum: 0
    """

    Lew_enforced: float = 0
    """Enforced end-winding lekage inductance"""

    def __post_init__(self):
        super().__post_init__()

    def _assert_parent_type(self, parent):
        if parent is not None and not isinstance(parent, (Winding,)):
            raise TypeError(
                "EndWinding parent must be an instance of Winding, or None; "
                + f"got {type(parent).__name__}"
            )

    # Inlined from Methods.Machine.EndWinding.comp_inductance
    def comp_inductance(self):
        """Return the enforced end winding inductance

        Parameters
        ----------
        self: EndWinding
            A EndWinding object

        Returns
        -------
        Lew : float
            end winding inductance [H]
        """

        return self.Lew_enforced

    # Inlined from Methods.Machine.EndWinding.comp_length
    def comp_length(self):
        """Compute the end winding conductor length on one side for a half-turn
        excluding the straight conductor length outside of the lamination (winding.Lewout).
        Since this is the abstract class method the actual length returned will be zero.

        Parameters
        ----------
        self: EndWinding
            A EndWinding object
        Returns
        -------
        end_wind_length : float
            End-winding length on one side for a half-turn [m].
        """

        return 0
