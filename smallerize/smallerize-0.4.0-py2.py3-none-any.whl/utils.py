def _dict_product_inplace(x: dict, y: dict):
    """
    Multiply each value in ``x`` by the matching value in ``y``,
    inplace.

    :param x: dict with float/int values
    :param y: dict with same keys as ``x``
    :return: None
    """
    for k in x:
        x[k] *= y[k]


def _dict_div_inplace(x, y):
    """
    Divide each value in ``x`` by the matching value in ``y``,
    inplace.

    :param x: dict with float/int values
    :param y: dict with same keys as ``x``
    :return: None
    """
    for k in x:
        x[k] /= y[k]


def _dict_add_inplace(x, y):
    """
    Add each value in ``y`` to the matching value in ``x``,
    modifying ``x`` inplace.

    :param x: dict with float/int values
    :param y: dict with same keys as ``x``
    :return: None
    """
    for k in x:
        x[k] += y[k]
