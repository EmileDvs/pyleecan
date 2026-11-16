# Experimental pydantic model generated from Generator/ClassesRef/Output/OutMagElmer.csv
"""Generated experimental pydantic model; do not edit by hand."""

from typing import Any, ClassVar

from .out_internal import OutInternal


class OutMagElmer(OutInternal):
    """Class to store outputs related to MagElmer magnetic model

    Attributes
    ----------
    FEA_dict : dict or None
        dictionary containing the main FEA parameters
        Default: None
    """

    FEA_dict: dict[str, Any] | None = None
    """dictionary containing the main FEA parameters"""

    _package: ClassVar[str] = "Output"
    """Name of the package of the legacy class module"""

    # Inlined from Methods.Output.OutMagElmer.clean
    def clean(self, clean_level: int = 1) -> None:
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
