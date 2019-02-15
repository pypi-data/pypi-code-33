try:
    import pandas as pd
    import numpy as np
    import scipy.sparse as sp
    from anndata import AnnData
except ImportError as e:
    msg = f"Could not import some of the necessary modules ({e.name}).  Please make sure to install anndata (https://github.com/theislab/anndata) with all its dependencies correctly (e.g. pandas, numpy, scipy)."
    raise ImportError(msg, name=e.name, path=e.path)
    raise e


def get_path(file, content_type):
    """Returns a path if the file is of requested FASTGenomics type,
otherwise throws a TypeError."""
    if file is None:
        return None
    if file.type != content_type:
        raise TypeError(
            f'File "{file.name}" is of type "{file.type}" but expected "{content_type}".'
        )
    return file.path


def read_data(
    fgprocess,
    expr="expression_matrix",
    cell_meta="cell_metadata",
    gene_meta="gene_metadata",
):
    """Reads an anndata object by composing three files together:
`expression_matrix`, `cell_metadata` and `gene_metadata`."""
    expr_path = get_path(fgprocess.input[expr], content_type="expression_matrix")
    expr = pd.read_csv(expr_path)

    obs = read_cell_metadata(fgprocess, cell_meta, expr)
    var = read_gene_metadata(fgprocess, gene_meta, expr)

    counts = read_sparse_matrix(expr, obs, var)

    adata = AnnData(counts, obs=obs, var=var, dtype="float64")
    return adata


def read_cell_metadata(fgprocess, cell_meta, expr):
    if cell_meta is None:
        cell_path = None
    else:
        cell_path = get_path(fgprocess.input[cell_meta], content_type="cell_metadata")

    expr_cell_id = expr.cell_id.unique()

    if cell_path is None:
        df = pd.DataFrame(expr_cell_id, columns=["cell_id"]).set_index("cell_id")
    else:
        df = pd.read_csv(cell_path, index_col="cell_id")
        if set(expr_cell_id) - set(df.index):
            raise Exception(
                f'Some cell_id\'s were present in the expression matrix but not in "{cell_meta}".'
            )
    return df


def read_gene_metadata(fgprocess, gene_meta, expr):
    gene_path = get_path(fgprocess.input[gene_meta], content_type="gene_metadata")

    expr_entrez_id = expr.entrez_id.unique()

    if gene_path is None:
        df = pd.DataFrame(expr_entrez_id, columns=["entrez_id"]).set_index("entrez_id")
    else:
        df = pd.read_csv(gene_path, index_col="entrez_id")
        if set(expr_entrez_id) - set(df.index):
            raise Exception(
                f'Some entrez_id\'s were present in the expression matrix but not in "{gene_meta}".'
            )
    return df


def read_sparse_matrix(expr, obs, var):
    cell_idx = pd.DataFrame(
        dict(cell_id=obs.index, cell_idx=np.arange(obs.shape[0]))
    ).set_index("cell_id")
    entrez_idx = pd.DataFrame(
        dict(entrez_id=var.index, entrez_idx=np.arange(var.shape[0]))
    ).set_index("entrez_id")
    expr = expr.merge(cell_idx, on="cell_id", copy=False)
    expr = expr.merge(entrez_idx, on="entrez_id", copy=False)

    counts = sp.coo_matrix(
        (expr.expression, (expr.cell_idx, expr.entrez_idx)),
        shape=(obs.shape[0], var.shape[0]),
    ).tocsr()

    return counts


# Writing
def write_exprs_csv(adata, csv_file):
    mat = adata.X.tocoo()
    df = pd.DataFrame.from_dict(
        dict(cell_id=mat.row, entrez_id=mat.col, expression=mat.data)
    )
    df.to_csv(csv_file)


def write_data(fgprocess, adata, expr=None, cell_meta=None, gene_meta=None):
    if expr is not None:
        exprs_path = get_path(fgprocess.output[expr], content_type="expression_matrix")
        write_exprs_csv(adata, exprs_path)
    if cell_meta is not None:
        cell_path = get_path(fgprocess.output[cell_meta], content_type="cell_metadata")
        adata.obs.to_csv(cell_path)
    if gene_meta is not None:
        gene_path = get_path(fgprocess.output[gene_meta], content_type="gene_metadata")
        adata.var.to_csv(gene_path)
