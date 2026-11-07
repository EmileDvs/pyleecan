# Experimental dataclass generated from Generator/ClassesRef/Material/MatMagnetics.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

import numpy as np

from ..Functions.init_fig import init_fig
from ._pyleecan_class import PyleecanClass
from .import_matrix import ImportMatrix
from .material import Material
from .model_bh import ModelBH


@dataclass(eq=False)
class MatMagnetics(PyleecanClass):
    """magnetic material properties

    Attributes
    ----------
    mur_lin : float
        Relative magnetic permeability
        Default: 1; Minimum: 0
    Brm20 : float
        magnet remanence induction at 20degC
        Unit: T; Default: 0
    alpha_Br : float
        temperature coefficient for remanent flux density
        Default: 0
    Wlam : float
        lamination sheet width without insulation [m] (0 == not laminated)
        Unit: m; Default: 0; Minimum: 0
    BH_curve : ImportMatrix or None
        nonlinear B(H) curve (two columns matrix, H and B(H))
        Default: None
    LossData : ImportMatrix or None
        specific loss data value triplets, i.e. B, f, P
        Unit: W/kg; Default: None
    ModelBH : ModelBH or None
        a model of BH curve with an analytical expression
        Default: None
    is_BH_extrapolate : bool
        True to use ModelBH to fit input data and extrapolate BH curve
        Default: False
    """

    mur_lin: float = 1
    """Relative magnetic permeability"""
    Brm20: float = 0
    """magnet remanence induction at 20degC"""
    alpha_Br: float = 0
    """temperature coefficient for remanent flux density"""
    Wlam: float = 0
    """lamination sheet width without insulation [m] (0 == not laminated)"""
    BH_curve: ImportMatrix | None = None
    """nonlinear B(H) curve (two columns matrix, H and B(H))"""
    LossData: ImportMatrix | None = None
    """specific loss data value triplets, i.e. B, f, P"""
    ModelBH: ModelBH | None = None
    """a model of BH curve with an analytical expression"""
    is_BH_extrapolate: bool = False
    """True to use ModelBH to fit input data and extrapolate BH curve"""

    def __post_init__(self):
        super().__post_init__()

    def _assert_parent_type(self, parent):
        if parent is not None and not isinstance(parent, (Material,)):
            raise TypeError(
                "MatMagnetics parent must be an instance of Material, or None; "
                + f"got {type(parent).__name__}"
            )

    # Inlined from Methods.Material.MatMagnetics.get_BH
    def get_BH(self):
        """Return the B(H) curve of the material according to the Import object.
        If there is no B(H) curve linear data are computed from mur_lin.

        Parameters
        ----------
        self : MatMagnetics
            a MatMagnetics object

        Returns
        -------
        BH: numpy.ndarray
            B(H) values (two colums matrix: H and B(H))

        """

        if self.BH_curve is not None:
            BH = self.BH_curve.get_data()

            if len(BH.shape) != 2:
                raise BHShapeError(
                    "BH must be a two colums matrix: H and B(H). Return shape: "
                    + str(BH.shape)
                )
            if BH.shape[1] != 2:
                raise BHShapeError(
                    "BH must be a two colums matrix: H and B(H). Return shape: "
                    + str(BH.shape)
                )

            if self.is_BH_extrapolate:
                BH = self.ModelBH.fit_model(BH=BH)

        else:
            BH = self.ModelBH.get_BH()

        if self.mur_lin is None and BH is None:
            raise BHShapeError("There are no BH data availible. Check input data.")

        return BH

    # Inlined from Methods.Material.MatMagnetics.get_Brm
    def get_Brm(self, T_op=None, T_ref=20):
        """Get magnetic remanent flux density

        Parameters
        ----------
        self : MatMagnetics
            a MatMagnetics object
        T_op: float
            Material operational temperature [degC]
        T_ref: float
            Material reference temperature [degC]

        Returns
        -------
        Brm: float
            Magnetic remanent flux density

        """

        if T_op is None:
            T_op = T_ref

        # Get magnetic remanent flux density at 20 degC from excitation coercitivity
        if self.Brm20 is None:
            raise Exception("Cannot calculate Brm20 if Hc or mur_lin is None")
        else:
            Brm20 = self.Brm20

        # Update magnetic remanent flux density
        Brm = Brm20 * (1 + self.alpha_Br * (T_op - T_ref))

        return Brm

    # Inlined from Methods.Material.MatMagnetics.get_Hc
    def get_Hc(self, T_op=None, T_ref=20):
        """Get magnetic excitation coercitivity

        Parameters
        ----------
        self : MatMagnetics
            a MatMagnetics object
        T_op: float
            Material operational temperature [degC]
        T_ref: float
            Material reference temperature [degC]

        Returns
        -------
        Hc: float
            Magnetic excitation coercitivity

        """

        if T_op is None:
            T_op = T_ref

        # Calculate magnetic coercitivity at 20 degC from remanent flux density
        if self.Brm20 is None or self.mur_lin is None:
            raise Exception("Cannot calculate Hc if Brm20 or mur_lin is None")

        # Magnet coercitivity
        Hc20 = self.Brm20 / (4 * np.pi * 1e-7 * self.mur_lin)

        # Update magnetic coercitivity
        Hc = Hc20 * (1 + self.alpha_Br * (T_op - T_ref))

        return Hc

    # Inlined from Methods.Material.MatMagnetics.plot_BH
    def plot_BH(self, fig=None, grid=True, color="r", is_show_fig=True):
        """Plot the curve B(H) at the specified frequency

        Parameters
        ----------
        self : MatMagnetics
            a MatMagnetics object
        fig :
            if None, open a new fig and plot, else add to the gcf (Default value = None)

        Returns
        -------
        None
        """
        (fig, axes, patch_leg, label_leg) = init_fig(fig)

        BH = self.get_BH()

        if BH is not None:
            axes.plot(BH[:, 0], BH[:, 1], color=color)
            axes.grid(visible=True)  # param "b" of grid was removed in MPL 3.7
            axes.set_xlabel("H [A/m]")
            axes.set_ylabel("B [T]")
            axes.set_title("B(H) curve")
            if is_show_fig:
                fig.show()

        return fig

    class BHShapeError(Exception):
        """Raised when the BH curve has not the expected shape"""


BHShapeError = MatMagnetics.BHShapeError
