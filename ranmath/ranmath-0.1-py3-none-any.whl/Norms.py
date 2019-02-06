

def frobenius_norm_squared(matrix):
    return (matrix @ matrix.T).trace() / matrix.shape[0]


def frobenius_eigenvalues_distance(eigvalues_array_1, eigvalues_array_2):
    return ((eigvalues_array_1 - eigvalues_array_2) ** 2).mean()