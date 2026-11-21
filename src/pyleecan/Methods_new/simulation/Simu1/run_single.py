from ....classes_common.logger_context import get_logger
from ..Input import InputError
from ....Classes_new.post.post_function import PostFunction
from ....Classes_new.post.post_method import PostMethod


def run_single(self) -> None:
    """Run the simulation

    Parameters
    ----------
    self : Simu1
        A Simu1 object

    """
    logger = get_logger(self)

    if self.parent is None:
        raise InputError("ERROR: Simulation object must be inside an Output object")
    output = self.parent
    output.geo = self.machine.comp_output_geo()

    # Init the input of the first module
    self.input.gen_input()

    # Run the modules
    if self.elec is not None:
        self.elec.run(output=output)
    if self.mag is not None:
        self.mag.run(output=output)

    if self.force is not None:
        self.force.run(output=output)
    # if self.HT is not None:
    #     self.HT.run()
    if self.struct is not None:
        self.struct.run(output=output)
    # if self.ac is not None:
    #     self.ac.run()

    if self.loss is not None:
        self.loss.run(output=output)
    # Running postprocessings

    if self.postproc_list:
        logger.info("Running simulation postprocessings...")
        for postproc in self.postproc_list:
            postproc.run(output)
