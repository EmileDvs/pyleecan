from ....Classes_new.scidatatool.data_freq import DataFreq
from ....Classes_new.scidatatool.data_nd import DataND
from ....Classes_new.scidatatool.data_time import DataTime

from ....Classes_new.mesh.solution_data import SolutionData
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np


@staticmethod
def build_solution_data(
    field: np.ndarray, axis_list: list, name: str = "", symbol: str = "", unit: str = "", is_real: bool = True, type_element: str = "triangle"
) -> SolutionData:
    """Build the MeshSolution objets from FEMM outputs.

    Parameters
    ----------
    field : ndarray
        a data field
    axis_list : list
        a list of SciDataTool axis

    Returns
    -------
    solution: SolutionData
        a SolutionData object
    """

    if axis_list[0].name == "time":
        DataClass = DataTime
    elif axis_list[0].name == "freqs":
        DataClass = DataFreq
    else:
        DataClass = DataND

    data = DataClass(
        name=name,
        unit=unit,
        symbol=symbol,
        axes=axis_list,
        values=field,
        is_real=is_real,
    )

    return SolutionData(field=data, label=symbol, type_element=type_element)
