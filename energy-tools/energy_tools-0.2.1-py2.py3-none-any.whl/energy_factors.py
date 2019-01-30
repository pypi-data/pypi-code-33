def utilisation_factor(hours_list, p_list, p):
    """Returns the utilisation factor based on the active power during a year.

    Args:
        hours_list: List of duration in hours for each active power in p_list.
        p_list: List of active power at each hour.
        p: Nominal active power (single value).

    Returns:
        Utilisation factor in per unit.
    """
    if len(hours_list) != len(p_list):
        raise ValueError("hours_list and p_mw_list must have the same length.")

    p_pu = []
    for i in range(len(hours_list)):
        p_pu.append(p_list[i] / p)

    e_pu = []
    for i in range(len(hours_list)):
        e_pu.append(hours_list[i] * p_pu[i])

    return sum(e_pu) / (24 * 365.25)


def loss_factor(hours_list, p_list, p):
    """Returns the loss factor based on the active power during a year.

    Args:
        hours_list: List of duration in hours for each active power in p_list.
        p_list: List of active power at each hour.
        p: Nominal active power (single value).

    Returns:
        Loss factor in per unit.
    """
    p_pu = []
    for i in range(len(hours_list)):
        p_pu.append(p_list[i] / p)

    e2_pu = []
    for i in range(len(hours_list)):
        e2_pu.append(hours_list[i] * pow(p_pu[i], 2))

    return sum(e2_pu) / (24 * 365.25)
