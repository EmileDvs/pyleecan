# Experimental dataclass generated from Generator/ClassesRef/Post/PostLUT.csv
"""Generated experimental dataclass; do not edit by hand."""

import os
from dataclasses import dataclass

from .post_method import PostMethod


@dataclass(eq=False)
class PostLUT(PostMethod):
    """Class to generate a LUT after the corresponding simulation

    Attributes
    ----------
    is_save_LUT : bool
        True to save LUT in PostLUT
        Default: True
    file_name : str
        File name of the file created if is_save_LUT is True
        Default: "LUT"
    """

    is_save_LUT: bool = True
    """True to save LUT in PostLUT"""
    file_name: str = "LUT"
    """File name of the file created if is_save_LUT is True"""

    # Inlined from Methods.Post.PostLUT.run
    def run(self, LUT):
        """PostProcessing to clean a LUT from un-necessary output
        after the corresponding simulation

        Parameters
        ----------
        self : PostLUT
            A PostLUT object
        LUT: LUT
            LUT object coming from LUT calculation workflow to cleanup
        """

        assert LUT.simu.var_simu.is_keep_all_output is True

        # Clean all reference Output (only use output_list)
        LUT.elec = None
        LUT.mag = None
        LUT.struct = None
        LUT.force = None
        LUT.loss = None

        # Clean all un-necessary data from output_list
        for out in LUT.output_list:
            # out.elec is not cleaned
            out.mag.clean(clean_level=5)
            out.struct = None
            out.force = None
            # out.loss = None

        # Save/Store LUT object
        if self.is_save_LUT:
            save_path = os.path.join(LUT.get_path_result(), self.file_name)
            self.get_logger().info("Saving LUT at: " + save_path)
            LUT.save(save_path=save_path)
