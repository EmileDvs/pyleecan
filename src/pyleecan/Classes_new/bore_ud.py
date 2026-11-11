# Experimental dataclass generated from Generator/ClassesRef/Machine/BoreUD.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass, field

from .bore import Bore
from .line import Line


@dataclass(eq=False)
class BoreUD(Bore):
    """User Defined Bore shape

    Attributes
    ----------
    line_list : [Line] or None
        List of line to draw the full bore
        Default: []
    sym : int
        Symmetry factor (1= full machine, 2= half of the machine...)
        Default: 1; Minimum: 1
    name : str or None
        Name of the bore (for save)
        Default: None
    """

    line_list: list[Line] | None = field(default_factory=list)
    """List of line to draw the full bore"""
    sym: int = 1
    """Symmetry factor (1= full machine, 2= half of the machine...)"""
    name: str | None = None
    """Name of the bore (for save)"""

    # Inlined from Methods.Machine.BoreUD.comp_periodicity_spatial
    def comp_periodicity_spatial(self):
        """Compute the periodicity factor of the Bore

        Parameters
        ----------
        self : BoreUD
            A BoreUD object

        Returns
        -------
        per_a : int
            Number of spatial periodicities of the bore
        is_antiper_a : bool
            True if an spatial anti-periodicity is possible after the periodicities
        """

        return self.sym, False

    # Inlined from Methods.Machine.BoreUD.get_bore_line
    def get_bore_line(self, label=None):
        """Return the bore line description

        Parameters
        ----------
        self : BoreUD
            A BoreUD object

        Returns
        -------
        bore_list : list
            List of bore lines
        """

        if label is not None:
            for line in self.line_list:
                line.label = label

        return self.line_list
