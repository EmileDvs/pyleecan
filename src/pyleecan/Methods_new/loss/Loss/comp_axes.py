from ....classes_common.errors import FieldMissingError
import numpy as np

from ....Classes_new.scidatatool.data_1d import Data1D
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.scidatatool.data import Data
    from ....Classes_new.mesh.mesh_solution import MeshSolution
    from ....Classes_new.output.output import Output


def comp_axes(self, output: Output, meshsol: MeshSolution | None = None) -> dict[str, Data]:
    """Compute the axes required in Loss module

    Parameters
    ----------
    self : Loss
        a Loss object
    output : Output
        an Output object (to update)
    meshsol : MeshSolution
        magnetic meshsolution with stator and rotor solutions merged (default: OutMag.get_meshsolution())

    Returns
    -------
    axes_dict: {Data}
        Dict containing Time and Angle axes including (anti-)periodicties used in any Force module
    """

    if meshsol is None:
        meshsol = output.mag.get_meshsolution()
        if meshsol is None:
            raise FieldMissingError("OutMag.meshsolution is None: the magnetic simulation stored no mesh solution")

    axes_list = meshsol.get_solution().field.get_axes()
    Time = axes_list[0]

    freqs = Time.get_values(is_oneperiod=True, operation="time_to_freqs")

    if "antiperiod" in Time.symmetries:
        Time_per = Time.copy()
        Time_per.symmetries = {"period": Time.symmetries["antiperiod"]}
        freqs_per = Time_per.get_values(is_oneperiod=True, operation="time_to_freqs")
        freqs = np.unique(np.concatenate((freqs, freqs_per)))

    Freqs = Data1D(
        name="freqs", unit="Hz", values=freqs, normalizations=Time.normalizations.copy()
    )

    axes_dict = {"freqs": Freqs, "indice": axes_list[1]}

    return axes_dict
