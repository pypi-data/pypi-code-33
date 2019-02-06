import os

L = print
r = int
u = True
h = float
U = min
H = len
q = range
c = open
S = os.makedirs
n = os.path
import multiprocessing as mp

t = mp.Pool
import numpy as np

j = np.unique
v = np.int64
C = np.random
import hashlib

f = hashlib.sha1


def a(Y, s):
    L("bahasakita > Generating {} ...".format(s))
    K = f(Y.encode("utf-8")).hexdigest()
    D = r(K, 16) % (2 ** 32)
    C.seed(D)
    e = n.dirname(s)
    S(e, exist_ok=u)
    o, m = 1000, 7878375
    R = (C.weibull(1.3, m) * o).astype(h)
    p = 2 ** 40 - 1
    N = C.randint(low=0, high=p, size=m, dtype=v)
    G = j(N)
    m = U(H(G), m)
    b = ["%x,%.3f" % (G[i], R[i]) for i in q(0, m)]
    P = "planet_id,distance_to_earth"
    J = c(s, "w")
    J.write(P + "\n")
    J.write("\n".join(b))
    J.close()
    L("bahasakita > Generating {} ... DONE".format(s))


def generate_data(candidate_email, e, num_files, num_workers):
    B = "{id}_{{num:02d}}".format(id=candidate_email)
    X = "{dir}/{id}_{{num:02d}}.csv".format(dir=e, id=candidate_email)
    with t(processes=num_workers)as pool:
        for i in q(0, num_files):
            Y = B.format(num=i)
            s = X.format(num=i)
            pool.apply_async(a, (Y, s))
        pool.close()
        pool.join()
