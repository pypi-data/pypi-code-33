from manhattan.chains import State


def test_state_from_dict():
    """Initialize a state from a dictionary"""
    state = State({'foo': 'bar'})
    assert state == {'foo': 'bar'}

def test_state_from_kwargs():
    """Initalize a state from a set of keyword arguments"""
    state = State(foo='bar')
    assert state == {'foo': 'bar'}

def test_state_assignment():
    """Assign an item to the state using dot-notation"""
    state = State()
    state.foo = 'bar'
    assert state == {'foo': 'bar'}

def test_state_retrieval():
    """Retrieve an item from the state using dot-notation"""
    state = State({'foo': 'bar'})
    assert state.foo == 'bar'

def test_state_deletion():
    """Delete an item from the state using dot-notation"""
    state = State({'foo': 'bar'})
    del state.foo
    assert 'foo' not in state