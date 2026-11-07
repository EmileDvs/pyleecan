# Experimental dataclass generated from Generator/ClassesRef/Output/OutMagFEMM.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass, field
from typing import Any

from .out_internal import OutInternal


@dataclass(eq=False)
class OutMagFEMM(OutInternal):
    """Class to store outputs related to MagFEMM magnetic model

    Attributes
    ----------
    FEMM_dict : dict or None
        dictionary containing the main FEMM parameters
        Default: {}
    handler_list : [_FEMMHandler] or None
        List of FEMM Handler (more than 1 if nb_worker >1)
        Default: None
    """

    FEMM_dict: dict[str, Any] | None = field(default_factory=dict)
    """dictionary containing the main FEMM parameters"""
    handler_list: list[Any] | None = None
    """List of FEMM Handler (more than 1 if nb_worker >1)"""

    # Inlined from Methods.Output.OutMagFEMM.clean
    def clean(self, clean_level=1):
        """Clean MagFEMM outputs depending on cleaning level

        Parameters
        ----------
        self : OutMagFEMM
            the OutMagFEMM object to update
        clean_level : int
            Value to indicate which fields to clean in OutMagFEMM (default=1/min=0/max=4)

        """

        # if clean_level = 0:
        # keep all internal outputs

        if clean_level > 0:
            # clean FEMM_dict
            self.FEMM_dict = None
