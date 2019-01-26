from .parsetable import GetNumberOfInputs
from ast import literal_eval

# Named neighbourhoods:
nhoods = {'2': [(-1, 0), (1, 0), (0, 0), (0, 0)],
          '4': [(0, -1), (-1, 0), (1, 0), (0, 1), (0, 0), (0, 0)],
          '8': [(-1, -1), (1, -1), (-1, 1), (1, 1), (0, -1), (-1, 0), (1, 0), (0, 1), (0, 0), (0, 0)]}

def ReadRuleTree(list_of_lines):

    numInputs = 0
    num_nodes = 0
    n_states = 0

    list_of_nodes = []

    for line in list_of_lines:

        line = line.split('#')[0].strip()

        if (line == '') or (line[0] == '@'):
            continue

        if '=' in line:

            command, thing = tuple([x.strip() for x in line.split('=')])

            if command == 'num_states':
                n_states = int(thing)
                if (n_states < 2) or (n_states > 65536):
                    raise ValueError('n_states must be between 2 and 65536, inclusive')
            elif command in ['num_neighbors', 'num_neighbours']:
                nstring = thing
                if nstring in nhoods:
                    nhood = nhoods[nstring]
                else:
                    nhood = [tuple(x) for x in literal_eval(nstring)]
                numInputs = GetNumberOfInputs(nhood)
            elif command == 'num_nodes':
                num_nodes = int(thing)

        else:

            # Replace all non-digits with whitespace:
            line = ''.join([(c if (c in '0123456789') else ' ') for c in line]).strip()

            if line == '':
                continue

            if (n_states <= 0) or (num_nodes <= 0) or (numInputs <= 0):
                raise RuntimeError('num_states, num_neighbours, and num_nodes must all be defined prior to the first node.')

            # Tree node
            numbers = [int(x) for x in line.split()]
            depth = numbers[0]
            children = numbers[1:]

            if depth > 1:
                # Convert node number to index into uint32_t array:
                children = [n_states * (num_nodes - 1 - x) for x in children]

            list_of_nodes.append(children)

    if (len(list_of_nodes) != num_nodes):
        raise RuntimeError('%d nodes found; %d expected' % (len(list_of_nodes), num_nodes))

    # We want the root to be position zero:
    list_of_nodes = list_of_nodes[::-1]

    return n_states, nhood, list_of_nodes
