import math
import numpy as np
from scipy.linalg.blas import drot, drotg
from innovations import Innovations
import models


# np.seterr(all='raise')

def cholupdate(R, z):
    n = z.shape[0]
    for k in range(n):
        c, s = drotg(R[k, k], z[k])
        drot(R[k, :], z, c, s, overwrite_x=True, overwrite_y=True)
    return R


def choldowndate(R, z):
    n = R.shape[0]
    for k in range(n):
        if (R[k, k] - z[k]) * (R[k, k] + z[k]) < 0: return R
        rbar = np.sqrt((R[k, k] - z[k]) * (R[k, k] + z[k]))
        for j in range(k + 1, n):
            R[k, j] = 1. / rbar * (R[k, k] * R[k, j] - z[k] * z[j])
            z[j] = 1. / R[k, k] * (rbar * z[j] - z[k] * R[k, j])
        R[k, k] = rbar
    return R


def temporal_update(xhat, S, m):
    X = m.va(m.X(xhat, S))
    xhat = m.Wm @ X.T
    for i in range(7): m.Xtil[:, i] = X[:, i] - xhat
    q, r = np.linalg.qr(np.concatenate([math.sqrt(m.Wc[1]) * m.Xtil[:, 1:], m.Sw], 1))
    S = cholupdate(r.T[0:3, 0:3], m.Wc[0] * m.Xtil[:, 0])
    return xhat, S, X


def observational_update(xhat, S, X, obs, m):
    Y = m.vc(m.Xhat(X))
    yhat = m.Wm @ Y.T
    for i in range(7): m.Ytil[0, i] = Y[i] - yhat
    q, r = np.linalg.qr(np.concatenate([math.sqrt(m.Wc[1]) * m.Ytil[:, 1:], m.Sv], 1))
    Sy = cholupdate(r.T[0:1, 0:1], m.Wc[0] * m.Ytil[:, 0])
    for i in range(7): m.Pxy[:, 0] = m.Pxy[:, 0] + m.Wc[i] * m.Xtil[:, i] * m.Ytil.T[i, :]
    if Sy[0, 0] < math.sqrt(10) or Sy[0, 0] > math.sqrt(1000): Sy[0, 0] = math.sqrt(1000)
    K = m.Pxy / Sy[0, 0] ** 2
    U = K * Sy
    xhat = xhat + K[:, 0] * (obs - yhat)
    S = choldowndate(S, U)
    return xhat, S, yhat


class Modern():
    def __init__(self, mode, plot=True):
        self.log = []
        if mode == 'spkf1':
            m = models.Jazwinski1()
            self.spkf1(m)
        elif mode == 'spkf2':
            m = models.Jazwinski2()
            self.spkf2(m)
        innov = Innovations(self.log)
        if plot: innov.plot_standard()

    def spkf1(self, m):
        xhat = 2.2
        Ptil = .01
        for step in m.steps():
            X = m.va(m.X(xhat, Ptil))
            Ptil = m.W @ np.power(X - m.W @ X, 2) + m.Rww
            Y = m.vc(m.Xhat(X, m.Rww))
            Rksiksi = m.W @ np.power(Y - m.W @ Y, 2) + m.Rvv
            RXtilksi = m.W @ np.multiply(X - m.W @ X, Y - m.W @ Y)
            K = RXtilksi / Rksiksi
            yhat = m.W @ Y
            xhat = m.W @ X + K * (step[2] - m.W @ Y)
            Ptil = Ptil - K * Rksiksi * K
            self.log.append([step[0], xhat, yhat, step[1] - xhat, step[2] - yhat])

    def spkf2(self, m):
        xhat = np.array([2.0, .055, .044])
        S = np.linalg.cholesky(.1 * np.eye(3))
        for step in m.steps():
            xhat, S, X = temporal_update(xhat=xhat, S=S, m=m)
            xhat, S, yhat = observational_update(xhat=xhat, S=S, X=X, obs=step[2], m=m)
            self.log.append([step[0], xhat[0], yhat, step[1][0] - xhat[0], step[2] - yhat])


if __name__ == "__main__":
    # Modern('spkf1')
    Modern('spkf2')
