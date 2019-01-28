from automaton_tools.regex_parser.Components import *



class Automaton:

    def __init__(self):
        self.states = set()
        self.transition = set() # triplet

    def getAlphabet(self):
        return { v for (_,_,v) in self.transition }

    def drawGraph(self,path = "graph"):
        from graphviz import Digraph

        isNFA = type(self.end) is not set
        if isNFA:
            dot = Digraph(comment='It is NFA')
            end = set([self.end])
        else:
            dot = Digraph(comment='It is DFA')
            end = self.end
        dot.format = 'png'

        ss = list(self.states)
        m2 = dict()
        for ii,s in enumerate(ss):
            name = f"node_{ii}"
            m2[s] = name
            l = str(s)
            if s == self.start:
                dot.node(name,label = l,
                         _attributes={'color':'lightblue2',"style":"filled"})
            elif s in end:
                dot.node(name,label = l,
                         _attributes={'color':'black:black',"peripheries":"2"})
            else:
                dot.node(name, label=l)


        for t in self.transition:
            i,j,e = t
            dot.edge( m2[i],m2[j],label = str(e))

        dot.render(path, view=False)


class AutomatonBuild(Automaton):

    def __init__(self):
        self.states = set()
        self.transition = set() # triplet
        self.start = None
        self.end = None

    def concat(self,b):
        self.transition |= set(
            [(self.end, b.start,Edge_Epsilon)]
        )
        self.transition |= b.transition
        self.states |= b.states
        self.end = b.end
        return self

    @staticmethod
    def defaultOne():
        x = AutomatonBuild()
        x.start = State()
        x.end = State()
        x.states = set([x.start,x.end])
        return x

    @staticmethod
    def charset(ch:CharSet):
        x = AutomatonBuild.defaultOne()
        x.transition = set( [(x.start, x.end,ch)] )
        return x

    @staticmethod
    def star(a):
        x = AutomatonBuild.defaultOne()
        x.transition = set([
                (x.start, x.end,Edge_Epsilon),
                (x.end,   x.start, Edge_Epsilon),
                (x.start, a.start, Edge_Epsilon),
                (a.end,   x.end, Edge_Epsilon)
        ])
        x.transition |= a.transition
        x.states |= a.states
        return x

    @staticmethod
    def plus(a):
        x = AutomatonBuild.defaultOne()
        x.transition = set([
                (x.end,   x.start, Edge_Epsilon),
                (x.start, a.start, Edge_Epsilon),
                (a.end,   x.end, Edge_Epsilon)
        ])
        x.states |= a.states
        x.transition |= a.transition
        return x

    @staticmethod
    def orRule(a,b):
        x = AutomatonBuild.defaultOne()
        x.transition = set([
                (x.start,  a.start, Edge_Epsilon),
                (a.end,   x.end, Edge_Epsilon),
                (x.start, b.start, Edge_Epsilon),
                (b.end, x.end, Edge_Epsilon)
        ])
        x.transition |= a.transition
        x.transition |= b.transition
        x.states |= a.states
        x.states |= b.states
        return x


    @staticmethod
    def optional(a):
        x = AutomatonBuild.defaultOne()
        x.transition = set([
                (x.start, x.end,Edge_Epsilon),
                (x.start, a.start, Edge_Epsilon),
                (a.end,   x.end, Edge_Epsilon)
        ])
        x.transition |= a.transition
        x.states |= a.states
        return x

