from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.mesh.mesh_solution import MeshSolution


def get_frame_meshsolution(self, group: str, loss_name: str = "losses") -> tuple[MeshSolution, str]:
    """Get the magnetic meshsolution and the label suffix of the frame (stator or rotor)
    in which the magnetic quantities of the group are calculated.

    Magnetic meshsolution contains solutions in stator frame (e.g. "B_S") and in rotor frame (e.g. "B_R"),
    each one defined on the elements of its frame and on its own time axis.

    Parameters
    ----------
    self : Output
        an Output object containing a magnetic meshsolution
    group : str
        name of the mesh group (e.g. "stator core", "rotor magnets")
    loss_name : str
        name of the losses to calculate (for error messages)

    Returns
    -------
    meshsol : MeshSolution
        magnetic meshsolution
    suffix : str
        "_S" for stator frame solutions, "_R" for rotor frame solutions
    """

    if self.mag is None:
        raise ValueError("Cannot calculate " + loss_name + " if OutMag is None")

    meshsol = self.mag.meshsolution

    if meshsol is None:
        raise ValueError(
            "Cannot calculate " + loss_name + " if OutMag.meshsolution is None"
        )

    if group not in meshsol.group:
        raise ValueError("Cannot calculate " + loss_name + " for group=" + group)

    suffix = "_S" if "stator" in group else "_R"

    return meshsol, suffix
