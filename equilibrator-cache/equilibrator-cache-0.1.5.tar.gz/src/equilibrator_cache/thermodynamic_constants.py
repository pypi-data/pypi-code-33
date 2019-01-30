import pint
from numpy import log


ureg = pint.UnitRegistry(system='mks')

kJ_per_mol = 1e3 * ureg.joule / ureg.mol
kC_per_mol = 1e3 * ureg.coulomb / ureg.mol

R = 8.31e-3 * kJ_per_mol / ureg.kelvin
Rlog10 = R * log(10)
FARADAY = 96.485 * kC_per_mol
default_T = 298.15 * ureg.kelvin
default_I = 0.25 * ureg.molar
default_pH = 7.0
default_c0 = 1 * ureg.molar
default_pMg = 10
default_RT = R * default_T
default_c_mid = 1e-3  # M
default_c_range = (1e-6 * ureg.molar, 1e-2 * ureg.molar)
dG0_f_Mg = -455.3e3 * kJ_per_mol # Mg2+ formation energy

standard_concentration = 1.0 * ureg.molar
physiological_concentration = 1.0e-3 * ureg.molar

symbol_d_G = "&Delta;G"
symbol_d_G0 = "&Delta;G&deg;"
symbol_d_G_prime = "&Delta;G'"
symbol_d_G0_prime = "&Delta;G'&deg;"

symbol_dr_G = "&Delta;<sub>r</sub>G"
symbol_dr_G0 = "&Delta;<sub>r</sub>G&deg;"
symbol_dr_G_prime = "&Delta;<sub>r</sub>G'"
symbol_dr_G0_prime = "&Delta;<sub>r</sub>G'&deg;"
symbol_dr_Gc_prime = "&Delta;<sub>r</sub>G'<sup>c</sup>"

symbol_df_G = "&Delta;<sub>f</sub>G"
symbol_df_G0 = "&Delta;<sub>f</sub>G&deg;"
symbol_df_G_prime = "&Delta;<sub>f</sub>G'"
symbol_df_G0_prime = "&Delta;<sub>f</sub>G'&deg;"

# Approximation of the temperature dependency of ionic strength effects

# Debye-Hueckel
@ureg.check('molar', 'kelvin')
def debye_hueckel(ionic_strength: float, temperature:float) -> float:
    """For the Legendre transform to convert between chemical and biochemical
    Gibbs energies, we use the extended Debye-Hueckel theory to calculate the
    dependence on ionic strength and temperature.

    :param ionic_strength: in Molar
    :param temperature:  in Kelvin
    :return: the ionic-strength-dependent transform coefficient (in units of RT)
    """
    if ionic_strength <= 0.0:
        return 0.0 * ureg('dimensionless')

    _a1 = 1.108 * ureg.molar**(-0.5)
    _a2 = 1.546e-3 * ureg.molar**(-0.5) * ureg.kelvin**(-1)
    _a3 = 5.959e-6 * ureg.molar**(-0.5) * ureg.kelvin**(-2)
    alpha = _a1  - _a2 * temperature + _a3 * temperature**2
    B = 1.6 * ureg.molar**(-0.5)

    return alpha * ionic_strength**0.5 / (1.0 + B * ionic_strength**0.5)

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
