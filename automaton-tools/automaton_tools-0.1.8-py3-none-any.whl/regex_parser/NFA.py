from .Automaton import *
from .grammar import *
from .Automaton import *
from .AutomatonVisitor import *
from .AutomatonErrorListener import *

from collections import *

class NFA(Automaton):
    def __init__(self,a:AutomatonBuild):
        self.a = a
        self.states = a.states
        self.start = a.start
        self.end = a.end
        self.transition = a.transition

        self.assignStateIds()
        self.transMap = self.transitionMap()

    def assignStateIds(self):
        for i,j in enumerate(self.states):
            j.id = i

    def transitionMap(self):
        import collections
        # defaultdict
        m = collections.defaultdict(list)
        for (i, j, c) in self.transition:
            m[i.id].append((j.id,c))
        return m

    def eClosure(self,stateIds:set):
        result = set()
        left = set(stateIds)
        while len(left) > 0:
            s2 = set()
            for i in left:
                s = [id2 for id2,c in self.transMap[i]
                     if c == Edge_Epsilon and id2 not in result ]
                s2 |= set(s)
            result |= left
            left = s2
        return result

    def expand(self,stateIds:set,ch:CharSet):
        s2 = set()
        for i in stateIds:
            s = [id2 for id2, c in self.transMap[i]
                 if c == ch ]
            s2 |= set(s)
        return s2


    def createStateEdgeTable(self):
        m = dict()
        start = self.eClosure(set([ self.start.id ]))
        start = frozenset(start)
        key_map = dict()
        c = 0
        key_map[start] = c
        left = [ (c,start) ]
        c += 1
        while len(left) > 0:
            next_left = []
            for id3,i in left: #src
                # find all edge from i
                edges = { e for node in i for _, e in self.transMap[node]
                    if e != Edge_Epsilon }
                for e in edges: # arc
                    expanded = self.expand(i,e)
                    s = self.eClosure(expanded)
                    if len(s) < 1:
                        continue
                    s = frozenset(s)
                    if s not in key_map:
                        # assign new set an id
                        key_map[s] = c
                        target_id = c
                        next_left += [(c, s)]
                        c += 1
                    else :
                        target_id = key_map[s]

                    # record transition
                    m[(id3, e)] = target_id

            #remove duplicated
            left = next_left

        return key_map,m

    @staticmethod
    def fromRegex(regex):
        input = InputStream(regex)
        lexer = RegexLexer(input)
        stream = CommonTokenStream(lexer)
        parser = RegexParser(stream)
        parser.addErrorListener(AutomatonErrorListener)
        root = parser.root()
        visitor = AutomatonVisotor()
        automaton = visitor.visit(root)

        nfa = NFA(automaton)
        return nfa