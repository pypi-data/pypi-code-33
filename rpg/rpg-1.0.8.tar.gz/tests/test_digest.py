"""Tests for digest.py"""
from pathlib import Path
import pytest
from .context import rpg
from rpg import digest
from rpg import enzyme
from rpg import rule
from rpg import core
from sequence import Peptide, Sequence

def test_resultonedigestion():
    """Test class 'ResultOneDigestion'"""
    header = "Test"
    seq = "QWSDESDF"
    enz_name = "fake_enzyme"
    aa_pka = core.AA_PKA_IPC
    pep0 = Peptide(header, seq, enz_name, aa_pka, 0, 3)
    pep1 = Peptide(header, seq, enz_name, aa_pka, 1, 4)
    peptides = [pep0, pep1]
    nb_cleav = 1
    pos_mc = [2, 3]

    # Test function '__repr__()'
    res_dig0 = digest.ResultOneDigestion(enz_name, peptides, nb_cleav, pos_mc)
    assert res_dig0.__repr__() == "Number of cleavage: 1\nNumber of misclea"\
                                  "vage: 2\nPositions of miscleavage: [2, 3"\
                                  "]\nRatio of miscleavage: 66.666666666666"\
                                  "66\nPeptides: [Original header: Test\nNo. "\
                                  "peptide: 0\nEnzyme: fake_enzyme\nCleav. po"\
                                  "s: 3\nPep. size: 8\nPep. mass: 1012.98488"\
                                  "\npKa values from: IPC\nPep. pI: 2.91\nSeq"\
                                  "uence: QWSDESDF\n, Original header: Test\n"\
                                  "No. peptide: 1\nEnzyme: fake_enzyme\nCleav"\
                                  ". pos: 4\nPep. size: 8\nPep. mass: 1012.98"\
                                  "488\npKa values from: IPC\nPep. pI: 2.91\n"\
                                  "Sequence: QWSDESDF\n]\n"

    # Test function '__eq__()'
    res_dig1 = digest.ResultOneDigestion(enz_name, peptides, nb_cleav, pos_mc)
    assert res_dig0 == res_dig1

    # Test function '__ne__()'
    res_dig2 = digest.ResultOneDigestion(enz_name+"a", peptides, nb_cleav,
                                         pos_mc)
    tmp_pep = peptides[:]
    tmp_pep.pop()
    res_dig3 = digest.ResultOneDigestion(enz_name, tmp_pep, nb_cleav, pos_mc)
    res_dig4 = digest.ResultOneDigestion(enz_name, peptides, nb_cleav-1, pos_mc)
    tmpos_mc = pos_mc[:]
    tmpos_mc.append(4)
    res_dig5 = digest.ResultOneDigestion(enz_name, peptides, nb_cleav, tmpos_mc)
    assert res_dig0 != res_dig2
    assert res_dig0 != res_dig3
    assert res_dig0 != res_dig4
    assert res_dig0 != res_dig5

    # Test function '__format__()'
    format_res = res_dig0.__format__("csv")
    assert format_res == "Test,0,fake_enzyme,3,8,1012.98488,2.91,QWSDESDF\nTe"\
                         "st,1,fake_enzyme,4,8,1012.98488,2.91,QWSDESDF\n"
    format_res = res_dig0.__format__("tsv")
    assert format_res == "Test\t0\tfake_enzyme\t3\t8\t1012.98488\t2.91\tQWSDE"\
                         "SDF\nTest\t1\tfake_enzyme\t4\t8\t1012.98488\t2.91\t"\
                         "QWSDESDF\n"
    format_res = res_dig0.__format__("fasta")
    assert format_res == ">Test_0_fake_enzyme_3_8_1012.98488_2.91\nQWSDESDF\n"\
                         ">Test_1_fake_enzyme_4_8_1012.98488_2.91\nQWSDESDF\n"

    # Test function 'pop_peptides()'
    assert res_dig5.peptides != []
    res_dig5.pop_peptides()
    assert res_dig5.peptides == []

    # Test function 'add_peptide()'
    res_dig5.add_peptide(pep0)
    assert res_dig5.peptides != []

    # Test function 'inc_nb_cleavage()'
    assert res_dig5.nb_cleavage == 1
    res_dig5.inc_nb_cleavage()
    res_dig5.inc_nb_cleavage()
    res_dig5.inc_nb_cleavage()
    assert res_dig5.nb_cleavage == 4

    # Test function 'get_nb_miscleavage()'
    assert res_dig5.get_nb_miscleavage() == 3

    # Test function 'add_miscleavage()'
    res_dig5.add_miscleavage(6)
    assert res_dig5.get_nb_miscleavage() == 4

    # Test function 'get_ratio_miscleavage()'
    assert res_dig5.get_ratio_miscleavage() == 50.0

    # Test function 'get_miscleavage_pos()'
    assert res_dig5.get_miscleavage_pos() == "2, 3, 4, 6"

    # Test function 'get_cleavage_pos()'
    res_dig5.add_peptide(pep1)
    # Looks strange because of previous 'inc_nb_cleavage()'
    assert res_dig5.get_cleavage_pos() == "3"

    # Test function 'merge()'
    # Change peptides name of merged one
    for i in res_dig1.peptides:
        i.enzyme_name = "zbla"
    for i in res_dig1.peptides:
        assert i.enzyme_name == "zbla"
    assert len(res_dig5.peptides) == 2
    res_dig5.merge(res_dig1)
    for i in res_dig5.peptides:
        assert i.enzyme_name == "fake_enzyme"
    assert len(res_dig5.peptides) == 4
    assert res_dig5.nb_cleavage == 5
    assert res_dig5.pos_miscleavage == [2, 3, 4, 6, 2, 3]

    # Test function 'get_more_info()'
    assert res_dig5.get_more_info() == "\nNumber of cleavage: 5\nCleavage pos"\
                                       "ition: 3, 4, 3\nNumber of miscleava"\
                                       "ge: 6\nmiscleavage position: 2, 3, "\
                                       "4, 6, 2, 3\nmiscleavage ratio: "\
                                       "54.55%\nSmallest peptide size: 8\nN t"\
                                       "erminal peptide: QWSDESDF\nC terminal"\
                                       " peptide: QWSDESDF"

def test_one_digest():
    """Test function 'one_digest(pep, enz)'"""
    # Cut after S not precedeed by D
    rule_dict = {}
    rule_txt = "(S,)"
    rule_dict[rule_txt] = True
    rule_exc = "(D)(S,)"
    rule_dict[rule_exc] = False
    all_rules = rule.create_rules(rule_dict)
    enz = enzyme.Enzyme(-1, "fake_enzyme", all_rules)
    aa_pka = core.AA_PKA_IPC
    # Input sequence
    pep = Peptide("Test", "WASD", enz.name, aa_pka)
    # Results, two peptides: 'WAS' and 'D'
    res_pep0 = Peptide("Test", "WAS", enz.name, aa_pka, 0, 3)
    res_pep1 = Peptide("Test", "D", enz.name, aa_pka, 1, 4)
    # Test it!
    res = digest.one_digest(pep, enz, aa_pka)
    assert res.enzyme_name == "fake_enzyme"
    assert res.peptides[0].__repr__() == res_pep0.__repr__()
    assert res.peptides[1].__repr__() == res_pep1.__repr__()

    # Input sequence
    pep = Peptide("Test", "WADSD", enz.name, aa_pka)
    # Results, no cut
    res_pep1 = Peptide("Test", "WADSD", enz.name, aa_pka, 0, 0)
    # Test it!
    res = digest.one_digest(pep, enz, aa_pka)
    assert res.enzyme_name == "fake_enzyme"
    assert res.peptides[0].__repr__() == res_pep1.__repr__()

    # Cut before S precedeed by D
    rule_dict = {}
    rule_txt = "(D)(,S)"
    rule_dict[rule_txt] = True
    all_rules = rule.create_rules(rule_dict)
    enz = enzyme.Enzyme(-1, "fake_enzyme", all_rules)
    # Input sequence
    pep = Peptide("Test", "WADS", enz.name, aa_pka)
    # Results, two peptides: 'WAS' and 'D'
    res_pep0 = Peptide("Test", "WAD", enz.name, aa_pka, 0, 3)
    res_pep1 = Peptide("Test", "S", enz.name, aa_pka, 1, 4)
    # Test it!
    res = digest.one_digest(pep, enz, aa_pka)
    assert res.enzyme_name == "fake_enzyme"
    assert res.peptides[0].__repr__() == res_pep0.__repr__()
    assert res.peptides[1].__repr__() == res_pep1.__repr__()

def test_digest_one_sequence():
    """Test function 'def digest_one_sequence(seq, enz, mode)'"""
    enzymes = []
    # First enzyme: cut after D not precedeed by S
    rule_dict = {}
    rule_txt = "(D,)"
    rule_dict[rule_txt] = True
    exc_txt = "(S)(D,)"
    rule_dict[exc_txt] = False
    all_rules = rule.create_rules(rule_dict)
    enz1 = enzyme.Enzyme(-1, "fake_enzyme1", all_rules)
    enzymes.append(enz1)
    aa_pka = core.AA_PKA_IPC

    # Second enzyme: cut after S
    rule_dict = {}
    rule_txt = "(S,)"
    rule_dict[rule_txt] = True
    all_rules = rule.create_rules(rule_dict)
    enz2 = enzyme.Enzyme(-1, "fake_enzyme2", all_rules)
    enzymes.append(enz2)

    # Input sequence
    seq = Sequence("Test", "WASDESDF")

    # Sequential, only one enzyme will cut
    mode = "sequential"
    # Enz1 will not cut
    res_pep0 = Peptide("Test", "WASDESDF", enzymes[0].name, aa_pka, 0, 0)
    # Enz2 will cut, three peptides: 'WAS', 'DES' and 'DF'
    res_pep1 = Peptide("Test", "WAS", enzymes[1].name, aa_pka, 0, 3)
    res_pep2 = Peptide("Test", "DES", enzymes[1].name, aa_pka, 1, 6)
    res_pep3 = Peptide("Test", "DF", enzymes[1].name, aa_pka, 2, 8)
    # Test it!
    res = digest.digest_one_sequence(seq, enzymes, mode, aa_pka)
    assert res[0].enzyme_name == "fake_enzyme1"
    assert res[0].peptides[0].__repr__() == res_pep0.__repr__()
    assert res[1].enzyme_name == "fake_enzyme2"
    assert res[1].peptides[0].__repr__() == res_pep1.__repr__()
    assert res[1].peptides[1].__repr__() == res_pep2.__repr__()
    assert res[1].peptides[2].__repr__() == res_pep3.__repr__()

    # Concurrent, both enzymes will cut
    mode = "concurrent"
    enzs_name = enzymes[0].name + "-" + enzymes[1].name
    # Results, five peptides: 'WAS', 'D', ES', 'D', and 'F'
    res_pep0 = Peptide("Test", "WAS", enzs_name, aa_pka, 0, 3)
    res_pep1 = Peptide("Test", "D", enzs_name, aa_pka, 1, 4)
    res_pep2 = Peptide("Test", "ES", enzs_name, aa_pka, 2, 6)
    res_pep3 = Peptide("Test", "D", enzs_name, aa_pka, 3, 7)
    res_pep4 = Peptide("Test", "F", enzs_name, aa_pka, 4, 8)
    # Test it!
    res = digest.digest_one_sequence(seq, enzymes, mode, aa_pka)
    assert res[0].enzyme_name == enzs_name
    assert res[0].peptides[0].__repr__() == res_pep0.__repr__()
    assert res[0].peptides[1].__repr__() == res_pep1.__repr__()
    assert res[0].peptides[2].__repr__() == res_pep2.__repr__()
    assert res[0].peptides[3].__repr__() == res_pep3.__repr__()
    assert res[0].peptides[4].__repr__() == res_pep4.__repr__()

    # Error, so sequential, only one enzyme will cut
    mode = "pwet"
    # Enz1 will not cut
    res_pep0 = Peptide("Test", "WASDESDF", enzymes[0].name, aa_pka, 0, 0)
    # Enz2 will cut, three peptides: 'WAS', 'DES' and 'DF'
    res_pep1 = Peptide("Test", "WAS", enzymes[1].name, aa_pka, 0, 3)
    res_pep2 = Peptide("Test", "DES", enzymes[1].name, aa_pka, 1, 6)
    res_pep3 = Peptide("Test", "DF", enzymes[1].name, aa_pka, 2, 8)
    # Test it!
    res = digest.digest_one_sequence(seq, enzymes, mode, aa_pka)
    assert res[0].enzyme_name == "fake_enzyme1"
    assert res[0].peptides[0].__repr__() == res_pep0.__repr__()
    assert res[1].enzyme_name == "fake_enzyme2"
    assert res[1].peptides[0].__repr__() == res_pep1.__repr__()
    assert res[1].peptides[1].__repr__() == res_pep2.__repr__()
    assert res[1].peptides[2].__repr__() == res_pep3.__repr__()

def test_sequential_digest():
    """Test function 'sequential_digest(seq, enz)'"""
    enzymes = []
    # Firt enzyme: cut after D precedeed by S
    rule_dict = {}
    rule_txt = "(S)(D,)"
    rule_dict[rule_txt] = True
    all_rules = rule.create_rules(rule_dict)
    enz1 = enzyme.Enzyme(-1, "fake_enzyme1", all_rules)
    enzymes.append(enz1)
    aa_pka = core.AA_PKA_IPC

    # Second enzyme: cut after S
    rule_dict = {}
    rule_txt = "(S,)"
    rule_dict[rule_txt] = True
    all_rules = rule.create_rules(rule_dict)
    enz2 = enzyme.Enzyme(-1, "fake_enzyme2", all_rules)
    enzymes.append(enz2)

    # Input sequence
    seq = Sequence("Test", "WASDESDF")

    # Enz1 will cut
    res_pep0 = Peptide("Test", "WASD", enzymes[0].name, aa_pka, 0, 4)
    res_pep1 = Peptide("Test", "ESD", enzymes[0].name, aa_pka, 1, 7)
    res_pep2 = Peptide("Test", "F", enzymes[0].name, aa_pka, 2, 8)
    # Enz2 will cut, three peptides: 'WAS', 'DES' and 'DF'
    res_pep3 = Peptide("Test", "WAS", enzymes[1].name, aa_pka, 0, 3)
    res_pep4 = Peptide("Test", "DES", enzymes[1].name, aa_pka, 1, 6)
    res_pep5 = Peptide("Test", "DF", enzymes[1].name, aa_pka, 2, 8)
    # Test it!
    res = digest.sequential_digest(seq, enzymes, aa_pka)
    assert res[0].enzyme_name == "fake_enzyme1"
    assert res[0].peptides[0].__repr__() == res_pep0.__repr__()
    assert res[0].peptides[1].__repr__() == res_pep1.__repr__()
    assert res[0].peptides[2].__repr__() == res_pep2.__repr__()
    assert res[1].enzyme_name == "fake_enzyme2"
    assert res[1].peptides[0].__repr__() == res_pep3.__repr__()
    assert res[1].peptides[1].__repr__() == res_pep4.__repr__()
    assert res[1].peptides[2].__repr__() == res_pep5.__repr__()

def test_concurrent_digest():
    """Test function 'concurrent_digest(seq, enz):'"""
    enzymes = []
    # Firt enzyme: cut after D precedeed by S
    rule_dict = {}
    rule_txt = "(S)(D,)"
    rule_dict[rule_txt] = True
    all_rules = rule.create_rules(rule_dict)
    enz1 = enzyme.Enzyme(-1, "fake_enzyme1", all_rules)
    enzymes.append(enz1)
    aa_pka = core.AA_PKA_S

    # Second enzyme: cut after S
    rule_dict = {}
    rule_txt = "(S,)"
    rule_dict[rule_txt] = True
    all_rules = rule.create_rules(rule_dict)
    enz2 = enzyme.Enzyme(-1, "fake_enzyme2", all_rules)
    enzymes.append(enz2)

    # Input sequence
    seq = Sequence("Test", "WASDESDF")
    enzs_name = enzymes[0].name + "-" + enzymes[1].name
    # Results
    res_pep0 = Peptide("Test", "WAS", enzs_name, aa_pka, 0, 3)
    res_pep1 = Peptide("Test", "D", enzs_name, aa_pka, 1, 4)
    res_pep2 = Peptide("Test", "ES", enzs_name, aa_pka, 2, 6)
    res_pep3 = Peptide("Test", "D", enzs_name, aa_pka, 3, 7)
    res_pep4 = Peptide("Test", "F", enzs_name, aa_pka, 4, 8)

    # Test it!
    res = digest.concurrent_digest(seq, enzymes, aa_pka)
    assert res[0].enzyme_name == enzs_name
    assert res[0].peptides[0].__repr__() == res_pep0.__repr__()
    assert res[0].peptides[1].__repr__() == res_pep1.__repr__()
    assert res[0].peptides[2].__repr__() == res_pep2.__repr__()
    assert res[0].peptides[3].__repr__() == res_pep3.__repr__()
    assert res[0].peptides[4].__repr__() == res_pep4.__repr__()

def test_digest_from_input(capsys, tmpdir):
    """ Test function 'digest_from_input(input_data, enzymes, mode)'"""
    rule_dict = {}
    rule_txt = "(S)(D,)"
    rule_dict[rule_txt] = True
    all_rules = rule.create_rules(rule_dict)
    enz1 = enzyme.Enzyme(-1, "fake_enzyme1", all_rules)
    enzymes = [enz1]
    mode = "sequential"
    aa_pka = core.AA_PKA_IPC

    # Test wrong file
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        digest.digest_from_input(str(Path.home()) + "/rpg_user.py",
                                 enzymes, mode, aa_pka)
    _, err = capsys.readouterr()
    assert err == "Input Error: input file format not recognized (f).\n"
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 1

    # Test input data
    seq = "WQSDESDFZQSDESDF"
    res = digest.digest_from_input(seq, enzymes, mode, aa_pka)
    assert res[0][0].__repr__() == "Number of cleavage: 4\nNumber of miscle"\
                                   "avage: 0\nPositions of miscleavage: []"\
                                   "\nRatio of miscleavage: 0.0\nPeptides: "\
                                   "[Original header: Input\nNo. peptide: 0"\
                                   "\nEnzyme: fake_enzyme1\nCleav. pos: 4\nPe"\
                                   "p. size: 4\nPep. mass: 534.52598\npKa val"\
                                   "ues from: IPC\nPep. pI: 3.14\nSequence: W"\
                                   "QSD\n, Original header: Input\nNo. peptid"\
                                   "e: 1\nEnzyme: fake_enzyme1\nCleav. pos: 7"\
                                   "\nPep. size: 3\nPep. mass: 349.29758\npKa"\
                                   " values from: IPC\nPep. pI: 3.04\nSequenc"\
                                   "e: ESD\n, Original header: Input\nNo. pep"\
                                   "tide: 2\nEnzyme: fake_enzyme1\nCleav. pos"\
                                   ": 12\nPep. size: 5\nPep. mass: 495.48938"\
                                   "\npKa values from: IPC\nPep. pI: 3.14\nSe"\
                                   "quence: FZQSD\n, Original header: Input\n"\
                                   "No. peptide: 3\nEnzyme: fake_enzyme1\nCle"\
                                   "av. pos: 15\nPep. size: 3\nPep. mass: 349"\
                                   ".29758\npKa values from: IPC\nPep. pI: 3."\
                                   "04\nSequence: ESD\n, Original header: Inp"\
                                   "ut\nNo. peptide: 4\nEnzyme: fake_enzyme1"\
                                   "\nCleav. pos: 16\nPep. size: 1\nPep. mass"\
                                   ": 165.19188\npKa values from: IPC\nPep. p"\
                                   "I: 5.97\nSequence: F\n]\n"

    # Test fasta file
    fasta_file = tmpdir.join("test.fasta")
    fasta_file.write(">Fake1\nWQSDESDFZQS\nDESDF\n>Fake2\nNPHARDORCOMPLET")
    res = digest.digest_from_input(str(fasta_file), enzymes, mode, aa_pka)
    assert res[0][0].__repr__() == "Number of cleavage: 4\nNumber of miscle"\
                                   "avage: 0\nPositions of miscleavage: []"\
                                   "\nRatio of miscleavage: 0.0\nPeptides: "\
                                   "[Original header: Fake1\nNo. peptide: 0\n"\
                                   "Enzyme: fake_enzyme1\nCleav. pos: 4\nPep."\
                                   " size: 4\nPep. mass: 534.52598\npKa value"\
                                   "s from: IPC\nPep. pI: 3.14\nSequence: WQS"\
                                   "D\n, Original header: Fake1\nNo. peptide:"\
                                   " 1\nEnzyme: fake_enzyme1\nCleav. pos: 7\n"\
                                   "Pep. size: 3\nPep. mass: 349.29758\npKa v"\
                                   "alues from: IPC\nPep. pI: 3.04\nSequence:"\
                                   " ESD\n, Original header: Fake1\nNo. pepti"\
                                   "de: 2\nEnzyme: fake_enzyme1\nCleav. pos: "\
                                   "12\nPep. size: 5\nPep. mass: 495.48938\np"\
                                   "Ka values from: IPC\nPep. pI: 3.14\nSeque"\
                                   "nce: FZQSD\n, Original header: Fake1\nNo."\
                                   " peptide: 3\nEnzyme: fake_enzyme1\nCleav."\
                                   " pos: 15\nPep. size: 3\nPep. mass: 349.29"\
                                   "758\npKa values from: IPC\nPep. pI: 3.04"\
                                   "\nSequence: ESD\n, Original header: Fake1"\
                                   "\nNo. peptide: 4\nEnzyme: fake_enzyme1\nC"\
                                   "leav. pos: 16\nPep. size: 1\nPep. mass: 1"\
                                   "65.19188\npKa values from: IPC\nPep. pI: "\
                                   "5.97\nSequence: F\n]\n"
    assert res[1][0].__repr__() == "Number of cleavage: 0\nNumber of miscleav"\
                                   "age: 0\nPositions of miscleavage: []\nRat"\
                                   "io of miscleavage: 0\nPeptides: [Original"\
                                   " header: Fake2\nNo. peptide: 0\nEnzyme: f"\
                                   "ake_enzyme1\nCleav. pos: 0\nPep. size: 15"\
                                   "\nPep. mass: 2014.35098\npKa values from:"\
                                   " IPC\nPep. pI: 7.16\nSequence: NPHARDORCO"\
                                   "MPLET\n]\n"

    # Test fastq file (same result)
    fastq_file = tmpdir.join("test.fastq")
    fastq_file.write("@Fake1\nWQSDESDFZQSDESDF\n+Fake1\nnWQSDESDFZQSDESDF\n@Fa"\
                     "ke2\nNPHARDORCOMPLET\n+Fake2\nnNPHARDORCOMPLET\n")
    res = digest.digest_from_input(str(fastq_file), enzymes, mode, aa_pka)
    assert res[0][0].__repr__() == "Number of cleavage: 4\nNumber of miscle"\
                                   "avage: 0\nPositions of miscleavage: []"\
                                   "\nRatio of miscleavage: 0.0\nPeptides: "\
                                   "[Original header: Fake1\nNo. peptide: 0\n"\
                                   "Enzyme: fake_enzyme1\nCleav. pos: 4\nPep."\
                                   " size: 4\nPep. mass: 534.52598\npKa value"\
                                   "s from: IPC\nPep. pI: 3.14\nSequence: WQS"\
                                   "D\n, Original header: Fake1\nNo. peptide:"\
                                   " 1\nEnzyme: fake_enzyme1\nCleav. pos: 7\n"\
                                   "Pep. size: 3\nPep. mass: 349.29758\npKa v"\
                                   "alues from: IPC\nPep. pI: 3.04\nSequence:"\
                                   " ESD\n, Original header: Fake1\nNo. pepti"\
                                   "de: 2\nEnzyme: fake_enzyme1\nCleav. pos: "\
                                   "12\nPep. size: 5\nPep. mass: 495.48938\np"\
                                   "Ka values from: IPC\nPep. pI: 3.14\nSeque"\
                                   "nce: FZQSD\n, Original header: Fake1\nNo."\
                                   " peptide: 3\nEnzyme: fake_enzyme1\nCleav."\
                                   " pos: 15\nPep. size: 3\nPep. mass: 349.29"\
                                   "758\npKa values from: IPC\nPep. pI: 3.04"\
                                   "\nSequence: ESD\n, Original header: Fake1"\
                                   "\nNo. peptide: 4\nEnzyme: fake_enzyme1\nC"\
                                   "leav. pos: 16\nPep. size: 1\nPep. mass: 1"\
                                   "65.19188\npKa values from: IPC\nPep. pI: "\
                                   "5.97\nSequence: F\n]\n"
    assert res[1][0].__repr__() == "Number of cleavage: 0\nNumber of miscle"\
                                   "avage: 0\nPositions of miscleavage: []"\
                                   "\nRatio of miscleavage: 0\nPeptides: [O"\
                                   "riginal header: Fake2\nNo. peptide: 0\nEn"\
                                   "zyme: fake_enzyme1\nCleav. pos: 0\nPep. s"\
                                   "ize: 15\nPep. mass: 2014.35098\npKa value"\
                                   "s from: IPC\nPep. pI: 7.16\nSequence: NPH"\
                                   "ARDORCOMPLET\n]\n"
