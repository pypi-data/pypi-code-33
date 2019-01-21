from __future__ import generators

import heapq
from difflib import SequenceMatcher

from numpy import *


class BreakIt(Exception): pass

def yrange(n,start=0):
    """
    :author: Dr. Massimo Domenico Sammito
    :email: msacri@ibmb.csic.es / massimo.sammito@gmail.com
    :param n:
    :param start:
    :return:
    """
    i = start
    while i < n:
        yield i
        i += 1

def LCS(s1, s2, extremity=False):
    """
    :author: Dr. Massimo Domenico Sammito
    :email: msacri@ibmb.csic.es / massimo.sammito@gmail.com
    :param s1:
    :param s2:
    :param extremity:
    :return:
    """
    s = SequenceMatcher(None, s1, s2)
    e = s.find_longest_match(0, len(s1), 0, len(s2))
    if (not extremity and len(s1) <= len(s2)) or (
            extremity and len(s1) <= len(s2) and (e.a == 0 or e.a + e.size == len(s1))):
        d = s1[e.a:e.a + e.size]
    elif (not extremity and len(s1) > len(s2)) or (
            extremity and len(s1) > len(s2) and (e.b == 0 or e.b + e.size == len(s2))):
        d = s2[e.b:e.b + e.size]
    else:
        d = ""

    return d

def split_string_by_common(a, e):
    """
    :author: Dr. Massimo Domenico Sammito
    :email: msacri@ibmb.csic.es / massimo.sammito@gmail.com
    :param a:
    :param e:
    :return:
    """
    c = a.find(e)
    strinit = a[:c] if not a[:c].endswith("/") else a[:c-1]
    strend = a[c + len(e):] if not a[c + len(e):].endswith("/") else a[c + len(e):-1]
    common = a[c:c + len(e)] if not a[c:c + len(e)].endswith("/") else a[c:c + len(e)-1]
    common = common if not common.startswith("/") else common[1:]

    return strinit,common,strend

def substract_string(a, e):
    """
    :author: Dr. Massimo Domenico Sammito
    :email: msacri@ibmb.csic.es / massimo.sammito@gmail.com
    :param a:
    :param e:
    :return:
    """
    c = a.find(e)
    different = a[:c] + a[c + len(e):]
    common = a[c:c + len(e)]
    starting = False
    ending = False
    if c == 0:
        starting = True
    if c + len(e) == len(a):
        ending = True

    return different, common, starting, ending


def rename_section(cp, section_from, section_to):
    """
    :author: Dr. Massimo Domenico Sammito
    :email: msacri@ibmb.csic.es / massimo.sammito@gmail.com
    :param cp:
    :param section_from:
    :param section_to:
    :return:
    """
    items = cp.items(section_from)
    cp.add_section(section_to)
    for item in items:
        cp.set(section_to, item[0], item[1])
    cp.remove_section(section_from)


def get_percentile_llg(v, x, T):
    """
    :author: Dr. Massimo Domenico Sammito
    :email: msacri@ibmb.csic.es / massimo.sammito@gmail.com
    :param v:
    :param x:
    :param T:
    :return:
    """
    if len(v) != len(x):
        sys.exit('Input vectors v and x must have same length')
    s = sorted(v)
    n = int(round(T * len(v) + 0.5))
    safe_llg = s[n - 1]
    basic = []
    for q in range(len(v)):
        vale = v[q]
        if vale <= safe_llg:
            basic.append(x[q])

    return basic, safe_llg


def get_percentage_llg(v, x, T):
    """
    :author: Dr. Massimo Domenico Sammito
    :email: msacri@ibmb.csic.es / massimo.sammito@gmail.com
    :param v:
    :param x:
    :param T:
    :return:
    """
    if len(v) != len(x):
        sys.exit('Input vectors v and x must have same length')
    s = sorted(v)
    safe_llg = s[-1] * T
    basic = []
    for q in range(len(v)):
        vale = v[q]
        if vale <= safe_llg:
            basic.append(x[q])

    return basic, safe_llg


def get_percentage_llg_range(v, x, T1, T2):
    """
    :author: Dr. Massimo Domenico Sammito
    :email: msacri@ibmb.csic.es / massimo.sammito@gmail.com
    :param v:
    :param x:
    :param T1:
    :param T2:
    :return:
    """
    if len(v) != len(x):
        sys.exit('Input vectors v and x must have same length')
    a, b = get_percentage_llg(v, x, T1)
    if T2 >= 1.0:
        T2 = 1.0
    c, d = get_percentage_llg(v, x, T2)
    basic = []
    for e in c:
        if e not in a:
            basic.append(e)

    return basic, d


def get_matrix(n, m):
    """
    :author: Dr. Massimo Domenico Sammito
    :email: msacri@ibmb.csic.es / massimo.sammito@gmail.com

    :param n:
    :param m:
    :return:
    """

    return [[0.0 for _ in range(m)] for _ in range(n)]


def cantor_pairing(listall):
    """
    :author: Dr. Massimo Domenico Sammito
    :email: msacri@ibmb.csic.es / massimo.sammito@gmail.com

    :param listall:
    :return:
    """
    if len(listall) == 0:
        return None
    if len(listall) == 1:
        return listall[0]
    lastElement = listall.pop(0)
    return (0.5 * (cantor_pairing(listall) + lastElement) * (cantor_pairing(listall) + lastElement + 1) + lastElement)


def erase_bad_region(v, x, minT):
    """
    :author: Dr. Massimo Domenico Sammito
    :email: msacri@ibmb.csic.es / massimo.sammito@gmail.com

    :param v:
    :param x:
    :param minT:
    :return:
    """
    if len(v) != len(x):
        sys.exit('Input vectors v and x must have same length')
    trimmed = []
    for q in range(len(v)):
        vale = v[q]
        if vale <= minT:
            trimmed.append(x[q])
    return trimmed


def flat_regions(v, x, minT):
    """
    :author: Dr. Massimo Domenico Sammito
    :email: msacri@ibmb.csic.es / massimo.sammito@gmail.com

    :param v:
    :param x:
    :param minT:
    :return:
    """
    if len(v) != len(x):
        sys.exit('Input vectors v and x must have same length')

    flat_reg = []
    delta = 0.0003
    start = None
    end = None
    start_i = None
    end_i = None
    for q in range(len(v)):
        vale = v[q]
        if vale < minT:
            if start != None and end == None:
                start = None
                end = None
                start_i = None
                end_i = None
            continue
        if start == None:
            start = vale
            end = None
            start_i = q
        elif start != None:
            if abs(vale - start) <= delta:
                end = vale
                end_i = q
            elif end != None:
                flat_reg.append([x[start_i], x[end_i]])
                start_i = q
                end_i = None
                start = vale
                end = None
            else:
                start_i = q
                end_i = None
                start = vale
                end = None
    if start != None and end != None and start_i != None and end_i != None:
        flat_reg.append([x[start_i], x[end_i]])

    print "FLAT_REGIONS first detection"
    print flat_reg

    restart = True
    todele = []
    while restart:
        for ind in todele:
            print "To delete", ind
            del flat_reg[ind]
        todele = []
        restart = False
        for i in range(len(flat_reg)):
            restart = False
            for j in range(i + 1, len(flat_reg)):
                peak1 = flat_reg[i]
                peak2 = flat_reg[j]
                if peak2[0] - peak1[1] <= 3:
                    flat_reg[i] = [peak1[0], peak2[1]]
                    todele.append(j)
                    restart = True
                    print "Merging peak", peak1, "with", peak2
                    break
            if restart:
                print "starting again"
                break

    print "FLAT_REGIONS merged"
    print flat_reg
    fla = []
    for peak in flat_reg:
        if peak[1] - peak[0] >= 3:
            fla.append(peak)

    print "FLAT_REGIONS trimmed <3 peaks"
    print fla

    return fla


def top_max_peaks(v, x, tops):
    """
    :author: Dr. Massimo Domenico Sammito
    :email: msacri@ibmb.csic.es / massimo.sammito@gmail.com

    :param v:
    :param x:
    :param tops:
    :return:
    """
    delta = 1
    maxp = []
    minp = []
    # print "======================V===================="
    # print v
    # print "==========================================="
    # print "======================X===================="
    # print x
    # print "==========================================="

    while len(maxp) < tops and delta > 0:
        maxp, minp = peakdet(v, delta, x)
        print "PEAKS ANALYSYS: ", len(maxp), delta, tops
        delta -= 0.001
    return maxp


def top_min_peaks(v, x, tops):
    """
    :author: Dr. Massimo Domenico Sammito
    :email: msacri@ibmb.csic.es / massimo.sammito@gmail.com

    :param v:
    :param x:
    :param tops:
    :return:
    """
    delta = 1
    maxp = []
    minp = []
    while len(minp) < tops and delta > 0:
        maxp, minp = peakdet(v, delta, x)
        delta -= 0.001
    return minp


def peakdet(v, delta, x=None):
    """
    :author: Dr. Massimo Domenico Sammito
    :email: msacri@ibmb.csic.es / massimo.sammito@gmail.com

    :param v:
    :param delta:
    :param x:
    :return:
    """
    maxtab = []
    mintab = []

    if x is None:
        x = arange(len(v))

    v = asarray(v)

    if len(v) != len(x):
        sys.exit('Input vectors v and x must have same length')

    if not isscalar(delta):
        sys.exit('Input argument delta must be a scalar')

    if delta <= 0:
        sys.exit('Input argument delta must be positive')

    mn, mx = Inf, -Inf
    mnpos, mxpos = NaN, NaN

    lookformax = True

    for i in arange(len(v)):
        this = v[i]
        if this > mx:
            mx = this
            mxpos = x[i]
        if this < mn:
            mn = this
            mnpos = x[i]

        if lookformax:
            if this < mx - delta:
                maxtab.append((mxpos, mx))
                mn = this
                mnpos = x[i]
                lookformax = False
        else:
            if this > mn + delta:
                mintab.append((mnpos, mn))
                mx = this
                mxpos = x[i]
                lookformax = True

    return array(maxtab), array(mintab)


class priorityDictionary(dict):
    """
    :author: Dr. Massimo Domenico Sammito
    :email: msacri@ibmb.csic.es / massimo.sammito@gmail.com

    """
    def __init__(self):
        '''Initialize priorityDictionary by creating binary heap
of pairs (value,key).  Note that changing or removing a dict entry will
not remove the old pair from the heap until it is found by smallest() or
until the heap is rebuilt.'''
        self.__heap = []
        dict.__init__(self)

    def smallest(self):
        '''Find smallest item after removing deleted items from heap.'''
        if len(self) == 0:
            raise IndexError, "smallest of empty priorityDictionary"
        heap = self.__heap
        while heap[0][1] not in self or self[heap[0][1]] != heap[0][0]:
            lastItem = heap.pop()
            insertionPoint = 0
            while 1:
                smallChild = 2 * insertionPoint + 1
                if smallChild + 1 < len(heap) and \
                                heap[smallChild] > heap[smallChild + 1]:
                    smallChild += 1
                if smallChild >= len(heap) or lastItem <= heap[smallChild]:
                    heap[insertionPoint] = lastItem
                    break
                heap[insertionPoint] = heap[smallChild]
                insertionPoint = smallChild
        return heap[0][1]

    def __iter__(self):
        '''Create destructive sorted iterator of priorityDictionary.'''

        def iterfn():
            while len(self) > 0:
                x = self.smallest()
                yield x
                del self[x]

        return iterfn()

    def __setitem__(self, key, val):
        '''Change value stored in dictionary and add corresponding
pair to heap.  Rebuilds the heap if the number of deleted items grows
too large, to avoid memory leakage.'''
        dict.__setitem__(self, key, val)
        heap = self.__heap
        if len(heap) > 2 * len(self):
            self.__heap = [(v, k) for k, v in self.iteritems()]
            self.__heap.sort()  # builtin sort likely faster than O(n) heapify
        else:
            newPair = (val, key)
            insertionPoint = len(heap)
            heap.append(None)
            while insertionPoint > 0 and \
                            newPair < heap[(insertionPoint - 1) // 2]:
                heap[insertionPoint] = heap[(insertionPoint - 1) // 2]
                insertionPoint = (insertionPoint - 1) // 2
            heap[insertionPoint] = newPair

    def setdefault(self, key, val):
        '''Reimplement setdefault to call our customized __setitem__.'''
        if key not in self:
            self[key] = val
        return self[key]

class DisjointSet(object):
    """
    :author: Dr. Massimo Domenico Sammito
    :email: msacri@ibmb.csic.es / massimo.sammito@gmail.com

    """
    def __init__(self):
        self.parent = None

    def find(self):
        if self.parent is None: return self
        return self.parent.find()

    def union(self, other):
        them = other.find()
        us = self.find()
        if them != us:
            us.parent = them


class Atom(object):
    """
    :author: Dr. Massimo Domenico Sammito
    :email: msacri@ibmb.csic.es / massimo.sammito@gmail.com

    """
    def __init__(self):
        self.coord = None

    def set_coord(self, coordi):
        self.coord = coordi

    def get_coord(self):
        return self.coord


class Heap(object):
    """
    :author: Dr. Massimo Domenico Sammito
    :email: msacri@ibmb.csic.es / massimo.sammito@gmail.com

    """

    def __init__(self):
        """ create a new min-heap. """
        self._heap = []

    def push(self, priority, item):
        """ Push an item with priority into the heap.
            Priority 0 is the highest, which means that such an item will
            be popped first."""
        # assert priority >= 0
        heapq.heappush(self._heap, (priority, item))

    def pop(self):
        """ Returns the item with lowest priority. """
        (prio, item) = heapq.heappop(self._heap)  # (prio, item)[1] == item
        return (prio, item)

    def len(self):
        return len(self._heap)

    def asList(self):
        return self._heap

    def __iter__(self):
        """ Get all elements ordered by asc. priority. """
        return self

    def next(self):
        """ Get all elements ordered by their priority (lowest first). """
        try:
            return self.pop()
        except IndexError:
            raise StopIteration


###GRAPHS###
def printGraph(vector, se):
    """
    :author: Dr. Massimo Domenico Sammito
    :email: msacri@ibmb.csic.es / massimo.sammito@gmail.com

    :param vector:
    :param se:
    :return:
    """
    vec1 = []
    vec2 = []
    for i in vector:
        vec1.append(i)

    for i in vector:
        vec2.append(i)

    vec1.sort()
    outp = []
    outp.append([" " for _ in range(len(vec2))])
    row = 0
    underzero = False
    rowzero = -1
    while len(vec1) > 0:
        a = vec1.pop()
        if (a < 0 and underzero == False):
            outp.append(["-" for _ in range(len(vec2))])
            rowzero = row
            row += 1
            underzero = True
        b = vec2.count(a)
        if b > 1:
            ind = vec2.index(a)
            vec2[ind] = -inf
            outp[row][ind] = "*"
        else:
            ind = vec2.index(a)
            vec2[ind] = -inf
            outp[row][ind] = "*"
            outp.append([" " for _ in range(len(vec2))])
            row += 1

    for i in range(len(outp)):
        for j in range(len(outp[i])):
            if outp[i][j] == "*":
                for l in range(i + 1, len(outp)):
                    if l <= rowzero:
                        outp[l][j] = "+"

                for l in range(0, i):
                    if l > rowzero:
                        outp[l][j] = "+"

    stringa = ""
    nu = ""
    for i in range(len(outp)):
        nu = ""
        zeroLine = False
        for j in range(len(outp[i])):
            if outp[i][j] == "-":
                zeroLine = True
            stringa += outp[i][j]
            nu += "_"
        stringa += "|"
        if zeroLine:
            stringa += " 0\n"
        else:
            stringa += "\n"
    stringa += se + "\n"
    stringa += nu + "\n"

    return stringa


def strongly_connected_components(graph):
    """
    :author: Dr. Massimo Domenico Sammito
    :email: msacri@ibmb.csic.es / massimo.sammito@gmail.com

    :param graph:
    :return:
    """

    result = []
    stack = []
    low = {}

    def visit(node):
        if node in low: return

        num = len(low)
        low[node] = num
        stack_pos = len(stack)
        stack.append(node)

        for successor in graph[node]:
            visit(successor)
            low[node] = min(low[node], low[successor])

        if num == low[node]:
            component = tuple(stack[stack_pos:])
            del stack[stack_pos:]
            result.append(component)
            for item in component:
                low[item] = len(graph)

    for node in graph:
        visit(node)

    return result


def topological_sort(graph):
    """
    :author: Dr. Massimo Domenico Sammito
    :email: msacri@ibmb.csic.es / massimo.sammito@gmail.com

    :param graph:
    :return:
    """
    count = {}
    for node in graph:
        count[node] = 0
    for node in graph:
        for successor in graph[node]:
            count[successor] += 1

    ready = [node for node in graph if count[node] == 0]

    result = []
    while ready:
        node = ready.pop(-1)
        result.append(node)

        for successor in graph[node]:
            count[successor] -= 1
            if count[successor] == 0:
                ready.append(successor)

    return result


def robust_topological_sort(graph):
    """
    :author: Dr. Massimo Domenico Sammito
    :email: msacri@ibmb.csic.es / massimo.sammito@gmail.com

    :param graph:
    :return:
    """

    components = strongly_connected_components(graph)

    node_component = {}
    for component in components:
        for node in component:
            node_component[node] = component

    component_graph = {}
    for component in components:
        component_graph[component] = []

    for node in graph:
        node_c = node_component[node]
        for successor in graph[node]:
            successor_c = node_component[successor]
            if node_c != successor_c:
                component_graph[node_c].append(successor_c)

    return topological_sort(component_graph)


def findFarestAway(graf, node):
    """
    :author: Dr. Massimo Domenico Sammito
    :email: msacri@ibmb.csic.es / massimo.sammito@gmail.com

    :param graf:
    :param node:
    :return:
    """
    heap = Heap()
    for n in graf.keys():
        leng = len(shortestPath(graf, n, node))
        leng *= -1  # inverting the sign i will have results ordered by DESC instead of the ASC values
        heap.push(leng, n)
    value = heap.pop()
    n_deep = ((value[
                   0]) * -1) + 1  # i multiply for -1 to return to the original value and i add 1 because we track the number of nodes and not of edges
    farn = value[1]
    return farn, n_deep


def Dijkstra(G, start, end=None):
    """
    :author: Dr. Massimo Domenico Sammito
    :email: msacri@ibmb.csic.es / massimo.sammito@gmail.com

    :param G:
    :param start:
    :param end:
    :return:
    """
    D = {}  # dictionary of final distances
    P = {}  # dictionary of predecessors
    Q = priorityDictionary()  # est.dist. of non-final vert.
    Q[start] = 0

    for v in Q:
        D[v] = Q[v]
        if v == end: break

        for w in G[v]:
            vwLength = D[v] + 1  # G[v][w] #all the edges the have the same weight i put 1 so i can count the edges
            if w in D:
                if vwLength < D[w]:
                    raise ValueError, "Dijkstra: found better path to already-final vertex"
            elif w not in Q or vwLength < Q[w]:
                Q[w] = vwLength
                P[w] = v

    return (D, P)


def shortestPath(G, start, end):
    """
    :author: Dr. Massimo Domenico Sammito
    :email: msacri@ibmb.csic.es / massimo.sammito@gmail.com

    :param G:
    :param start:
    :param end:
    :return:
    """
    D, P = Dijkstra(G, start, end)
    Path = []
    while 1:
        Path.append(end)
        if end == start: break
        end = P[end]
    Path.reverse()
    return Path
