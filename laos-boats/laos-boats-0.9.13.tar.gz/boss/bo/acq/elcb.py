import numpy as np


def elcb(x, model, params):
    """
    GP-Lower Confidence Bound acquisition function with increasing exploration

    Doesn't take any parameters (apart from the model).
    explr_weight = sqrt( 2*log[ ( i^((dim/2) + 2)*pi^(2) ) / ( 3*0.1 ) ] )
    """
    ndata = model.X.shape[0]
    dim = model.X.shape[1]
    upstairs = (ndata**((dim/2.) + 2.))*(np.pi**2.)
    downstairs = 3*0.1
    explr_weight = np.sqrt(2*np.log10(upstairs/downstairs))

    m, s, dmdx, dsdx = model.predictive_m_s_grad(x)
    f_acqu = m - explr_weight * s
    df_acqu = dmdx - explr_weight * dsdx
    scipygradient = np.asmatrix(df_acqu).transpose()
    return f_acqu, scipygradient


