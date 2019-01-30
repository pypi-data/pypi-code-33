def i_base_ka(sb_mva, vbll_kv):
    """Returns the base current based on the base power and voltage.

    Args:
        sb_mva: Base power in MVA.
        vbll_kv: Base voltage in kV.

    Returns:
        Base current in kA.
    """
    sb_mva = float(sb_mva)
    vbll_kv = float(vbll_kv)
    return sb_mva / (vbll_kv * 3 ** 0.5)


def z_base_ohm(vbll_kv, ib_ka=None, sb_mva=None):
    """Returns the base impedance based on the base voltage and either the base current
    or the base power.

    Args:
        vbll_kv: Base voltage in kV.
        sb_mva: Base power in MVA.
        ib_ka: Base current in kA.

    Returns:
        Base impedance in ohms.
    """
    vbll_kv = float(vbll_kv)
    if ib_ka is None and sb_mva is not None:
        sb_mva = float(sb_mva)
        return (vbll_kv ** 2) / sb_mva
    elif sb_mva is None and ib_ka is not None:
        ib_ka = float(ib_ka)
        return vbll_kv / (ib_ka * 3 ** 0.5)
    else:
        raise ValueError("You must provide either ib_ka or sb_mva")


def s_base_mva(vbll_kv, ib_ka):
    """Returns the base power based on the base voltage and current.

    Args:
        vbll_kv: Base voltage in kV.
        ib_ka: Base current in kA.

    Returns:
        Base power in MVA.
    """
    vbll_kv = float(vbll_kv)
    ib_ka = float(ib_ka)
    return ib_ka * vbll_kv * 3 ** 0.5
