from flask import Flask

from manhattan.chains import Chain, ChainMgr


def test_init():
    """Initialize a chain manager"""
    chains = ChainMgr()

    # Initially the chain manager should have no assigned chains
    assert chains.chains == {}

def test_assign_chain():
    """Assign a chain to the chain manager"""
    chains = ChainMgr()

    my_chain = Chain(['foo', 'bar'])
    chains['my_chain'] = my_chain

    assert chains['my_chain'] is my_chain

def test_chains_property():
    """Get a map of chains for the chain manager using the chains property"""
    chains = ChainMgr()

    my_chain_a = Chain(['foo', 'bar'])
    my_chain_b = Chain(['zee', 'omm'])
    chains['my_chain_a'] = my_chain_a
    chains['my_chain_b'] = my_chain_b

    assert chains.chains == {'my_chain_a': my_chain_a, 'my_chain_b': my_chain_b}

def test_copy():
    """Copy the chain manager"""
    chains = ChainMgr()

    my_chain_a = Chain(['foo', 'bar'])
    my_chain_b = Chain(['zee', 'omm'])
    chains['my_chain_a'] = my_chain_a
    chains['my_chain_b'] = my_chain_b

    chains_copy = chains.copy()

    # Check the chain manager is the same
    assert chains.chains == chains.chains

    # Check the chain is a copy
    assert chains_copy is not chains
    assert chains_copy._chains is not chains._chains

def test_retrieve_chain():
    """Retreive a chain from the chain manager by name"""
    chains = ChainMgr()

    my_chain = Chain(['foo', 'bar'])
    chains['my_chain'] = my_chain

    assert chains['my_chain'] is my_chain

def test_delete_chain():
    """Delete a chain from the chain manager by name"""
    chains = ChainMgr()

    my_chain = Chain(['foo', 'bar'])
    chains['my_chain'] = my_chain
    del chains['my_chain']

    assert 'my_chain' not in chains

def test_insert_link():
    """Insert a link into every chain"""

    chains = ChainMgr()

    my_chain_a = Chain(['foo', 'bar'])
    my_chain_b = Chain(['zee', 'bar'])
    chains['my_chain_a'] = my_chain_a
    chains['my_chain_b'] = my_chain_b

    chains.insert_link('bar', 'omm', after=True)

    assert chains['my_chain_a'].links == ['foo', 'bar', 'omm']
    assert chains['my_chain_b'].links == ['zee', 'bar', 'omm']

def test_remove_link():
    """Remove a link from every chain"""

    chains = ChainMgr()

    my_chain_a = Chain(['foo', 'bar'])
    my_chain_b = Chain(['zee', 'bar'])
    chains['my_chain_a'] = my_chain_a
    chains['my_chain_b'] = my_chain_b

    chains.remove_link('bar')

    assert chains['my_chain_a'].links == ['foo']
    assert chains['my_chain_b'].links == ['zee']

def test_set_final():
    """Set a final function across one or more chains in the chain manager"""
    chains = ChainMgr()

    chains['my_chain_a'] = Chain(['foo', 'bar'])
    chains['my_chain_b'] = Chain(['foo', 'bar'])

    # Add a final function to just one chain
    def zee(state):
        pass

    chains.set_final(zee, scope={'my_chain_a'})

    assert chains['my_chain_a'].get_final() is zee
    assert chains['my_chain_b'].get_final() is None

    # Add a link to multiple chains
    def omm(state):
        pass

    chains.set_final(omm)

    assert chains['my_chain_a'].get_final() is omm
    assert chains['my_chain_b'].get_final() is omm

def test_set_link():
    """Set a link across one or more chains in the chain manager"""
    chains = ChainMgr()

    chains['my_chain_a'] = Chain(['foo', 'bar'])
    chains['my_chain_b'] = Chain(['foo', 'bar'])

    # Add a link to just one chain
    def foo(state):
        pass

    chains.set_link(foo, scope={'my_chain_a'})

    assert chains['my_chain_a'].get_link('foo') is foo
    assert chains['my_chain_b'].get_link('foo') is None

    # Add a final function to multiple chains
    def bar(state):
        pass

    chains.set_link(bar)

    assert chains['my_chain_a'].get_link('bar') is bar
    assert chains['my_chain_b'].get_link('bar') is bar

def test_final_decorator():
    """Set a final function across one or more chains in the chain manager"""
    chains = ChainMgr()

    chains['my_chain_a'] = Chain(['foo', 'bar'])
    chains['my_chain_b'] = Chain(['foo', 'bar'])

    # Add a final function to just one chain
    @chains.final(scope={'my_chain_a'})
    def zee(state):
        pass

    assert chains['my_chain_a'].get_final() is zee
    assert chains['my_chain_b'].get_final() is None

    # Add a final function to multiple chains
    @chains.final
    def omm(state):
        pass

    assert chains['my_chain_a'].get_final() is omm
    assert chains['my_chain_b'].get_final() is omm

def test_link_decorator():
    """
    Set a link across one or more chains in the chain manager with the link
    decorator.
    """
    chains = ChainMgr()

    chains['my_chain_a'] = Chain(['foo', 'bar'])
    chains['my_chain_b'] = Chain(['foo', 'bar'])

    # Add a link to just one chain
    @chains.link(scope={'my_chain_a'})
    def foo(state):
        pass

    assert chains['my_chain_a'].get_link('foo') is foo
    assert chains['my_chain_b'].get_link('foo') is None

    # Add a link to multiple chains
    @chains.link
    def bar(state):
        pass

    assert chains['my_chain_a'].get_link('bar') is bar
    assert chains['my_chain_b'].get_link('bar') is bar

def test_flask_view():
    """
    Return a Flask view that will call a chain against the manager with the
    appropriate HTTP method.
    """
    chains = ChainMgr()

    chains['get'] = Chain(['getter'])
    chains['post'] = Chain(['poster'])

    @chains.link(scope={'get'})
    def getter(state):
        return 'get'

    @chains.link(scope={'post'})
    def poster(state):
        return 'post'

    # Create a test application to run
    app = Flask(__name__)
    app.add_url_rule(
        '/',
        'index',
        chains.flask_view(zee='omm'),
        methods=['GET', 'POST']
        )
    client = app.test_client()

    # Test get request
    res = client.get('/')
    assert res.data == b'get'

    # Test post request
    res = client.post('/')
    assert res.data == b'post'
