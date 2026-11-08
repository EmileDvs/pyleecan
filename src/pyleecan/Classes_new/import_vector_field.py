# Experimental dataclass generated from Generator/ClassesRef/Import/ImportVectorField.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass, field

from ._pyleecan_class import PyleecanClass
from .import_data import ImportData
from .vector_field import VectorField


@dataclass(eq=False)
class ImportVectorField(PyleecanClass):
    """Abstract class for Data Import/Generation

    Attributes
    ----------
    components : {ImportData}
        Dict of components (e.g. {"radial": ImportData})
        Default: {}
    name : str or None
        Name of the vector field
        Default: None
    symbol : str or None
        Symbol of the vector field
        Default: None
    """

    components: dict[str, ImportData] = field(default_factory=dict)
    """Dict of components (e.g. {"radial": ImportData})"""
    name: str | None = None
    """Name of the vector field"""
    symbol: str | None = None
    """Symbol of the vector field"""

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
