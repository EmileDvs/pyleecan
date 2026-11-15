# Experimental pydantic model generated from Generator/ClassesRef/Import/ImportMatrixVal.csv
"""Generated experimental pydantic model; do not edit by hand."""

from typing import ClassVar

from .._pyleecan_model import NDArray
from .import_matrix import ImportMatrix


class ImportMatrixVal(ImportMatrix):
    """Import directly the value from the object

    Attributes
    ----------
    value : ndarray or None
        The matrix to return
        Default: None
    """

    value: NDArray | None = None
    """The matrix to return"""

    _package: ClassVar[str] = "Import"
    """Name of the package of the legacy class module"""

    # Inlined from Methods.Import.ImportMatrixVal.get_data
    def get_data(self):
        """Return the object's matrix

        Parameters
        ----------
        self : ImportMatrixVal
            An ImportMatrixVal object

        Returns
        -------
        matrix: ndarray
            The object's matrix

        """

        return self.edit_matrix(self.value)
