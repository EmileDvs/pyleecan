from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.scidatatool.data_nd import DataND


def get_vectorfield_along(self, *args, unit="SI", is_norm: bool = False, axis_data=[]):
    """Returns the sliced or interpolated version of the data, using conversions and symmetries if needed.
    Parameters
    ----------
    self : VectorField
        a VectorField object
    Returns
    -------
    a VectorField object
    """

    # Dynamic import to avoid loop
    module = __import__("pyleecan.Classes.VectorField", fromlist=["VectorField"])
    VectorField = module.VectorField

    comp_dict: dict[str, DataND] = dict()

    for comp in self.components:  # Call get_data_along on each component
        comp_dict[comp] = self.components[comp].get_data_along(
            *args, unit=unit, is_norm=is_norm, axis_data=axis_data
        )

    return VectorField(name=self.name, symbol=self.symbol, components=comp_dict)
