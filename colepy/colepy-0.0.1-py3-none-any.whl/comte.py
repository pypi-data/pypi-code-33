import numpy as np


def comte(config):
    '''
    :param config:
    x: n x p matrix for feature of training data
    y: n x q matrix for response of training data
    S: d x L matrix for support points. If L = p + 1, then the first p columns are betas and the last column
    is the corresponding residual error estimates. If L = p, then each column of S is a vector of betas
    and argument min_s2 is required. d = q x g where g is the number of groups of support points. Support points
    can be estimated by other methods that solve multivariate linear regression. Eg. GLASSO, RIDGE, OLS, CAMEL.
    min_s2: a positive number corresponds to minimal variance of estimated y, min_s2 is required when there are p
    columns in S.
    tol: tol error tolerance for convergence of EM algorithm. Default value of tol is 1e-6.
    maxit: maxit maximum number of allowable iterations. Default value of maxit is 1e5.
    :return:
    '''

    try:
        x = config['x']
        y = config['y']
        S = config['S']
    except NameError:
        print('Incorrect config file')
        return 'Incorrect config file'

    if 'tol' in config.keys():
        tol = config['tol']
    else:
        tol = 0.1**6

    if 'maxit' in config.keys():
        maxit = config['maxit']
    else:
        maxit = 10**5

    if 'scale' in config.keys():
        scale = config['scale']
    else:
        scale = 1

    if 'cutoff' in config.keys():
        cutoff = config['cutoff']
    else:
        cutoff = 0.1**50

    p = x.shape[1]
    q = y.shape[1]
    ps = S.shape[1]
    mp1 = S.shape[0]
    f = np.ones((mp1, 1))/mp1

    if p == ps:
        try:
            min_s2 = config['min_s2']
            B = S
            ss = min_s2*np.ones((mp1, 1))
            bs = np.concatenate((B,ss), axis=1)
        except FileExistsError:
            print('min_s2 is required')
            return 'min_s2 is required'

    elif p == ps-1:
        B = S[:, 0:p]
        ss = S[:, p].reshape((mp1, 1))
        bs = S
    else:
        print('wrong dimension for x and S')
        return 'wrong dimension for x and S'

    A1 = np.tile(np.sum(y**2, axis=0).reshape(q, 1), (1, mp1))
    A2 = -2 * np.matmul(np.transpose(y), np.matmul(x, np.transpose(B)))
    A3 = np.tile(np.sum(np.matmul(x, np.transpose(B)), axis=0), (q, 1))
    A4 = np.tile(np.transpose(ss), (q, 1))
    A = np.exp(-np.abs((A1 + A2 + A3)/(-2 * A4))) * scale
    A = np.nan_to_num(A) + cutoff

    err = np.inf
    tol_it = 0
    while tol_it < maxit and err > tol:
        tol_it += 1
        oldf = f
        thres = 1/(np.matmul(A, oldf))
        f = np.matmul(np.transpose(A), thres) * oldf / q
        ll = np.sum(np.log(np.matmul(A, f)))
        oldll = np.sum(np.log(np.dot(A, oldf)))
        diff = oldll - ll
        err = np.abs(diff)/np.abs(oldll)

    return {'f': f, 'A': A, 'bs': bs}


def predict_comte(config):
    try:
        x = np.array(config['newx'])
        A = np.array(config['A'])
        bs = np.array(config['bs'])
        f = np.array(config['f'])
    except NameError:
        return 'Incorrect config file'

    n, p = x.shape
    if sum(x[:, 0] == 1) != n:
        p += 1
        x = np.append(np.ones(n).reshape((n, 1)), x, 1)

    q = A.shape[0]
    g = len(f)/q
    mp1 = int(q*g)

    fmat = np.tile(f.reshape(mp1, 1), (1, q))
    numeritor = np.dot((np.dot(x, np.transpose(bs[:, :p]))),
                       np.transpose(A * np.transpose(fmat)))
    denominator = np.transpose(np.tile(1/(np.dot(A, f.reshape(mp1, 1))),
                                       (1, n)))
    yhat = numeritor * denominator
    return {'yhat': yhat}


if __name__ == '__main__':
    n = 100
    p = 10
    q = 20
    x = np.random.normal(5, 10, n * p).reshape((n, p))
    e = np.random.normal(0, 0.01, n * q).reshape((n, q))
    B = np.random.normal(0, 1, p * q)
    B[np.random.choice(range(p * q), int(p * q * 0.8), replace=False)] = 1
    B = B.reshape((p, q))
    y = np.dot(x, B) + e
    S = np.ones((q, (p+1)))
    S[:, 0:p] = np.transpose(B)

    config_train = {
        'x': x,
        'y': y,
        'S': S
    }

    comte_fit = comte(config_train)

    config_test = {
        'newx': x,
        'A': comte_fit['A'],
        'f': comte_fit['f'],
        'bs': comte_fit['bs']
    }

    comte_predict = predict_comte(config_test)
    err = np.linalg.norm(y - comte_predict['yhat'])
    print(err)



