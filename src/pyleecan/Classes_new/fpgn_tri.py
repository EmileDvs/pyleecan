# Experimental dataclass generated from Generator/ClassesRef/Mesh/Interpolation/FPGNTri.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

from .gauss_point import GaussPoint


@dataclass(eq=False)
class FPGNTri(GaussPoint):
    """Store gauss point for triangle elements

    Attributes
    ----------
    nb_gauss_point : int
        Nb of gauss point to be used
        Default: 3
    """

    nb_gauss_point: int = 3
    """Nb of gauss point to be used"""

    # Inlined from Methods.Mesh.FPGNTri.get_gauss_points
    def get_gauss_points(self):
        """Return the gauss points and weights for Triangle3 element"""

        raise NotImplementedError(
            "Quadpy is not possible to use anymore, need to rewrite this method"
        )
        nb_gauss_points = self.nb_gauss_point
        scheme = quadpy.tn.grundmann_moeller(2, nb_gauss_points)
        gauss_pts = scheme.points
        weights = scheme.weights

        return gauss_pts, weights, nb_gauss_points
