# Experimental pydantic model generated from Generator/ClassesRef/Import/ImportMatrixXls.csv
"""Generated experimental pydantic model; do not edit by hand."""

import os
from typing import Any, ClassVar

from pandas import ExcelFile, read_excel
from pydantic import Field

from ...classes_common.errors import XlsFileError
from ...Functions_pydantic.path_tools import abs_file_path
from .import_matrix import ImportMatrix


class ImportMatrixXls(ImportMatrix):
    """Import the data from an xls file

    Attributes
    ----------
    file_path : str
        Path of the file to load
        Default: ""
    sheet : str
        Name of the sheet to load
        Default: ""
    skiprows : int
        To skip some rows in the file (header)
        Default: 0; Minimum: 0
    usecols : str or None
        list of Excel column letters and column ranges (e.g. "A:E" or "A,C,E:F")
        Default: None
    axes_colrows : dict or None
        To read axes in first line/column
        Default: None
    is_allsheets : bool
        To read all sheets in a 3D matrix
        Default: False
    """

    file_path: str = ""
    """Path of the file to load"""
    sheet: str = ""
    """Name of the sheet to load"""
    skiprows: int = Field(default=0, ge=0)
    """To skip some rows in the file (header)"""
    usecols: str | None = None
    """list of Excel column letters and column ranges (e.g. "A:E" or "A,C,E:F")"""
    axes_colrows: dict[str, Any] | None = None
    """To read axes in first line/column"""
    is_allsheets: bool = False
    """To read all sheets in a 3D matrix"""

    _package: ClassVar[str] = "Import"
    """Name of the package of the legacy class module"""

    # Inlined from Methods.Import.ImportMatrixXls.get_data
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
        file_path = abs_file_path(self.file_path, is_check=False)
        if not os.path.isfile(file_path):
            raise XlsFileError("ERROR: The xls file doesn't exist " + self.file_path)
        if self.usecols == "":
            self.usecols = None

        if self.is_allsheets:
            xl = ExcelFile("file.xlsx")
            Nsheets = len(xl.sheet_names)
            for i in range(Nsheets):
                df = read_excel(
                    file_path,
                    i,
                    header=None,
                    usecols=self.usecols,
                    skiprows=self.skiprows,
                )
                values = df.values
                # Extract axes
                if self.axes_colrows is not None:
                    axes_dict = {}
                    if len(axes_dict) == 1:
                        is_first = False
                    else:
                        is_first = True
                    for axis in self.axes_colrows:
                        if self.axes_colrows[axis] == "1":
                            if is_first:
                                axes_dict[axis] = values[0, 1:]
                                is_first = False
                            else:
                                axes_dict[axis] = values[0, :]
                            values = values[1:, :]
                        elif self.axes_colrows[axis] == "A":
                            if is_first:
                                axes_dict[axis] = values[1:, 0]
                                is_first = False
                            else:
                                axes_dict[axis] = values[:, 0]
                            values = values[:, 1:]
                        else:
                            raise Exception(
                                "ERROR: axes_colrows should contain either '1' or 'A'"
                            )

                # Transpose if necessary
                values = self.edit_matrix(values)

                # Store in 3D matrix
                if i == 0:
                    values_3d = values[..., None]
                else:
                    values_3d.append(values_3d, values[..., None], axis=-1)

            if self.axes_colrows is not None:
                return values_3d, axes_dict
            else:
                return values_3d

        else:
            df = read_excel(
                file_path,
                self.sheet,
                header=None,
                usecols=self.usecols,
                skiprows=self.skiprows,
            )
            values = df.values

            # Extract axes
            if self.axes_colrows is not None:
                axes_dict = {}
                if len(axes_dict) == 1:
                    is_first = False
                else:
                    is_first = True
                for axis in self.axes_colrows:
                    if self.axes_colrows[axis] == "1":
                        if is_first:
                            axes_dict[axis] = values[0, 1:]
                            is_first = False
                        else:
                            axes_dict[axis] = values[0, :]
                        values = values[1:, :]
                    elif self.axes_colrows[axis] == "A":
                        if is_first:
                            axes_dict[axis] = values[1:, 0]
                            is_first = False
                        else:
                            axes_dict[axis] = values[:, 0]
                        values = values[:, 1:]
                    else:
                        raise Exception(
                            "ERROR: axes_colrows should contain either '1' or 'A'"
                        )
            else:
                axes_dict = None

            # Transpose if necessary
            values = self.edit_matrix(values)

            if self.axes_colrows is not None:
                return values, axes_dict
            else:
                return values
