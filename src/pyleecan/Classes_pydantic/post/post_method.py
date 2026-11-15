# Experimental pydantic model generated from Generator/ClassesRef/Post/PostMethod.csv
"""Generated experimental pydantic model; do not edit by hand."""

from typing import ClassVar

from .post import Post


class PostMethod(Post):
    """Abstract class for post-processing defined in the method run

    Attributes
    ----------
    """

    _package: ClassVar[str] = "Post"
    """Name of the package of the legacy class module"""

    # Inlined from Methods.Post.PostMethod.run
    def run(self, output):
        """Method to raise an NotImplementedError"""
        raise NotImplementedError
