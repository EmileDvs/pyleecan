from numpy import concatenate, unique
from SciDataTool import Data1D


def comp_axes(self, output, meshsol=None):
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

    axes_list = meshsol.get_solution().field.get_axes()
    Time = axes_list[0]

    freqs = Time.get_values(is_oneperiod=True, operation="time_to_freqs")

    if "antiperiod" in Time.symmetries:
        Time_per = Time.copy()
        Time_per.symmetries = {"period": Time.symmetries["antiperiod"]}
        freqs_per = Time_per.get_values(is_oneperiod=True, operation="time_to_freqs")
        freqs = unique(concatenate((freqs, freqs_per)))

    Freqs = Data1D(
        name="freqs", unit="Hz", values=freqs, normalizations=Time.normalizations.copy()
    )

    axes_dict = {"freqs": Freqs, "indice": axes_list[1]}

    return axes_dict
