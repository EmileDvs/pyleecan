import numpy as np
from scipy.optimize import curve_fit


@staticmethod
def comp_loss_val(xdata, k_hy, k_ed, k_ex, alpha_B):
    """A function that compute the loss with respect to the maximum value and the frequency of the magnetic flux density

    Parameters
    ----------
    xdata : ndarray
        input matrix with f in the first line and B in the second line
    k_hy : float
        hysteresis loss coefficient
    k_ed : float
        Eddy current loss coefficient
    k_ex : float
        excess loss coefficient
    alpha_B : float
        hysteresis flux density amplitude exponent

    Returns
    -------
    loss : ndarray
        loss for each value of f and B in the input array
    """

    f = xdata[0]
    B = xdata[1]

    return k_hy * f * B**alpha_B + k_ed * (f * B) ** 2 + k_ex * (f * B) ** 1.5


def comp_coeff(self, material):
    """Enables to compute the coefficients of the loss model with a curve fitting
    on loss data stored in the material (stored in self.k_hy, self.k_ed, self.k_ex)

    Parameters
    ----------
    self : LossModelBertotti
        A loss model to compute Bertotti losses
    material : Material
        A material object, corresponding to the material used in the electrical machine.
        This material object must contain loss data as an ImportMatrixVal object.
        This matrix must contain 3 rows, correspoding to the excitation frequency (Hz),
        the peak magnetic flux density (T), and the loss density (W/kg) in this order.
    """

    def comp_loss(xdata, k_hy, k_ed, k_ex, alpha_B):
        """A function that compute the loss with respect to the maximum value and the frequency of the magnetic flux density

        Parameters
        ----------
        xdata : ndarray
            input matrix with f in the first line and B in the second line
        k_hy : float
            hysteresis loss coefficient
        k_ed : float
            Eddy current loss coefficient
        k_ex : float
            excess loss coefficient
        alpha_B : float
            hysteresis loss exponenent

        Returns
        -------
        loss : ndarray
            loss for each value of f and B in the input array
        """

        if self.k_hy is not None:
            k_hy = self.k_hy
        if self.k_ed is not None:
            k_ed = self.k_ed
        if self.k_ex is not None:
            k_ex = self.k_ex
        if self.alpha_B is not None:
            alpha_B = self.alpha_B

        return comp_loss_val(xdata, k_hy, k_ed, k_ex, alpha_B)

    loss_data = material.mag.LossData.get_data()

    f = loss_data[0]
    B = loss_data[1]
    loss = loss_data[2]

    xdata = np.array([f, B])
    ydata = np.array(loss)

    popt, _ = curve_fit(
        comp_loss, xdata, ydata, bounds=([0, 0, 0, 0], [np.inf, np.inf, np.inf, np.inf])
    )

    if self.k_hy is None:
        # Hysteresis loss coefficient [W/kg]
        self.k_hy = popt[0]

    if self.k_ed is None:
        # Eddy current loss coefficient [W/kg]
        self.k_ed = popt[1]

    if self.k_ex is None:
        # Excess loss coefficient [W/kg]
        self.k_ex = popt[2]

    if self.alpha_B is None:
        # Hysteresis loss exponent for B
        self.alpha_B = popt[3]
