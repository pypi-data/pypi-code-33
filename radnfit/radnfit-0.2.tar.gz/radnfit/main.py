import numpy as np
import scipy.stats as st
from cvxopt import matrix, solvers


solvers.options['show_progress'] = False

from scipy import stats
st.chisqprob = lambda chisq, df: stats.chi2.sf(chisq, df)

def SingleNode(N,T,S,nc,U,P_s,a_s,n,W,i,gamma):
    
    r_s = np.zeros((1,N))
    q_s = np.zeros((1,U.shape[1]))

    ns = len(S[i])
    H = np.zeros((N+1,ns+nc[i]+N))
    H[:N,:nc[i]] = U[:,U[i]>0]
    for h,j in enumerate(S[i]):
        H[j,nc[i]+h] = 1
    H[:N,ns+nc[i]:] = np.identity(N)
    H[N] = np.array([1]*(ns+nc[i])+[0]*N)

    H[i] = 0.

    b = np.concatenate((P_s[i],[1]))

    Hm = np.zeros((2*(ns+nc[i]),ns+nc[i]+N))

    Hm[:ns+nc[i],:ns+nc[i]] = np.identity(ns+nc[i])
    Hm[ns+nc[i]:2*(ns+nc[i]),:ns+nc[i]] = -np.identity(ns+nc[i])

    bm = np.zeros(2*(ns+nc[i]))
    bm[:ns+nc[i]] = 1.

    Xc = np.zeros((ns+nc[i]+N,ns+nc[i]+N))
    Xc[nc[i]+ns:,nc[i]+ns:] = (1.-gamma)*np.identity(N)/2.

    c = np.zeros(ns+nc[i]+N)
    c[nc[i]:nc[i]+ns] = gamma

    indx = np.where(H.sum(axis=1)==0)
    H = np.delete(H,indx,0)

    b = np.delete(b,indx)

    res = np.array(solvers.qp(matrix(Xc),matrix(c),matrix(Hm),matrix(bm),matrix(H),matrix(b))['x']).T[0]

    q_s[0][U[i]>0.] = res[:(nc[i])]
    r_s[0][S[i]]= res[nc[i]:nc[i]+ns]

    M = (U>0).astype(float)
    P_m = np.dot(q_s,1./(n[np.newaxis].T-1)*M.T)+r_s
    W_m = P_m*a_s[i]*T

    W_m[0,i] = 0.

    L = 2.*(np.log(st.poisson.pmf(W[i],W[i])).sum() - np.log(st.poisson.pmf(W[i],W_m)).sum())
    
    return st.chisqprob(L,N-1),q_s,r_s,W[i],W_m[0]
    
    
def Fit_Pattern(W,T,M):
	
	M = M.astype(float)
    N = M.shape[0]
    nc = M.sum(axis=1).astype(int)
    n = M.sum(axis=0)
    U = M/(n-1.)

    R_s = np.zeros((N,N))
    Q_s = np.zeros(M.shape)

    S = [np.where(W[i]>0)[0] for i in range(W.shape[0])]
    a_s = (W.sum(axis=1)/float(T))[np.newaxis].T
    P_s = W/(T*a_s)

    G = []
    for h in range(N):
        f = partial(SingleNode,N,T,S,nc,U,P_s,a_s,n,W,h)

        imin,imax = 0, 1-1e-13
        while True:

            gamma = np.linspace(imin,imax,3)[1]
            out = f(gamma)[0]

            if abs(imin-imax)<1e-10:
                break
            if abs(out-0.05)<0.01:
                break
            if out>0.01:
                imin = gamma
            if out<0.01:
                imax = gamma
        q_s,r_s = f(gamma)[1:3]
        G.append(gamma)

        Q_s[h] = q_s.copy()
        R_s[h] = r_s.copy()
    return Q_s,R_s,G
        
