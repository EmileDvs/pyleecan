from ....Classes_new.scidatatool.vector_field import VectorField
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.scidatatool.data_nd import DataND


def get_data(self) -> VectorField:
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

    comp_dict: dict[str, DataND] = {}
    for key, component in self.components.items():
        comp_dict[key] = component.get_data()

    VectField = VectorField(name=self.name, symbol=self.symbol, components=comp_dict)

    return VectField
