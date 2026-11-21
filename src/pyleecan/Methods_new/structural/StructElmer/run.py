from ....classes_common.parents import container_or_parent
from ...simulation.Input import InputError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.output.output import Output


def run(self, output: Output | None = None) -> None:
    """Run the Structural module

    Parameters
    ----------
    output : Output, optional
        Output of the simulation (default: the parent of the simulation)
    """
    output = container_or_parent(self, output, "output", depth=2)
    if output is None and self.parent is None:
        raise InputError(
            "ERROR: The Structural object must be in a Simulation object to run"
        )
    if output is None:
        raise InputError(
            "ERROR: The Simulation object must be in an Output object to run"
        )

    self.comp_axes(output)

    # setup the mesh
    mesh_names = self.gen_mesh(output)

    # setup the Elmer case file
    self.gen_case(output, mesh_names)

    # Compute the magnetic force according to the Force model
    self.solve_FEA(output)

    # Post processing
    self.get_meshsolution(output)
