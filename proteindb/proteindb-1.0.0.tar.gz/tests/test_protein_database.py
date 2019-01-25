from pytest_bdd import scenario, given, when, then, scenarios
from proteindb import ProteinDB
from os import path

@given("I have a database populated with data from Fasta file named <filename>.")
def db(filename):

    db = ProteinDB()
    db.populate(path.join('data', filename))
    return db


#####
@scenario('protein_database.feature', "Sequence Search by ID")
def test_search_by_ID():
    pass


@given("<uniprot_id>")
def uniprot_id(uniprot_id):
    return uniprot_id


@when("I search for <uniprot_id> in a database")
def step_impl(db, uniprot_id):
    db.query(uniprot_id=uniprot_id)


@then("I will see the corresponding <sequence>")
def step_impl(db, sequence):
    assert db.result == sequence


#############
@scenario('protein_database.feature', "ID Search by Sequence")
def test_search_by_ID():
    pass

@given("<sequence>")
def sequence(sequence):
    return sequence



@when("I search for the <sequence> in the database")
def step_impl(db, sequence):
    db.query(sequence=sequence)


@then("I will see the corresponding <uniprot_id>")
def step_impl(db, uniprot_id):
    assert db.result == uniprot_id

