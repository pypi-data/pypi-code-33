from pynextgen.basics_fasta import Fasta

# TO FIX: Testing is working now from PynextGen folder, not sure it
# will work from other folder (check paths)

fasta_file = "test/test_data/fasta1.fas"

fasta = Fasta(fasta_file)
fasta_dict = fasta.to_dict()
fasta_dict_full = fasta.to_dict(simple_ID=False)

fasta_gen = Fasta(fasta_file).parse()


def test_fasta_to_dict():

    assert len(fasta_dict) == 2

    assert fasta_dict["seq2"] == "CGATCTGAGCTACGATCGTAGCTCGATGCATCTGTAGCTGTAG"

    assert "seq1 chromosome chromosome" in fasta_dict_full


def test_fasta_to_generator():

    fasta_len = sum(1 for x in fasta_gen)
    assert fasta_len == 2


def test_fasta_filter():

    fasta_filtered = fasta.filter(".*chromosome chromosome.*")
    fasta_filtered_len = sum(1 for x in fasta_filtered.parse())

    assert fasta_filtered_len == 1

    assert "seq1 chromosome chromosome" in fasta_filtered.to_dict(simple_ID=False)
