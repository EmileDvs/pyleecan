from logging import WARNING
import traceback
import sys

from io import StringIO

import os
from datetime import datetime
import numpy as np



def evaluate(self, indiv) -> bool:
    """Evaluate the individual according to the solver method

    Parameters
    ----------
    self : Solver
        optimization solver
    indiv : individual
        individual to evaluate

    Returns
    -------
    evaluation_failure : bool
        failure of the evaluation
    """
    # Get solver logger
    logger = self.get_logger()

    tb = StringIO()  # to store the traceback in case of error

    logger.debug("Design variables :")
    for i, design_variable in enumerate(indiv.design_var_name_list):
        logger.debug(design_variable + " : " + str(indiv[i]))

    try:
        # Run the preprocessing
        if self.problem.preprocessing is not None:
            self.problem.preprocessing(indiv.output.simu)

        if self.problem.eval_func == None:
            indiv.output.simu.run()
        else:
            self.problem.eval_func(indiv.output)

        # Add the fitness values, handle exception for each fitness
        fitness = []
        for obj_func in self.problem.obj_func:
            try:
                fitness.append(float(obj_func.keeper(indiv.output)))
            # Raise KeyboardInterrupt to stop optimization
            except KeyboardInterrupt:
                raise KeyboardInterrupt

            # Except error and try to compute the error_keeper
            except Exception as err:
                logger.warning(
                    "Objectiv computation " + obj_func.name + " failed:" + str(err)
                )
                if obj_func.error_keeper is None:  # Set fitness value as infinity
                    fitness.append(float("inf"))
                else:
                    try:
                        fitness.append(float(obj_func.error_keeper(indiv.output)))
                    # Raise KeyboardInterrupt to stop optimization
                    except KeyboardInterrupt:
                        raise KeyboardInterrupt
                    # Set the fitness value as infinity
                    except Exception as err:
                        logger.warning(
                            "Objectiv error computation "
                            + obj_func.name
                            + " failed:"
                            + str(err)
                        )
                        fitness.append(float("inf"))

        # Add fitness values to indiv object
        indiv.fitness.values = fitness

        # Execute the DataKeepers
        for datakeeper in self.problem.datakeeper_list:
            try:
                datakeeper.result.append(datakeeper.keeper(indiv.output))
            except KeyboardInterrupt:
                raise KeyboardInterrupt("Stopped by the user.")
            except Exception as err:
                logger.warning(
                    "DataKeeper"
                    + datakeeper.name
                    + ".keeper execution failed:"
                    + str(err)
                )
                if datakeeper.error_keeper:
                    try:
                        datakeeper.result.append(
                            datakeeper.error_keeper(indiv.output.simu)
                        )
                    except KeyboardInterrupt:
                        raise KeyboardInterrupt("Stopped by the user.")
                    except Exception as err:
                        logger.warning(
                            "DataKeeper"
                            + datakeeper.name
                            + ".error_keeper execution failed:"
                            + str(err)
                        )
                        datakeeper.result.append(np.nan)
                else:
                    datakeeper.result.append(np.nan)

        indiv.is_simu_valid = True

        evaluation_failure = False  # Evaluation succeed

    except KeyboardInterrupt:
        raise KeyboardInterrupt("Stopped by the user.")

    except:
        # Logging
        print("The following simulation failed :", file=tb)

        if logger.level > 10:  # Log design variables values if it is not already done
            print("Design variables :", file=tb)
            for i, design_variable in enumerate(indiv.design_var_name_list):
                print(design_variable + " : " + str(indiv[i]), file=tb)

        # Log the simulation error
        traceback.print_exc(file=tb)
        logger.warning(tb.getvalue())

        # Set fitness as inf
        indiv.fitness.values = [float("inf") for _ in self.problem.obj_func]
        indiv.is_simu_valid = False

        # Execute the DataKeepers
        for datakeeper in self.problem.datakeeper_list:
            if datakeeper.error_keeper:
                try:
                    datakeeper.result.append(datakeeper.error_keeper(indiv.output.simu))
                except KeyboardInterrupt:
                    raise KeyboardInterrupt("Stopped by the user.")
                except Exception as err:
                    logger.warning(
                        "DataKeeper"
                        + datakeeper.name
                        + ".error_keeper execution failed:"
                        + str(err)
                    )
                    datakeeper.result.append(np.nan)
            else:
                datakeeper.result.append(np.nan)

        # Reset standard output and error
        evaluation_failure = True  # Evaluation failed

    return evaluation_failure
