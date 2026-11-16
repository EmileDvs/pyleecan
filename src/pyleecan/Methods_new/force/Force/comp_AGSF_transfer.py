import numpy as np

from ....Classes_new.scidatatool.data_1d import Data1D
from ....Classes_new.scidatatool.data_freq import DataFreq
from ....Classes_new.scidatatool.vector_field import VectorField
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.scidatatool.data import Data
    from ....Classes_new.output.output import Output


def comp_AGSF_transfer(self, output: Output, rnoise=None) -> None:
    """Method to compute Air-Gap Surface Force transfer from middle air-gap
    radius to stator bore radius.

    From publication:
        PILE, Raphaël, LE BESNERAIS, Jean, PARENT, Guillaume, et al. Analytical
        study of air-gap surface force–application to electrical machines. Open
        Physics, 2020, vol. 18, no 1, p. 658-673.
        https://www.degruyter.com/view/journals/phys/18/1/article-p658.xml

    Parameters
    ----------
    self: Force
        a Force object
    output : Output
        an Output object

    """

    # Inputs
    Rag = output.force.Rag

    if self.Rsbo_enforced_transfer is None:
        Rsbo = output.simu.machine.stator.Rint
    else:
        Rsbo = self.Rsbo_enforced_transfer

    AGSF = output.force.AGSF

    arg_list = ["freqs", "wavenumber"]
    result_freq = AGSF.get_rphiz_along(*arg_list)
    Prad_wr = result_freq["radial"]
    Ptan_wr = result_freq["tangential"]
    wavenumber = result_freq["wavenumber"]
    freqs = result_freq["freqs"]
    Nf = len(freqs)

    Ratio = Rag / Rsbo

    # Transfer coefficients Eq. (46)
    Sn = (Ratio**2) * (np.power(Ratio, wavenumber) + np.power(Ratio, -wavenumber)) / 2
    Cn = (Ratio**2) * (np.power(Ratio, wavenumber) - np.power(Ratio, -wavenumber)) / 2

    # Noise filtering (useful with magnetic FEA)
    if rnoise is not None:
        Inoise = np.where(abs(wavenumber) > rnoise)[0]
        Sn[Inoise] = 1
        Cn[Inoise] = 0

    XSn = np.repeat(Sn[..., np.newaxis], Nf, axis=1).transpose()
    XCn = np.repeat(Cn[..., np.newaxis], Nf, axis=1).transpose()

    # Transfer law Eq. (45)
    Prad_wr_TR = np.multiply(XSn, Prad_wr) + 1j * np.multiply(XCn, Ptan_wr)
    Ptan_wr_TR = np.multiply(XSn, Ptan_wr) - 1j * np.multiply(XCn, Prad_wr)

    # Save results as Data objects
    Datafreqs = Data1D(name="freqs", values=freqs)
    Datawavenumbers = Data1D(name="wavenumber", values=wavenumber)

    axes_list: list[Data] = [Datafreqs, Datawavenumbers]

    AGSF_TR = VectorField(
        name="Air gap Surface Force",
        symbol="AGSF",
    )

    AGSF_TR.components["radial"] = DataFreq(
        name="Radial AGSF",
        unit="N/m^2",
        symbol="AGSF_r",
        axes=axes_list,
        values=Prad_wr_TR,
    )

    AGSF_TR.components["tangential"] = DataFreq(
        name="Tangential AGSF",
        unit="N/m^2",
        symbol="AGSF_t",
        axes=axes_list,
        values=Ptan_wr_TR,
    )

    # Replace original AGSF
    output.force.AGSF = AGSF_TR
    output.force.Rag = Rsbo
