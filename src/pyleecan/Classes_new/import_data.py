# Experimental dataclass generated from Generator/ClassesRef/Import/ImportData.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass
from typing import Any

from ._pyleecan_class import PyleecanClass
from .data_1d import Data1D
from .data_freq import DataFreq
from .data_time import DataTime
from .import_ import Import
from .import_vector_field import ImportVectorField
from .input import Input


@dataclass(eq=False)
class ImportData(PyleecanClass):
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
    name : str or None
        Name of the field
        Default: None
    symbol : str or None
        Symbol of the field
        Default: None
    normalizations : dict
        Dict of normalizations
        Default: -1
    symmetries : dict
        Dict of symmetries
        Default: -1
    """

    axes: "list[ImportData]" = []
    """List of axes of the data"""
    field: Import | None = None
    """Field (Import object)"""
    unit: str = "SI"
    """Unit of the field"""
    name: str | None = None
    """Name of the field"""
    symbol: str | None = None
    """Symbol of the field"""
    normalizations: dict[str, Any] = field(default_factory=dict)
    """Dict of normalizations"""
    symmetries: dict[str, Any] = field(default_factory=dict)
    """Dict of symmetries"""

    def __post_init__(self):
        super().__post_init__()

    def _assert_parent_type(self, parent):
        if parent is not None and not isinstance(
            parent,
            (
                ImportVectorField,
                Input,
            ),
        ):
            raise TypeError(
                "ImportData parent must be an instance of ImportVectorField or Input, or None; "
                + f"got {type(parent).__name__}"
            )

    # Inlined from Methods.Import.ImportData.get_data
    def get_data(self):
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

        axes_list = []
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
