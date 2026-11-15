# Experimental dataclass generated from Generator/ClassesRef/Import/ImportVectorField.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass, field
from typing import ClassVar

from .._pyleecan_class import PyleecanClass
from ..scidatatool.vector_field import VectorField
from .import_data import ImportData


@dataclass(eq=False)
class ImportVectorField(PyleecanClass):
    """Abstract class for Data Import/Generation

    Attributes
    ----------
    components : {ImportData}
        Dict of components (e.g. {"radial": ImportData})
        Default: {}
    name : str
        Name of the vector field
        Default: ""
    symbol : str
        Symbol of the vector field
        Default: ""
    """

    components: dict[str, ImportData] = field(default_factory=dict)
    """Dict of components (e.g. {"radial": ImportData})"""
    name: str = ""
    """Name of the vector field"""
    symbol: str = ""
    """Symbol of the vector field"""

    _package: ClassVar[str] = "Import"
    """Name of the package of the legacy class module"""

    # Inlined from Methods.Import.ImportVectorField.get_data
    def get_data(self):
        """Generate VectorField object

        Parameters
        ----------
        self : ImportVectorField
            An ImportVectorField object

        Returns
        -------
        VectField: VectorField
            The generated VectorField object

        """

        comp_dict = {}
        for key, component in self.components.items():
            comp_dict[key] = component.get_data()

        VectField = VectorField(
            name=self.name, symbol=self.symbol, components=comp_dict
        )

        return VectField
