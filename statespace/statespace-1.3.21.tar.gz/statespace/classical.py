import numpy as np
from innovations import Innovations
import models


def ud_factorization(M):
    assert np.allclose(M, M.T)
    n = M.shape[0]
    M = np.triu(M)
    U = np.eye(n)
    d = np.zeros(n)
    for j in reversed(range(2, n + 1)):
        d[j - 1] = M[j - 1, j - 1]
        if d[j - 1] > 0:
            alpha = 1.0 / d[j - 1]
        else:
            alpha = 0.0
        for k in range(1, j):
            beta = M[k - 1, j - 1]
            U[k - 1, j - 1] = alpha * beta
            M[0:k, k - 1] = M[0:k, k - 1] - beta * U[0:k, j - 1]
    d[0] = M[0, 0]
    return U, np.diag(d)


def temporal_update(xin, Uin, Din, m):  # thornton
    Phi, Gin, Q = m.A(xin), m.G, m.Q
    x, U, D = Phi @ xin, Uin, Din
    n, r = 3, 3
    G = Gin
    U = np.eye(3)
    PhiU = Phi @ Uin
    for i in reversed(range(3)):
        sigma = 0
        for j in range(n):
            sigma = sigma + PhiU[i, j] ** 2 * Din[j, j]
            if (j <= r - 1):
                sigma = sigma + G[i, j] ** 2 + Q[j, j]
        D[i, i] = sigma
        ilim = i - 1
        if not ilim < 0:
            for j in range(ilim):
                sigma = 0
                for k in range(n):
                    sigma = sigma + PhiU[i, k] * Din[k, k] * PhiU[j, k]
                for k in range(r):
                    sigma = sigma + G[i, k] * Q[k, k] * G[j, k]
                U[j, i] = sigma / D[i, i]
                for k in range(n):
                    PhiU[j, k] = PhiU[j, k] - U[j, i] * PhiU[i, k]
                for k in range(r):
                    G[j, k] = G[j, k] - U[j, i] * G[i, k]
    return x, U, D


def observational_update(xin, Uin, Din, obs, m):  # bierman
    R, H, yhat = m.Rvv, m.C(xin), m.c(xin)
    x, U, D = xin, Uin, Din
    a = U.T @ H.T
    b = D @ a
    dz = obs - yhat  # z - H @ xin
    alpha = R
    gamma = 1 / alpha
    for j in range(3):
        beta = alpha
        alpha = alpha + a[j] * b[j]
        lamda = -a[j] * gamma
        gamma = 1 / alpha
        D[j, j] = beta * gamma * D[j, j]
        jlim = j - 1
        if not jlim < 0:
            for i in range(jlim):
                beta = U[i, j]
                U[i, j] = beta + b[i] * lamda
                b[i] = b[i] + b[j] * beta
    dzs = gamma * dz
    x = x + dzs * b
    return x, U, D, yhat


class Classical():
    def __init__(self, mode, plot=True):
        self.log = []
        if mode == 'kf':
            m = models.Jazwinski1()
            self.kf(m)
        elif mode == 'ekf1':
            m = models.Jazwinski1()
            self.ekf1(m)
        elif mode == 'ekf2':
            m = models.Jazwinski2()
            self.ekf2(m)
        innov = Innovations(self.log)
        if plot: innov.plot_standard()

    def kf(self, m):
        xhat = 2.2
        Ptil = .01
        for step in m.steps():
            xref = 2. + .067 * step[0]
            xhat = m.a(xref, 0) + m.A(xref) * (xhat - xref)
            Ptil = m.A(xref) * Ptil * m.A(xref)
            Ree = m.C(xref) * Ptil * m.C(xref) + m.Rvv
            K = Ptil * m.C(xref) / Ree
            yhat = m.c(xref, 0) + m.C(xref) * (xhat - xref)
            xhat = xhat + K * (step[2] - yhat)
            Ptil = (1 - K * m.C(xref)) * Ptil
            self.log.append([step[0], xhat, yhat, step[1] - xhat, step[2] - yhat])

    def ekf1(self, m):
        xhat = 2.2
        Ptil = .01
        for step in m.steps():
            xhat = m.a(xhat)
            Ptil = m.A(xhat) * Ptil * m.A(xhat)
            Ree = m.C(xhat) * Ptil * m.C(xhat) + m.Rvv
            K = Ptil * m.C(xhat) / Ree
            yhat = m.c(xhat)
            xhat = xhat + K * (step[2] - yhat)
            Ptil = (1 - K * m.C(xhat)) * Ptil
            self.log.append([step[0], xhat, yhat, step[1] - xhat, step[2] - yhat])

    def ekf2(self, m):
        xhat = np.array([2, .055, .044])
        U, D = ud_factorization(1. * np.eye(3))
        for step in m.steps():
            xhat, U, D = temporal_update(xin=m.a(xhat), Uin=U, Din=D, m=m)
            xhat, U, D, yhat = observational_update(xin=xhat, Uin=U, Din=D, obs=step[2], m=m)
            self.log.append([step[0], xhat[0], yhat, step[1][0] - xhat[0], step[2] - yhat])


if __name__ == "__main__":
    Classical('ekf1')
    Classical('ekf2')
