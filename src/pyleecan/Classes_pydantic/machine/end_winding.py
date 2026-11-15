# Experimental pydantic model generated from Generator/ClassesRef/Machine/EndWinding.csv
"""Generated experimental pydantic model; do not edit by hand."""

from typing import ClassVar

from pydantic import Field

from .._pyleecan_model import PyleecanModel


class EndWinding(PyleecanModel):
    """Abstract Class of the machine's end winding

    Attributes
    ----------
    Lew_enforced : float
        Enforced end-winding lekage inductance
        Unit: H; Default: 0; Minimum: 0
    """

    Lew_enforced: float = Field(default=0, ge=0, json_schema_extra={"unit": "H"})
    """Enforced end-winding lekage inductance"""

    _package: ClassVar[str] = "Machine"
    """Name of the package of the legacy class module"""

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
