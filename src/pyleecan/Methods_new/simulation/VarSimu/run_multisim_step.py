from logging import WARNING

from ....loggers import CONSOLE_LEVEL
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.simulation.simulation import Simulation


@staticmethod
def run_multisim_step(
    simulation: Simulation,
    datakeeper_list,
    stop_if_error: bool,
    post_keeper_postproc_list: list | None = None,
    simu_type: str | None = None,
):
    """Execute a simulation step of a multi-simulation and run datakeepers

    Parameters
    ----------
    simulation: Simulation
        Simulation to run
    datakeeper_list
        List of datakeeper to run and update results
    stop_if_error: bool
        True: Raises an error if the simulation fails
    post_keeper_postproc_list : list
        list of postprocessing to run after the datakeeper
    simu_type : str
        To adapt the text ex: "Variable Load Results"
    """
    # Change console logger level from a specific layer (if requested)
    from ....Classes_new.simulation.var_simu import VarSimu
    if (
        simulation.layer_log_warn is not None
        and simulation.layer >= simulation.layer_log_warn
    ):
        simulation.get_logger().handlers[0].level = WARNING

    # Run the simulation with/without error handling
    if stop_if_error:
        is_error = False
        result = simulation.run()
    else:
        try:
            result = simulation.run()
            is_error = False
        except Exception as err:
            print(err)
            is_error = True
            result = None

    # Revert logger level
    simulation.get_logger().handlers[0].level = CONSOLE_LEVEL

    # Datakeepers
    index = simulation.index
    if is_error:  # Execute error_keeper
        for datakeeper in datakeeper_list:
            if datakeeper.error_keeper is None:
                value = None
            else:
                value = datakeeper.error_keeper(simulation)
            if simulation.index is None:  # index == None => ref simu
                datakeeper.result_ref = value
            else:
                datakeeper.result[index] = value
    else:  # Execute Normal DataKeeper
        for datakeeper in datakeeper_list:
            # Run and store Datakeeper
            try:
                value = datakeeper.keeper(result)
            except Exception as e:
                simulation.get_logger().error(
                    "ERROR while calling DataKeeper "
                    + datakeeper.name
                    + " for simulation "
                    + str(index)
                    + ":\n"
                    + str(e)
                )
                if stop_if_error:
                    raise e
                value = datakeeper.error_keeper(simulation)
            if simulation.index is None:  # index == None => ref simu
                datakeeper.result_ref = value
            else:
                datakeeper.result[index] = value
        VarSimu.log_datakeeper_step_result(simulation, datakeeper_list, index, simu_type)

        # Run Post datakeeper post-processings
        if post_keeper_postproc_list is not None:
            for postproc in post_keeper_postproc_list:
                postproc.run(result)
    return result
