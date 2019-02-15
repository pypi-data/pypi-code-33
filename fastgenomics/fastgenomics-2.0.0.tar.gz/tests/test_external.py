import fastgenomics.external.anndata as fgad
import pytest


@pytest.mark.anndata
def test_read(fgprocess):
    adata = fgad.read_data(
        fgprocess, expr="some_input", gene_meta="genes", cell_meta="cells"
    )

    assert adata.X[2, 3] == 4
    assert adata.shape == (3, 4)
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
