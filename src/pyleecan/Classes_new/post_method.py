# Experimental dataclass generated from Generator/ClassesRef/Post/PostMethod.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

from .post import Post


@dataclass(eq=False)
class PostMethod(Post):
    """Abstract class for post-processing defined in the method run

    Attributes
    ----------
    """

    # Inlined from Methods.Post.PostMethod.run
    def run(self, output):
        """Method to raise an NotImplementedError"""
        raise NotImplementedError
