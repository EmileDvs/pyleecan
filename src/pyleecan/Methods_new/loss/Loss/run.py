from ...simulation.Input import InputError


def run(self) -> None:
    """Run the Loss module

    Parameters
    ----------
    self : Loss
        A Loss model
    """
    if self.parent is None:
        raise InputError("The Loss object must be in a Simulation object to run")
    if self.parent.parent is None:
        raise InputError("The Loss object must be in an Output object to run")

    self.get_logger().info("Running Loss module")

    # get output
    output = self.parent.parent

    # Merge stator and rotor frame magnetic solutions once for all loss models
    meshsol = output.mag.get_meshsolution()

    axes_dict = self.comp_axes(output, meshsol=meshsol)
    # Comp and store in output
    self.comp_all_losses(axes_dict, meshsol=meshsol)
