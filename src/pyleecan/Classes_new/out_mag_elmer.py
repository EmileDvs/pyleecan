# Experimental dataclass generated from Generator/ClassesRef/Output/OutMagElmer.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass, field
from typing import Any

from .out_internal import OutInternal


@dataclass(eq=False)
class OutMagElmer(OutInternal):
    """Class to store outputs related to MagElmer magnetic model

    Attributes
    ----------
    FEA_dict : dict or None
        dictionary containing the main FEA parameters
        Default: {}
    """

    FEA_dict: dict[str, Any] | None = field(default_factory=dict)
    """dictionary containing the main FEA parameters"""

    # Inlined from Methods.Output.OutMagElmer.clean
    def clean(self, clean_level=1):
        """Clean MagElmer outputs depending on cleaning level

        Parameters
        ----------
        self : OutMagElmer
            the OutMagElmer object to update
        clean_level : int
            Value to indicate which fields to clean in OutMagElmer (default=1/min=0/max=4)

        """

        # if clean_level = 0:
        # keep all internal outputs

        if clean_level > 0:
            # clean FEA_dict
            self.FEA_dict = None
