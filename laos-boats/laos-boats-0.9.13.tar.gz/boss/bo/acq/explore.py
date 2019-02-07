import numpy as np


def explore(x, model, params):
    """
    Purely exploring acquisition function

    Doesn't take any parameters (apart from the model).
    """
    m, s, dmdx, dsdx = model.predictive_m_s_grad(x)
    f_acqu = -s
    df_acqu = -dsdx
    scipygradient = np.asmatrix(df_acqu).transpose()
    return f_acqu, scipygradient

