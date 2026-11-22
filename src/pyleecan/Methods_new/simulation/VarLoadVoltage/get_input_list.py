from ....classes_common.parents import container_or_parent
from ....Classes_new.simulation.input_voltage import InputVoltage
from ....Classes_new.simulation.simulation import Simulation


def get_input_list(self, simu: Simulation | None = None):
    """Return a list of InputVoltage to set the Operating point

    Parameters
    ----------
    self : VarLoadVoltage
        A VarLoadVoltage object
    simu : Simulation, optional
        Simulation holding the object (default: the parent)
    """
    simu = container_or_parent(self, simu, "simu")

    # Check that the object has the correct type
    assert isinstance(simu, Simulation)
    ref_simu = simu
    assert isinstance(ref_simu.input, InputVoltage)

    OP_list = self.OP_matrix.get_OP_list()
    N_simu = len(OP_list)

    # Generate initial input_list
    ref_input = ref_simu.input.copy()
    input_list = [ref_input.copy() for ii in range(N_simu)]

    # Set default time vector (enforce definition Nt_tot, Nrev)
    if ref_input.Nt_tot is None:
        Nt_tot = len(ref_input.time.get_data())
    else:
        Nt_tot = ref_input.Nt_tot

    # Update OP according to OP_matrix
    for ii in range(N_simu):
        input_list[ii].OP = OP_list[ii]
        # Edit time vector
        input_list[ii].time = None
        input_list[ii].Nt_tot = Nt_tot
        input_list[ii].Nrev = ref_input.Nrev

    return input_list
