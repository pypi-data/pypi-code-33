"""
Classes for implementing execution chains.
"""

from copy import deepcopy
import json
import pprint
import sys
import time

try:
    # The Flask `request` module is required for the `flask_view` method, but we
    # treat this as an option requirement since chains this may not be
    # applicable when using chains.
    from flask import request as flask_request
except ImportError:
    pass


class ChainMgr:
    """
    A class for managing multiple related chains, e.g:

        chains = ChainMgr()
        chains['get']  = Chain(...)
        chains['post'] = Chain(...)

        method = request.method.lower()
        if method in chains:
            chains[method]()
        else:
            abort(405)
    """

    def __init__(self):
        # A map of named chains
        self._chains = {}

    def __contains__(self, name):
        return name in self._chains

    def __getitem__(self, name):
        return self._chains[name]

    def __setitem__(self, name, value):
        self._chains[name] = value

    def __delitem__(self, name):
        del self._chains[name]

    @property
    def chains(self):
        """Return a copy of the chains map for the manager"""
        return self._chains.copy()

    def copy(self):
        """Return a copy of the chain manager"""
        chains = self.__class__()
        for name, chain in self._chains.items():
            chains[name] = chain.copy()
        return chains

    def insert_link(self, target_link, new_link, after=False):
        """
        Insert a new link in every chain before/after every instance of the
        target link. By default new links are inserted before the target link,
        to insert the new link after the target link pass `after` as True to the
        method.
        """
        for chain in self._chains.values():
            chain.insert_link(target_link, new_link, after=after)

    def remove_link(self, target_link):
        """Remove all instances of a link from every chain"""
        for chain in self._chains.values():
            chain.remove_link(target_link)

    def set_final(self, func, scope=None):
        """Sets the final function across one or more chains"""

        if scope is None:
            # If no scope is specified then add the link to all chains
            scope = self._chains.keys()

        for name in scope:
            self[name].set_final(func)

    def set_link(self, func, scope=None, **kwargs):
        """
        Sets a function for a link. Works exactly like the `link()` decorator,
        e.g:

            # Set for all chains
            def foo(state):
                ...

            chains.set_link(foo)

            # Set for the given scope of chains
            def foo(state):
                ...

            chains.add_link(foo, scope={'get', 'post'})

            # Set for the link named 'bar'
            def foo(state):
                ...

            chains.add_link(foo, scope={'get', 'post'}, name='bar')
        """

        if scope is None:
            # If no scope is specified then add the link to all chains
            scope = self._chains.keys()

        for name in scope:
            self[name].set_link(func, **kwargs)

    # Decorators

    def final(self, *args, **kwargs):
        """Sets the final function across one or more chains"""

        def wrap(func):
            if 'scope' in kwargs:
                scope = kwargs.pop('scope')
            else:
                # If no scope is specified then set the final for all chains
                scope = self._chains.keys()

            for name in scope:
                self._chains[name].set_final(func)

            return func

        if len(args) == 1 and callable(args[0]):
            return wrap(args[0])
        else:
            return wrap

    def link(self, *args, **kwargs):
        """
        A decorator that will set the decorated function as a link in the
        given set of chains, e.g:

            # Set for all chains
            @chains.link
            def foo(state):
                ...

            # Set for the given scope of chains
            @chains.link(scope={'get', 'post'})
            def foo(state):
                ...

            # Set for the link named 'bar'
            @chains.link(scope={'get', 'post'}, name='bar')
            def foo(state):
                ...
        """
        def wrap(func):
            if 'scope' in kwargs:
                scope = kwargs.pop('scope')
            else:
                # If no scope is specified then add the link to all chains
                scope = self._chains.keys()

            for name in scope:
                self._chains[name].set_link(func, **kwargs)

            return func

        if len(args) == 1 and callable(args[0]):
            return wrap(args[0])
        else:
            return wrap

    # Framework methods

    def flask_view(self, **kwargs):
        """
        Return a Flask view function for the chain. The keyword arguments are
        used to initialize the chain when called. The request.method (lowercase)
        value is used to determine which chain get's called, therefore the chain
        manager must support at least one applicable HTTP verb.
        """

        def _view():
            assert 'flask' in sys.modules, \
                'Flask must be installed to use this method'

            method = flask_request.method.lower()
            if method in self:
                return self[method](**kwargs)

        return _view


class Chain:
    """
    Chains provide a pattern for *loosely* coupling together a series of
    functions with support for intersections.

    Within a chain logic is broken down into small independent blocks (known
    as links), these links can be easily switched out and/or re-arranged to
    modify the behaviour of the chain.

    Chains are initially defined as a list of named links without associated
    function, for example:

        # An puesdo chain for updating a document via a HTTP POST request
        chain = Chain([
            'lookup',
            'check_permissions',
            'init_form',
            'validate',
            [
                [
                    'update',
                    'redirect'
                ],
                ['template']
            ]
        ])

    The function for each link can then be added using the `set_link` method or
    more typically the `link` decorator like so:

        @chain.link
        def lookup(state):
            state.product = Product.by_id(request.values.get('id'))
            if not state.product:
                abort(404)

    The flow of execution is controlled by the return value of the link, and
    these rules are simple but important:

    - If `None` is returned then call the next link.
    - If a `True` or `False` is returned then this determines the fork taken at
      an intersection.
    - If any other value is returned then the execution is stoped and the value
      returned to the caller.

    An intersection is represented by a list containing two lists of named
    links, as in the example chain above where an intersection follows the
    'validate' link, validate might look something like this:

        @chain.link
        def validate(state):
            return scope.form.validate()

    If the form is valid then 'update' will be exectuted next, otherwise
    'template' will be, at which template will return a response in form of a
    render template and execution will end (even if there are other links after
    this):

        @chain.link
        def template(state):
            # We send the entire scope to the template as this makes it easier
            return render_template('products/update.html', **scope)

    By breaking the logic down in this way chains make it easy to modify their
    behaviour from anywhere. The initial reason for designing the chain pattern
    was to allow controllers for models in our web applications (which provide
    standard functions for add, update, delete, list, view, etc) to be easily
    modified without the need to override methods which typically contain
    complete chunks of logic (such as everything in our example chain).
    """

    def __init__(self, links):
        # A structured list of links that make up the chain
        self._links = links

        # A map of links to functions
        self._funcs = {}

        # A function guaranteed to be called after the chain is executed
        self._final = None

    def __call__(self, _trace=False, **kwargs):
        """Call the chain of links"""

        # Create a state object that will be passed to (and potentially
        # mutated by) each link in the chain.
        state = State(**kwargs)
        state._call = State(
            route=[],
            trace=[]
        )

        # We call the chain within a try..finally block
        try:
            r = self._call(_trace, state)

            if _trace:

                # If the call was traced print details of the trace
                printer = pprint.PrettyPrinter(width=78, compact=True)

                print('\n~ Trace ~')
                for item in state._call.trace:
                    print('\n<{link}> took {duration:.4f}s'.format(**item))
                    print('--')
                    printer.pprint(item['state'])
                print('\n~ fin ~\n')

            return r

        finally:
            if not (self._final is None):
                self._final(state)

    def __repr__(self):
        return 'Chain: {0}'.format(json.dumps(self.links, indent='    '))

    @property
    def links(self):
        """Return (a copy) of links in the chain"""
        return deepcopy(self._links)

    @links.setter
    def links(self, value):
        """Set the links in the chain (restructure)"""
        self._links = deepcopy(value)

    def copy(self):
        """Return a copy of the chain"""
        chain = self.__class__(self.links)
        chain._funcs = dict(self._funcs)
        return chain

    def get_final(self):
        """Get the final function for the chain"""
        return self._final

    def get_link(self, name):
        """Return the function associated with the named link"""
        return self._funcs.get(name)

    def insert_link(self, target_link, new_link, after=False):
        """
        Insert a new link in the chain before/after every instance of the target
        link. By default new links are inserted before the target link, to
        insert the new link after the target link pass `after` as True to the
        method.
        """
        parents = [self._links]
        indexes = [0]

        while True:
            index = indexes[-1]
            links = parents[-1]

            # Check if we're at the end of the current link list...
            if index >= len(links):
                # ...we are so pop this link list of the stack
                parents.pop()

                # Check if this was the last link list...
                if len(parents) == 0:
                    # ...it is so we're done
                    break
                else:
                    # ...it isn't so pop the index and continue with the
                    # previous link list.
                    indexes.pop()
                    continue

            # Get the current link
            link = parents[-1][index]
            indexes[-1] += 1

            # Check if the link is a intersection...
            if isinstance(link, list):
                # ...it is so add each fork to the stack
                parents += [link[1], link[0]]
                indexes += [0, 0]
                continue
            else:
                # ...it isn't so check if we need to add the new link after this
                # link.
                if link == target_link:
                    # Add the new link
                    if after:
                        parents[-1].insert(indexes[-1], new_link)
                    else:
                        parents[-1].insert(index, new_link)
                    indexes[-1] += 1

    def remove_link(self, target_link):
        """Remove all instances of a link from the chain"""
        parents = [self._links]
        indexes = [0]

        while True:
            index = indexes[-1]
            links = parents[-1]

            # Check if we're at the end of the current link list...
            if index >= len(links):
                # ...we are so pop this link list of the stack
                parents.pop()

                # Check if this was the last link list...
                if len(parents) == 0:
                    # ...it is so we're done
                    break
                else:
                    # ...it isn't so pop the index and continue with the
                    # previous link list.
                    indexes.pop()
                    continue

            # Get the current link
            link = parents[-1][index]
            indexes[-1] += 1

            # Check if the link is a intersection...
            if isinstance(link, list):
                # ...it is so add each fork to the stack
                parents += [link[1], link[0]]
                indexes += [0, 0]
                continue
            else:
                # ...it isn't so check if we need to remove the link.
                if link == target_link:
                    # Remove the link
                    parents[-1].remove(target_link)
                    indexes[-1] -= 1

    def set_final(self, func):
        """
        Set a function that is guaranteed to be called once the chain has
        executed (or failed to), think try...finally.
        """
        self._final = func

    def set_link(self, func, name=None):
        """
        Sets a function as a link. Works exactly like the `link()` decorator,
        e.g:

            def foo(state):
                ...

            chains.set_link(foo)

            # Set for the link named 'bar'
            def foo(state):
                ...

            chains.set_link(foo, name='bar')
        """
        self._funcs[name or func.__name__] = func

    def super(self, state):
        """
        Given an active state object, call the current link against this
        chain.

        It's often useful when overwriting a link to call the the original
        link, similar to calling super when overriding a method in a class
        you inherit from.

        This method is basically a shortcut for:

            my_chain.get_link('decorate')(state)

        Which becomes:

            my_chain.super(state)

        Active state objects contains a `_call` state with a list of links
        called so far (in `route`) and so `super` simply peeks at the last
        link in the route, finds the associated link in this chain and calls
        it with the given state.
        """

        assert '_call' in state, 'Not a valid state object'

        link = state._call['route'][-1]
        func = self.get_link(link)

        assert func, 'No corresponding link `{}` in chain'.format(link)

        return func(state)

    def update(self, links):
        """Update the chain with a new structured list of links"""
        self._links = links

    # Decorators

    def link(self, *args, **kwargs):
        """
        A decorator that will set the decorated function as a link, if no `name`
        keyword argument is specified then the function's name will be used to
        determine which link the function should be mapped to, e.g:

            @chain.link
            def foo(state):
                ...

            # Set for the link named 'bar'
            @chain.link(name='bar')
            def foo(state):
                ...
        """

        def wrap(func):
            self.set_link(func, **kwargs)
            return func

        if len(args) == 1 and callable(args[0]):
            return wrap(args[0])
        else:
            return wrap

    def final(self, func):
        """A decorator that will set the final function for the chain"""
        self.set_final(func)
        return func

    # Private methods

    def _call(self, _trace, state):
        """Call the chain of links"""

        # Call each link in the chain
        fork = None
        route = self.links
        while len(route):
            # Get the next link
            link = route.pop(0)

            # Check if the link is a fork
            if isinstance(link, list):

                assert len(link) == 2, \
                        'Intersections must have exactly 2 routes: {0}'\
                        .format(link)

                assert type(fork) == bool, \
                        'No fork determine at intesection: {0}'.format(link)

                # Fork to the new route
                route = link[0 if fork else 1]

                # Reset fork
                fork = None

                # Continue to the first link in the new route
                continue

            # Select the function for the link
            func = self._funcs.get(link)

            assert func is not None, 'Chain is incomplete: {0}'.format(link)

            # Track the link against the scope
            state._call.route.append(link)

            if _trace:
                # If the call is being traced record the point at which we
                # called this link.
                start = time.time()

            # Call the link function
            result = func(state)

            if _trace:
                # If the call is being traced record the link, it's call
                # duration and the state after the call.

                state_copy = state.copy()
                del state_copy['_call']

                state._call.trace.append({
                    'link': link,
                    'duration': time.time() - start,
                    'state': state_copy
                })

            # Determine the next step...

            if result is None:
                # ...no result returned so continue to the next link
                continue

            elif type(result) is bool:
                # ...a boolean was returned so the next link will be an
                # intersection and the fork taken will be determine by the
                # result.
                fork = result
                continue

            # ...something else was returned so we leave break from the chain
            # and return the result.
            return result


class State(dict):
    """
    An dictionary-like object that supports dot notation syntax. State objects
    are used to pass state between links within a chain.
    """

    def __getattr__(self, attr):
        if attr.startswith('__'):
            raise AttributeError
        return self.get(attr, None)

    __setattr__ = dict.__setitem__

    __delattr__ = dict.__delitem__
