# Experimental pydantic model generated from Generator/ClassesRef/Import/ImportData.csv
"""Generated experimental pydantic model; do not edit by hand."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar

from pydantic import Field

from .._legacy_model import LegacyModel
from ..scidatatool.data_1d import Data1D
from ..scidatatool.data_freq import DataFreq
from ..scidatatool.data_time import DataTime
from .import_ import Import

if TYPE_CHECKING:
    from ..scidatatool.data import Data
    from ..scidatatool.data_nd import DataND


class ImportData(LegacyModel):
    """Abstract class for Data Import/Generation

    Attributes
    ----------
    axes : [ImportData]
        List of axes of the data
        Default: []
    field : Import or None
        Field (Import object)
        Default: None
    unit : str
        Unit of the field
        Default: "SI"
    name : str
        Name of the field
        Default: ""
    symbol : str
        Symbol of the field
        Default: ""
    normalizations : dict
        Dict of normalizations
        Default: -1
    symmetries : dict
        Dict of symmetries
        Default: -1
    """

    axes: list[ImportData] = Field(default_factory=list)
    """List of axes of the data"""
    field: Import | None = None
    """Field (Import object)"""
    unit: str = "SI"
    """Unit of the field"""
    name: str = ""
    """Name of the field"""
    symbol: str = ""
    """Symbol of the field"""
    normalizations: dict[str, Any] = Field(default_factory=dict)
    """Dict of normalizations"""
    symmetries: dict[str, Any] = Field(default_factory=dict)
    """Dict of symmetries"""

    _package: ClassVar[str] = "Import"
    """Name of the package of the legacy class module"""

    # Inlined from Methods.Import.ImportData.get_data
    def get_data(self) -> DataND:
        """Generate Data objects

        Parameters
        ----------
        self : ImportData
            An ImportData object

        Returns
        -------
        Data: DataND
            The generated Data object

        """

        axes_list: list[Data] = []
        is_freq = False
        for axis in self.axes:
            if axis.name == "freqs" or axis.name == "wavenumber":
                is_freq = True
            axes_list.append(
                Data1D(
                    values=axis.field.get_data(),
                    name=axis.name,
                    unit=axis.unit,
                    symmetries=axis.symmetries,
                    normalizations=axis.normalizations,
                )
            )

        if is_freq:
            Data = DataFreq(
                axes=axes_list,
                values=self.field.get_data(),
                name=self.name,
                symbol=self.symbol,
                unit=self.unit,
                normalizations=self.normalizations,
            )
        else:
            Data = DataTime(
                axes=axes_list,
                values=self.field.get_data(),
                name=self.name,
                symbol=self.symbol,
                unit=self.unit,
                normalizations=self.normalizations,
            )

        return Data
