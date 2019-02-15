import fastgenomics.external.anndata as fgad
import pytest
import pandas as pd


@pytest.mark.anndata
def test_read(fgprocess):
    adata = fgad.read_data(
        fgprocess, expr="some_input", gene_meta="genes", cell_meta="cells"
    )

    assert (adata.obs.index == ["c1", "c3", "c4", "c2"]).all()
    assert (adata.var.index == [1, 3, 5, 10, 100]).all()
    assert adata.X[1, 0] == 4
    assert adata.shape == (4, 5)
    assert adata.var.shape[1] == 2
    assert adata.obs.shape[1] == 2
    assert "some_column" in adata.var
    assert "some_column" in adata.obs
    assert "batch_id" in adata.obs


@pytest.mark.anndata
def test_read_type_throws(fgprocess):
    with pytest.raises(TypeError):
        fgprocess.input["some_input"].type = "wrong_type"
        fgad.read_data(
            fgprocess, expr="some_input", gene_meta="genes", cell_meta="cells"
        )


@pytest.mark.anndata
def test_read_output_throws(fgprocess):
    with pytest.raises(KeyError):
        fgad.read_data(
            fgprocess, expr="some_output", gene_meta="genes", cell_meta="cells"
        )


@pytest.mark.anndata
def test_write(fgprocess, adata):
    for f in ["count_output", "genes_output", "cells_output"]:
        assert not fgprocess.output[f].path.exists()

    fgad.write_data(
        fgprocess,
        adata,
        expr="count_output",
        gene_meta="genes_output",
        cell_meta="cells_output",
    )

    for f in ["count_output", "genes_output", "cells_output"]:
        assert fgprocess.output[f].path.exists()


@pytest.mark.anndata
def test_read_write(fgprocess, adata):
    fgad.write_data(
        fgprocess,
        adata,
        expr="count_output",
        gene_meta="genes_output",
        cell_meta="cells_output",
    )

    expr_out = pd.read_csv(fgprocess.output["count_output"].path)
    expr_out = expr_out.sort_values(list(expr_out.columns)).reset_index(drop=True)

    genes_out = pd.read_csv(fgprocess.output["genes_output"].path)
    genes_out.set_index("entrez_id", inplace=True)

    cells_out = pd.read_csv(fgprocess.output["cells_output"].path)
    cells_out.set_index("cell_id", inplace=True)

    expr_in = pd.DataFrame(
        dict(
            cell_id=["c1", "c1", "c2", "c3", "c3"],
            entrez_id=[1, 3, 5, 1, 100],
            expression=[1.0, 2.0, 3.0, 4.0, 1.0],
        )
    )
    expr_in = expr_in.sort_values(list(expr_out.columns)).reset_index(drop=True)

    assert expr_out.equals(expr_in)
    assert genes_out.equals(adata.var)
    assert cells_out.equals(adata.obs)
