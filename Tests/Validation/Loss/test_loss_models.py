import numpy as np
import pytest

from pyleecan.Classes.ImportMatrixVal import ImportMatrixVal
from pyleecan.Classes.LossModelBertotti import LossModelBertotti
from pyleecan.Classes.LossModelSteinmetz import LossModelSteinmetz
from pyleecan.Classes.Material import Material
from pyleecan.Classes.MatMagnetics import MatMagnetics

BERTOTTI_PARAMETERS = {
    "k_hy": 0.25,
    "k_ed": 0.08,
    "k_ex": 0.12,
    "alpha_B": 1.7,
}

PARAMETERS = {
    "k_hy": 0.25,
    "k_ed": 0.08,
    "alpha_f": 1.3,
    "alpha_B": 1.7,
}


def make_bertotti_material(parameters=BERTOTTI_PARAMETERS):
    freq, flux_density = np.meshgrid(
        np.linspace(1.0, 8.0, 8),
        np.linspace(0.15, 0.95, 9),
    )
    loss_density = (
        parameters["k_hy"] * freq * flux_density ** parameters["alpha_B"]
        + parameters["k_ed"] * (freq * flux_density) ** 2
        + parameters["k_ex"] * (freq * flux_density) ** 1.5
    )
    loss_data = np.vstack((freq.ravel(), flux_density.ravel(), loss_density.ravel()))

    return Material(mag=MatMagnetics(LossData=ImportMatrixVal(value=loss_data)))


def make_material(parameters=PARAMETERS):
    freq, flux_density = np.meshgrid(
        np.linspace(1.0, 8.0, 8),
        np.linspace(0.15, 0.95, 9),
    )
    loss_density = (
        parameters["k_hy"]
        * freq ** parameters["alpha_f"]
        * flux_density ** parameters["alpha_B"]
        + parameters["k_ed"] * (freq * flux_density) ** 2
    )
    loss_data = np.vstack((freq.ravel(), flux_density.ravel(), loss_density.ravel()))

    return Material(mag=MatMagnetics(LossData=ImportMatrixVal(value=loss_data)))


def test_comp_coeff_fits_all_parameters():
    model = LossModelSteinmetz()

    model.comp_coeff(make_material())

    for parameter, expected in PARAMETERS.items():
        assert getattr(model, parameter) == pytest.approx(expected, rel=1e-4)


@pytest.mark.parametrize("fixed_parameter", PARAMETERS)
def test_comp_coeff_preserves_enforced_parameter(fixed_parameter):
    fixed_value = PARAMETERS[fixed_parameter] * 1.3
    parameters = {**PARAMETERS, fixed_parameter: fixed_value}
    model = LossModelSteinmetz(**{fixed_parameter: fixed_value})

    model.comp_coeff(make_material(parameters))

    assert getattr(model, fixed_parameter) == fixed_value


def test_bertotti_comp_coeff_fits_all_parameters():
    model = LossModelBertotti()

    model.comp_coeff(make_bertotti_material())

    for parameter, expected in BERTOTTI_PARAMETERS.items():
        assert getattr(model, parameter) == pytest.approx(expected, rel=1e-4)


@pytest.mark.parametrize("fixed_parameter", BERTOTTI_PARAMETERS)
def test_bertotti_comp_coeff_preserves_enforced_parameter(fixed_parameter):
    fixed_value = BERTOTTI_PARAMETERS[fixed_parameter] * 1.3
    parameters = {**BERTOTTI_PARAMETERS, fixed_parameter: fixed_value}
    model = LossModelBertotti(**{fixed_parameter: fixed_value})

    model.comp_coeff(make_bertotti_material(parameters))

    assert getattr(model, fixed_parameter) == fixed_value
