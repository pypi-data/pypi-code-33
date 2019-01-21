import numpy as np


def get_d_dict():
# d for MDA and MDO
    return {'twist': [1.0, 37.081, 0.40, 58314.726368],
            'Fo1': [1.0],
            'Fo2': [1.0, 1.0],
            'Fo3': [1.0],
            'sigma[1]': [0.05, 58314.726368, 1.0, 37.081, 0.40],
            'sigma[2]': [0.05, 58314.726368, 1.0, 37.081, 0.40],
            'sigma[3]': [0.05, 58314.726368, 1.0, 37.081, 0.40],
            'sigma[4]': [0.05, 58314.726368, 1.0, 37.081, 0.40],
            'sigma[5]': [0.05, 58314.726368, 1.0, 37.081, 0.40],
            'dpdx': [0.05],
            'Temp': [1.6, 45000.0, 0.5]}

def polynomial_function(S_new, flag, S_bound, var, deriv=False):

    R = [[0.2736, 0.3970, 0.8152, 0.9230, 0.1108],
         [0.4252, 0.4415, 0.6357, 0.7435, 0.1138],
         [0.0329, 0.8856, 0.8390, 0.3657, 0.0019],
         [0.0878, 0.7248, 0.1978, 0.0200, 0.0169],
         [0.8955, 0.4568, 0.8075, 0.9239, 0.2525]]

    d = get_d_dict()

    if len(S_new) > 1:
        res = np.array([])
        S_new = np.append(res, S_new)

    if var not in d:
        raise AssertionError('Variable (var) {} is missing in the dictionary d.'.format(var))

    S = d[var]
    S_norm = []
    S_shifted = []
    Ai = []
    Aij = [[0.0]*len(S_new) for i in range(len(S_new))]

    assert len(S) == len(S_new)

    for i in range(len(S)):
        S_norm.append(S_new[i] / S[i])

        if S_norm[i] > 1.25:
            S_norm[i] = 1.25
        elif S_norm[i] < 0.75:
            S_norm[i] = 0.75

        S_shifted.append(S_norm[i]-1)

        a = 0.1
        b = a

        if flag[i] == 3:
            a = -a
            b = a
        elif flag[i] == 2:
            b = 2*a
        elif flag[i] == 4:
            a = -a
            b = 2*a

        So = 0.0
        Sl = So - S_bound[i]
        Su = So + S_bound[i]
        Mtx_shifted = np.array([[1.0, Sl, Sl**2],
                                [1.0, So, So**2],
                                [1.0, Su, Su**2]])

        if flag[i] == 5:
            F_bound = np.array([[1+(0.5*a)**2], [1.0], [1+(0.5*b)**2]])
        else:
            F_bound = np.array([[1-(0.5*a)], [1.0], [1+(0.5*b)]])

        A = np.linalg.solve(Mtx_shifted, F_bound)

        Ao = A[0]
        B = A[1]

        if var == "Fo1":
            Ai.append(B)
        else:
            Ai.append(A[1])

        Aij[i][i] = A[2]

    for i in range(len(S)):
        for j in range(i+1, len(S)):
            Aij[i][j] = Aij[i][i] * R[i][j]
            Aij[j][i] = Aij[i][j]

    Ai = np.matrix(np.array(Ai))
    Aij = np.matrix(np.array(Aij))
    S_shifted = np.matrix(np.array(S_shifted))

    if deriv:
        return S_shifted, Ai, Aij
    else:
        return float((Ao + Ai.T * S_shifted.T + 0.5 * S_shifted * Aij * S_shifted.T)[0])
