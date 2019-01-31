"""stc main method"""
from math import sqrt
import numpy as np
from numpy.linalg import norm, solve
from scipy.interpolate import BSpline as bsl
from scipy.spatial.distance import cosine
from scipy.stats import pearsonr
from scipy.linalg import sqrtm



class STC(object):
    """
    implements stc methods for time series
    """
    def __init__(self, Y, X, lam, rho, t_interval, norder=5, nbasis=10, n=10, tol=1e-6):
        """
        Parameters
        -------------------
        Y: N by p matrix
        X: N by q matrix
        lam, rho: list of tuning parameters
        t_interval: list of time points
        norder: order of B spline basis
        nbasis: number of basis
        n: number of seeds (different initial values)
        """
        self.Y = Y
        self.X = X
        self.lam = lam
        self.rho = rho
        self.norder = norder
        self.nbasis = nbasis
        self.t_interval = t_interval
        self.N = self.Y.shape[0]
        self.n = n
        self.p = self.Y.shape[1]
        self.q = self.X.shape[1]
        # T by nbasis
        self.phi, spl = self._generate_basis()
        # precompute
        # nbasis by n basis
        self.H = np.dot(self.phi.T, self.phi)
        self.T = self.t_interval[-1] - self.t_interval[0]
        self.G = np.dot(spl.T, spl)/1000*(self.T)
        self.tol = tol
        self.para = None
        self.cor = None
        self.f = None
        self.g = None
        self.cor_abs = None
        self.u_dif = None
        self.v_dif = None
        self.tuning = None

    def loss(self, para, lam, rho):
        """
        Calculate the value of the objective function
        """
        A, B, u, v, r_a, r_b = para['A'], para['B'], para['u'], para['v'], para['r_a'], para['r_b']
        G = self.G
        #H = self.H
        N = self.N
        phi = self.phi
        Y, X = self.Y, self.X
        T = self.T
        #print A.shape, B.shape, u.shape, v.shape, G.shape
        l1 = (np.dot(np.dot(A.T, G), A) + np.dot(np.dot(B.T, G), B) - 2*np.dot(np.dot(A.T, G), B))/T
        l2 = 1.0 * lam / N * norm(np.dot(Y, u) - r_a * np.dot(phi, A), 2) ** 2
        l3 = 1.0 * rho / N * norm(np.dot(X, v)-r_b * np.dot(phi, B), 2) ** 2
        return l1 + l2 + l3

    #TBD: linter
    def stc_main(self, lam, rho, seed):
        """
        main algorithm
        """
        np.random.seed(seed)
        para = self._generate_init(seed)
        loss0 = self.loss(para, lam, rho)
        A, B, u, v, r_a, r_b = para['A'], para['B'], para['u'], para['v'], para['r_a'], para['r_b']
        G = self.G
        T = self.T
        H = self.H
        N = self.N
        phi = self.phi
        Y, X = self.Y, self.X
        loss1 = loss0 + 1e6
        Gsqrt = sqrtm(G)
        iters = 0
        A = A / norm(np.dot(phi, A))
        B = B / norm(np.dot(phi, B))

        while abs(loss0-loss1) > self.tol and iters < 1e3:
            ny = np.dot(Y.T, Y)
            nx = np.dot(X.T, X)
            u = solve(np.dot(Y.T, Y), np.dot(np.dot(Y.T, phi), A) * r_a)
            u = sqrt(N) * u / (sqrt(np.dot(np.dot(u.T, ny), u)))
            v = solve(np.dot(X.T, X), np.dot(np.dot(X.T, phi), B) * r_b)
            v = sqrt(N) * v / (sqrt(np.dot(np.dot(v.T, nx), v)))
            ac_tmp = np.dot(G, B)/T + (lam * 1.0 / N) * r_a * np.dot(np.dot(phi.T, Y), u)
            A = solve(G / T + (lam * 1.0 / N) * r_a ** 2 * H, ac_tmp)
            A = sqrt(T) * A / (norm(np.dot(sqrtm(Gsqrt), A)))
            bc_tmp = np.dot(G, A)/T + (rho * 1.0 / N) * r_b * np.dot(np.dot(phi.T, X), v)
            B = solve(G / T + (rho * 1.0 / N) * r_b ** 2 * H, bc_tmp)
            B = sqrt(T) * B / (norm(np.dot(sqrtm(Gsqrt), B)))
            _tmp_a = np.dot(phi, A)
            _tmp_b = np.dot(phi, B)
            r_a = solve(np.dot(_tmp_a.T, _tmp_a), np.dot(np.dot(_tmp_a.T, Y), u))[0][0]
            r_b = solve(np.dot(_tmp_b.T, _tmp_b), np.dot(np.dot(_tmp_b.T, X), v))[0][0]
            loss0 = loss1
            para['A'], para['B'], para['u'], para['v'] = A, B, u, v
            para['r_a'], para['r_b'] = r_a, r_b
            loss1 = self.loss(para, lam, rho)
            iters += 1
        ac_hat = solve(G / T + (lam * 1.0 / N) * r_a ** 2 * H, lam * 1.0 / N * np.dot(phi.T, r_a))
        para['A_hat'] = np.dot(np.dot(r_a, phi), ac_hat)
        bc_hat = solve(G / T + (rho * 1.0 / N) * r_b ** 2 * H, rho * 1.0 / N * np.dot(phi.T, r_b))
        para['B_hat'] = np.dot(np.dot(r_b, phi), bc_hat)
        return loss1, para

    def stc_multi_seeds(self, lam, rho):
        """
        different initials, select the best
        """
        dic = dict()
        for seed in range(self.n):
            dic[seed] = self.stc_main(lam, rho, seed)
        ind = sorted(range(self.n), key=lambda x: dic[x][0])[0]
        return dic[ind]

    def stc_tuning(self):
        """
        select the best tuning parameters
        """
        dic_gcv = dict()
        dic = dict()
        for lam in self.lam:
            for rho in self.rho:
                dic[(lam, rho)] = self.stc_multi_seeds(lam, rho)
                dic_gcv[(lam, rho)] = self.gcv(dic[(lam, rho)][1])
        ind = sorted(dic.keys(), key=lambda x: dic_gcv[x])[0]
        self.para = dic[ind][1]
        self.tuning = ind

    def gcv(self, para):
        """
        validation creteria
        """
        A, B, u, v, r_a, r_b = para['A'], para['B'], para['u'], para['v'], para['r_a'], para['r_b']
        A_hat = para['A_hat']
        B_hat = para['B_hat']
        #H = self.H
        N = self.N
        phi = self.phi
        Y, X = self.Y, self.X
        gcvy_tmp = (1 - np.sum(np.diag(A_hat)) / N) ** 2
        gcvy = 1.0 / N * norm(np.dot(Y, u) - np.dot(np.dot(r_a, phi), A)) ** 2 / gcvy_tmp
        gcvx_tmp = (1 - np.sum(np.diag(B_hat)) / N) ** 2
        gcvx = 1.0 / N * norm(np.dot(X, v) - np.dot(np.dot(r_b, phi), B)) ** 2 / gcvx_tmp
        return gcvx + gcvy

    def _generate_basis(self):
        """
        generate bspline basis
        """
        nbasis = self.nbasis
        norder = self.norder
        t0, t1 = self.t_interval[0], self.t_interval[-1]
        tmp_list = np.linspace(t0, t1, nbasis - norder + 1).tolist()
        knots = [t0] * norder + tmp_list + [t1] * norder
        spl = bsl(knots, np.eye(nbasis), norder)
        phi = spl(self.t_interval)
        spl = spl(np.linspace(t0, t1, 1000))
        #print self.knots
        return phi, spl

    def _generate_init(self, seed):
        """
        generate random initial
        """
        # A0<-A0/norm(phi%*%A0,'2')
        # B0<-B0/norm(phi%*%B0,'2')
        np.random.seed(seed)
        p, q = self.p, self.q
        nbasis = self.nbasis
        para = {}
        para['u'] = np.random.uniform(size=(p, 1))
        para['v'] = np.random.uniform(size=(q, 1))
        para['A'] = np.random.uniform(size=(nbasis, 1))
        para['B'] = np.random.uniform(size=(nbasis, 1))
        para['r_a'] = 1
        para['r_b'] = 1
        return para

    def compute_final(self):
        """
        generate correlation, f, g for results
        """
        if hasattr(self, 'para'):
            para = self.para
            A, B = para['A'], para['B']
            self.f, self.g = np.dot(self.phi, A), np.dot(self.phi, B)
            self.cor = abs(pearsonr(self.f, self.g)[0])
        else:
            raise Exception('please run the estimation first')

    def compute_metric(self, u_true, v_true, cor_true):
        """
        compute metrics for known truth, especially used in simulation settings
        """
        self.compute_final()
        self.cor_abs = abs(self.cor-cor_true)/cor_true
        self.u_dif = min(cosine(self.para['u'], u_true), 2 - cosine(self.para['u'], u_true))
        self.v_dif = min(cosine(self.para['v'], v_true), 2 - cosine(self.para['v'], v_true))

    def __str__(self):
        """
        print
        """
        return 'cor_abs:{0}, u_cos:{1}, v_cos:{2}, cor:{3}, tuning:{4}'.format(self.cor_abs, \
                self.u_dif, self.v_dif, self.cor, self.tuning)
