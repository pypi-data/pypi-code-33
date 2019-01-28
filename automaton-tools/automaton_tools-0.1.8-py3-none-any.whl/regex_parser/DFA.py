from .NFA import *

from collections import *

class DFA(Automaton):

    def __init__(self,nfa:NFA):
        if nfa is not None:
            nfa_state_id_map, m = nfa.createStateEdgeTable()
            #m represent dfa transition between nodes

            self.start = 0
            self.end = set()

            for k,v in nfa_state_id_map.items():
                if nfa.end.id in k:
                    self.end.add(v)

            self.transMap = m
            self.transition = self.getTransition()
            self.states = set(nfa_state_id_map.values())

    @staticmethod
    def constructDFA(states,transMap,start,end):
        dfa = DFA(None)
        dfa.states = states
        dfa.transMap = transMap
        dfa.transition = dfa.getTransition()
        dfa.start = start
        dfa.end = end
        return dfa

    def getTransition(self):
        return {(id, id2, e) for (id, e), id2 in self.transMap.items()}

    def _expand(self,id,edge):
        return self.transMap[(id,edge)]

    # use　Myphill-Nerode Theorem, table method
    def minimize(self):

        def show_table(tbmap):
            import sys
            print("show table.......")
            last_row = 0
            for i in table_keys:
                (row, col) = i
                if row != last_row:
                    last_row = row
                    print("\n")
                    sys.stdout.write("    \t\t" * (col-1))
                sys.stdout.write( str(tbmap[i]) + "\t\t")
            print("\n")

        #------------- init ---------------
        n = len(self.states) # number of states
        n0 = n
        n = n + 1 # add a dead state
        table = { (j,i):False for i in range(n) for j in range(i) } # upper diagonal matrix
        table_keys = sorted(list(table.keys()))


        # init table
        for (a,b) in table_keys:
            if (a in self.end and b not in self.end) or \
               (b in self.end and a not in self.end):
                table[(a,b)] = True


        # get all edges from each state
        state_edge = defaultdict(set)
        for (src,edge) in self.transMap.keys():
            state_edge[src].add(edge)

        # init transition of state pairs
        pair_tansition = defaultdict(list)

        alphabet = self.getAlphabet()
        for (a,b) in table_keys:
            for e in alphabet:
                a1 = n0  # dead state
                b1 = n0  # dead state
                if e in state_edge[a]:
                    a1 = self.transMap[(a,e)]
                if e in state_edge[b]:
                    b1 = self.transMap[(b,e)]
                if a1 != b1: #remove diagonal
                    pair_tansition[(a,b)] += [ (a1,b1) if a1 < b1 else (b1,a1) ]

        #------------- loop -----------------
        updated = True
        while updated:
            updated = False
            for t1 in table_keys:
                if not table[t1]:
                    for t2 in pair_tansition[t1]:
                        if table[t2]:
                            table[t1] = True
                            updated = True
                            break
            #print("table",table)


        # ---------------- merge unmarked states ----------
        # disjoint set, use array instead of dict
        parents = list(range(0,n))
        def find(x):
            while parents[x] != x:
                prev = x
                x = parents[x]
                parents[prev] = parents[x]
            return x

        def union(x,y):
            a = find(x)
            b = find(y)
            if a != b: # not the same set
                parents[y] = parents[a]
            return x

        for (a,b),v in table.items():
            if not v:
                union(a,b)

        # new set id starts from 0
        tempdict = dict()
        n2 = 0
        for i in range(n):
            t = parents[i]
            if t not in tempdict:
                tempdict[ t ] = n2
                n2 += 1
            parents[i] = tempdict[t]

        state_newid_map = defaultdict(set)
        for id,iset in enumerate(parents):
            state_newid_map[iset].add(id)

        new_states = range(0,n2)
        new_transMap = dict()
        outdegree_states = set()
        for (src, edge), dst in self.transMap.items():
            new_transMap[(parents[src], edge)] = parents[dst]
            if parents[src] != parents[dst]:
                outdegree_states.add(parents[src])

        new_end = {
            newid for oldid,newid in enumerate(parents) if oldid in self.end
        }

        # ------------- remove zero outdegree state unless it is in end -----------------
        n3 = 0
        parents2 = list(range(n2))
        for i in range(n2):
            if parents2[i] in outdegree_states or parents2[i] in new_end:
                parents2[i] = n3
                n3 += 1
            else:
                parents2[i] = -1

        new_states = list(range(n3)) # new id
        new_transMap = {
            (parents2[src], edge): parents2[dst]
            for (src, edge), dst in frozenset(new_transMap.items()) if parents2[src] != -1 and parents2[dst] != -1
        }

        new_dfa = DFA.constructDFA( new_states,new_transMap,start = 0,end  = new_end )
        return new_dfa


    def _compile(self):
        if hasattr(self, 'routes'):
            return
        routes = defaultdict(list)
        for (src, edge), dst in self.transMap.items():
            routes[src].append( (edge,dst) )
        self.routes = routes

    def match(self,target:str):
        self._compile()
        cursor = self.start
        for ch in target:
            found = False
            for (e,dst) in self.routes[cursor]:
                if e.match(ch):
                    cursor = dst
                    found = True
                    break
            if not found:
                return False
        return cursor in self.end

    @staticmethod
    def fromRegex(regex):
        nfa = NFA.fromRegex(regex)
        dfa = DFA(nfa)
        #dfa = dfa.minimize()
        #dfa._compile()
        return dfa

