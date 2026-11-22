# Experimental pydantic model generated from Generator/ClassesRef/Output/OutMagFEMM.csv
"""Generated experimental pydantic model; do not edit by hand."""

from typing import Any, ClassVar

from pydantic import Field

from .out_internal import OutInternal


class OutMagFEMM(OutInternal):
    """Class to store outputs related to MagFEMM magnetic model

    Attributes
    ----------
    FEMM_dict : dict or None
        dictionary containing the main FEMM parameters
        Default: None
    handler_list : [_FEMMHandler] or None
        List of FEMM Handler (more than 1 if nb_worker >1)
        Default: []
    """

    FEMM_dict: dict[str, Any] | None = None
    """dictionary containing the main FEMM parameters"""
    handler_list: list[Any] = Field(default_factory=list)
    """List of FEMM Handler (more than 1 if nb_worker >1)"""

    _package: ClassVar[str] = "Output"
    """Name of the package of the legacy class module"""

    # Inlined from Methods.Output.OutMagFEMM.clean
    def clean(self, clean_level: int = 1) -> None:
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
