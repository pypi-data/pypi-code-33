import pint
from numpy import log


ureg = pint.UnitRegistry(system="mks")
Q_ = ureg.Quantity

R = Q_(8.31e-3, "kJ / mol / K")
LOG10 = log(10)
FARADAY = Q_(96.485, "kC / mol")
default_T = Q_(298.15, "K")
default_I = Q_(0.25, "M")
default_pH = Q_(7.0)
default_pMg = Q_(10)
default_RT = R * default_T
default_c_mid = Q_(1e-3, "M")
default_c_range = (Q_(1e-6, "M"), Q_(1e-2, "M"))
dG0_f_Mg = Q_(-455.3, "kJ/mol")  # Mg2+ formation energy

standard_concentration = Q_(1.0, "M")
physiological_concentration = Q_(1.0e-3, "M")

# Approximation of the temperature dependency of ionic strength effects

# Debye-Hueckel
@ureg.check("[concentration]", "[temperature]")
def debye_hueckel(ionic_strength: float, temperature: float) -> float:
    """For the Legendre transform to convert between chemical and biochemical
    Gibbs energies, we use the extended Debye-Hueckel theory to calculate the
    dependence on ionic strength and temperature.

    :param ionic_strength: in Molar
    :param temperature:  in Kelvin
    :return: the ionic-strength-dependent transform coefficient (in units of RT)
    """
    if ionic_strength <= 0.0:
        return Q_(0.0)

    _a1 = Q_(1.108, "1 / M**0.5")
    _a2 = Q_(1.546e-3, "1 / M**0.5 / K")
    _a3 = Q_(5.959e-6, "1 / M**0.5 / K**2")
    alpha = _a1 - _a2 * temperature + _a3 * temperature ** 2
    B = Q_(1.6, "1 / M**0.5")

    return alpha * ionic_strength ** 0.5 / (1.0 + B * ionic_strength ** 0.5)


@ureg.check(None, "[concentration]", "[temperature]", None, None)
def legendre_transform(
    p_h: float,
    ionic_strength: float,
    temperature: float,
    num_protons: int,
    charge: int,
) -> float:

    """Calculate the Legendre Transform value for a certain microspecie
    at a certain pH, I, T

    :param p_h:
    :param ionic_strength:
    :param temperature:
    :param num_protons:
    :param charge:
    :return: the transformed relative deltaG (in units of RT)
    """

    # the DH factor in units of RT
    DH = debye_hueckel(ionic_strength, temperature)

    return (
        num_protons * LOG10 * p_h * Q_("dimensionless")
        + (num_protons - charge ** 2) * DH
    )


POSSIBLE_REACTION_ARROWS = (
    "<->",
    "<=>",
    "-->",
    "<--",  # 3-character arrows
    "=>",
    "<=",
    "->",
    "<-",  # 2-character arrows
    "=",
    "⇌",
    "⇀",
    "⇋",
    "↽",
)  # 1-character arrows
