import pynextgen.utils


def test_simplify_outpath(tmpdir):

    filename = "infile"
    infile = tmpdir.join(filename + ".txt")
    print(infile)

    assert pynextgen.utils.simplify_outpath(infile) == "infile"

    assert pynextgen.utils.simplify_outpath(infile, "prefix_") == "prefix_infile"

    assert (
        pynextgen.utils.simplify_outpath(infile, prefix="prefix_", suffix="_suffix")
        == "prefix_infile_suffix"
    )

    assert (
        pynextgen.utils.simplify_outpath(
            infile, prefix="prefix_", suffix="_suffix", keep_path=True
        )
        == tmpdir.join(f"prefix_{filename}_suffix").strpath
    )
