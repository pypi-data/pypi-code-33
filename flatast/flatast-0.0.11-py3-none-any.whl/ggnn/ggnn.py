#!/usr/bin/env python3
import ggnn
import argparse
import random
import torch
import torch.nn as nn
import torch.optim as optim
import sqlite3
import utils.data
from utils.model import GGNN
from utils.model import ClassPrediction
from utils.train_ggnn import train
from utils.test_ggnn import test
from utils.data import dataset
# from utils.data.dataset import MonoLanguageProgramData
from utils.data.dataset import ProgramData
from utils.data.dataloader import bAbIDataloader
from tensorboardX import SummaryWriter
import os
import os.path
import json
import pickle
import time
import sys
import tempfile
import hashlib
import flatbuffers
from tqdm import tqdm
import fast_
import fast_.Graph_
import fast_.Data_
import fast_.Data_.Anonymous3
from fast_ import Data, Graph, Element, Bugs, Log, Delta
from fast_.Data_ import Anonymous3
from fast_.Data import *
from fast_.Graph import *
from fast_.Element import *
from fast_.Bugs import *
from fast_.Log import *
from fast_.Delta import *
from fast_.Data_.Anonymous3 import *
from fast_.Graph import *
from fast_.Graph_.Unit import *
from fast_.Graph_.ContextGraph import *
from fast_.Graph_.ContextEdges import *
from fast_.Graph_.Edge import *
from fast_.Graph_.SymbolCandidate import *
from fast_.Graph_.NodeLabel import *
from fast_.Graph_.NodeType import *
from flatast.json_format import MessageToJson
import flatast.fast_pb2
import traceback
import pdb
import tqdm


parser = argparse.ArgumentParser()
parser.add_argument('--db', default="gitlog.db", help='the data sources')
parser.add_argument('--manualSeed', type=int, help='manual seed')
parser.add_argument('--label', default=None, help='assign the datasets to this class')
parser.add_argument('--n_classes', type=int, default=0, help='number of classes')
parser.add_argument('argv', nargs="*", help='add all the files if n_classes = 0')

# TODO: keep relevant options

# For feature engineering
parser.add_argument('--maps', action='store_true', default=True, help='maps node type to a consequetive number')
parser.add_argument('--map_folder', default=".", help='where to store the maps file')
parser.add_argument('--edgemaps', action='store_true', default=False, help='maps node type to a consequetive number')
############ Do not remove duplicated edges, which is found irrelevant to the performance
parser.add_argument('--dup', action='store_true', default=False, help='keep duplicated edges of the nodetypes')
############ Reinitialise the maps per class of instances. It leads to inappropriate performance for the classification
parser.add_argument('--localmaps', action='store_true', default=False, help='use local maps instead of global one')
## Use the occurrence of type instead of label to encode nodes
parser.add_argument('--occurrence', type=bool, default=True, help='use the <nodetype, occurrence> representation of nodes')
parser.add_argument('--mod', type=int, default=2, help='use the <nodetype, occurrence % mod> representation of nodes')
## Ignore the POSITION and COMMENT node types as noises to the input
parser.add_argument('--noposition', type=bool, default=True, help='ignore POSITION and COMMENT node types')
## Derive the last lexical use edges from adjacent occurrences of same node encodings
parser.add_argument('--lastuse', type=bool, default=False, help='add lastLexicalUse edges "3" between adjacent occurrence nodes  of the same node labels')
## Consider only the edge types of Child and NextToken
parser.add_argument('--syntaxonly', type=bool, default=False, help='output only syntactical edges, i.e. type "1" and "2"')
## Do not distinguish edge types
parser.add_argument('--noedgetype', type=bool, default=False, help='ignore edge types by replacing all edge types with "1"')
## Add label to the encoding of nodes
parser.add_argument('--labelling', type=bool, default=False, help='use the <nodetype, nodelabel> representation of nodes')
## Generate bidirectional edges
parser.add_argument('--bidirect', type=bool, default=False, help='make edges bidirectional')
## Add extra semantic edges as if they are syntactical
parser.add_argument('--mixing', type=bool, default=False, help='make semantic edges syntactical to allow for propagation')

# For learning
parser.add_argument('--workers', type=int, help='number of data loading workers', default=2)
parser.add_argument('--train_batch_size', type=int, default=32, help='input batch size')
parser.add_argument('--test_batch_size', type=int, default=32, help='input batch size')
parser.add_argument('--state_dim', type=int, default=5, help='GGNN hidden state size')
parser.add_argument('--n_steps', type=int, default=10, help='propogation steps number of GGNN')
parser.add_argument('--niter', type=int, default=150, help='number of epochs to train for')
parser.add_argument('--lr', type=float, default=0.01, help='learning rate')
parser.add_argument('--cuda', action='store_true', help='enables cuda')
parser.add_argument('--verbal', type=bool, default=True, help='print training info or not')
# parser.add_argument('--directory', default="program_data/cpp_babi_format_Sep-29-2018-0000006", help='program data')
parser.add_argument('--model_path', default="model/model.ckpt", help='path to save the model')
parser.add_argument('--n_hidden', type=int, default=50, help='number of hidden layers')
parser.add_argument('--size_vocabulary', type=int, default=59, help='maximum number of node types')
parser.add_argument('--is_training_ggnn', type=bool, default=True, help='Training GGNN or BiGGNN')
parser.add_argument('--log_path', default="" ,help='log path for tensorboard')
parser.add_argument('--epoch', type=int, default=0, help='epoch to test')

opt = parser.parse_args()
# print(opt)
if opt.manualSeed is None:
    opt.manualSeed = random.randint(1, 10000)
    # print("Random Seed: ", opt.manualSeed)
random.seed(opt.manualSeed)


def fbsEdges(builder, edges, type):
    typed_edges = edges[type]
    fbs_edges = []
    for e in typed_edges:
        EdgeStart(builder)
        EdgeAddNode1(builder, e[0])
        EdgeAddNode2(builder, e[1])
        fbs_edges.append(EdgeEnd(builder))
    N = len(fbs_edges)
    if type == "NextToken":
        ContextEdgesStartNextTokenVector(builder, N)
    elif type == "Child":
        ContextEdgesStartChildVector(builder, N)
    elif type == "LastWrite":
        ContextEdgesStartLastWriteVector(builder, N)
    elif type == "ReturnsTo":
        ContextEdgesStartReturnsToVector(builder, N)
    elif type == "LastUse":
        ContextEdgesStartLastUseVector(builder, N)
    elif type == "LastLexicalUse":
        ContextEdgesStartLastLexicalUseVector(builder, N)
    elif type == "ComputesFrom":
        ContextEdgesStartComputesFromVector(builder, N)
    for i in reversed(range(0, N)):
       builder.PrependUOffsetTRelative(fbs_edges[i])
    fbs_nodeTypes = builder.EndVector(N)
    return fbs_nodeTypes

def fbsContextEdges(builder, edges):
    #print(edges)
    if 'NextToken' in edges:
        nextToken = fbsEdges(builder, edges, 'NextToken')
    if 'Child' in edges:
        child = fbsEdges(builder, edges, 'Child')
    if 'LastLexicalUse' in edges:
        lastLexicalUse = fbsEdges(builder, edges, 'LastLexicalUse')
    if 'LastUse' in edges:
        lastUse = fbsEdges(builder, edges, 'LastUse')
    if 'LastWrite' in edges:
        lastWrite = fbsEdges(builder, edges, 'LastWrite')
    if 'ReturnsTo' in edges:
        returnsTo = fbsEdges(builder, edges, 'ReturnsTo')
    if 'ComputesFrom' in edges:
        computesFrom = fbsEdges(builder, edges, 'ComputesFrom')
    ContextEdgesStart(builder)
    if 'NextToken' in edges:
        ContextEdgesAddNextToken(builder, nextToken)
    if 'Child' in edges:
        ContextEdgesAddChild(builder, child)
    if 'LastLexicalUse' in edges:
        ContextEdgesAddLastLexicalUse(builder, lastLexicalUse)
    if 'LastUse' in edges:
        ContextEdgesAddLastUse(builder, lastUse)
    if 'LastWrite' in edges:
        ContextEdgesAddLastWrite(builder, lastWrite)
    if 'ReturnsTo' in edges:
         ContextEdgesAddReturnsTo(builder, returnsTo)
    if 'ComputesFrom' in edges:
         ContextEdgesAddComputesFrom(builder, computesFrom)
    return ContextEdgesEnd(builder)

def fbsNodeType(builder, key, value):
    fbs_key = int(key)
    fbs_value = builder.CreateString(value)
    NodeTypeStart(builder)
    NodeTypeAddNode(builder, fbs_key)
    NodeTypeAddType(builder, fbs_value)
    return NodeTypeEnd(builder)

def fbsNodeTypes(builder, node_types):
    nodeTypes = []
    for k in node_types.keys():
        nodeTypes.append(fbsNodeType(builder, k, node_types[k]))
    N = len(nodeTypes)
    ContextGraphStartNodeTypeVector(builder, N)
    for i in reversed(range(0, N)):
       builder.PrependUOffsetTRelative(nodeTypes[i])
    fbs_nodeTypes = builder.EndVector(N)
    return fbs_nodeTypes

def fbsNodeLabel(builder, key, value):
    fbs_key = int(key)
    fbs_value = builder.CreateString(value)
    NodeLabelStart(builder)
    NodeLabelAddNode(builder, fbs_key)
    NodeLabelAddLabel(builder, fbs_value)
    return NodeLabelEnd(builder)

def fbsNodeLabels(builder, node_labels):
    nodeLabels = []
    for k in node_labels.keys():
        nodeLabels.append(fbsNodeLabel(builder, k, node_labels[k]))
    N = len(nodeLabels)
    ContextGraphStartNodeLabelVector(builder, N)
    for i in reversed(range(0, N)):
       builder.PrependUOffsetTRelative(nodeLabels[i])
    fbs_nodeLabels = builder.EndVector(N)
    return fbs_nodeLabels

def fbsGraph(builder, graph):
    fbs_edges = fbsContextEdges(builder, graph["Edges"])
    fbs_nodeLabels = fbsNodeLabels(builder, graph["NodeLabels"])
    fbs_nodeTypes = fbsNodeTypes(builder, graph["NodeTypes"])

    ContextGraphStart(builder)
    ContextGraphAddEdges(builder, fbs_edges)
    ContextGraphAddNodeLabel(builder, fbs_nodeLabels)
    ContextGraphAddNodeType(builder, fbs_nodeTypes)
    fbs_graph = ContextGraphEnd(builder)
    return fbs_graph

def fbsSymbolCandidate(builder, symbolCandidate):
    symbolName = builder.CreateString(symbolCandidate['SymbolName'])
    SymbolCandidateStart(builder)
    SymbolCandidateAddSymbolDummyNode(builder, symbolCandidate["SymbolDummyNode"])
    SymbolCandidateAddSymbolName(builder, symbolName)
    SymbolCandidateAddIsCorrect(builder, symbolCandidate["IsCorrect"])
    symbolCandidates = SymbolCandidateEnd(builder)
    return symbolCandidates

def fbsSymbolCandidates(builder, symbolCandidates):
    candidates = []
    for s in symbolCandidates:
        candidates.append(fbsSymbolCandidate(builder, s))
    N = len(candidates)
    UnitStartSymbolCandidateVector(builder, N)
    for i in reversed(range(0, N)):
       builder.PrependUOffsetTRelative(candidates[i])
    fbs_candidates = builder.EndVector(N)
    return fbs_candidates

def fbsGatedGraph(builder, data):
    units = []
    for g in data:
        fbs_filename = builder.CreateString(g['filename'])
        fbs_slotTokenIdx = g['slotTokenIdx']
        fbs_SlotDummyNode = g['SlotDummyNode']
        fbs_Graph = fbsGraph(builder, g['ContextGraph'])
        fbs_SymbolCandidate = fbsSymbolCandidates(builder, g['SymbolCandidates'])
        UnitStart(builder)
        UnitAddFilename(builder, fbs_filename)
        UnitAddSlotTokenIdx(builder, fbs_slotTokenIdx)
        UnitAddGraph(builder, fbs_Graph)
        UnitAddSlotDummyNode(builder, fbs_SlotDummyNode)
        UnitAddSymbolCandidate(builder, fbs_SymbolCandidate)
        unit = UnitEnd(builder)
        units.append(unit)
    N = len(units)
    GraphStartUnitVector(builder, N)
    for i in tqdm(reversed(range(0, N))):
        builder.PrependUOffsetTRelative(units[i])
    fbs_unit = builder.EndVector(N)
    GraphStart(builder)
    GraphAddUnit(builder, fbs_unit)
    graph = GraphEnd(builder)
    DataStart(builder)
    DataAddRecordType(builder, graph)
    data = DataEnd(builder)
    return data

def jdefault(o):
    if o is None:
        return ' '
    if isinstance(o, set):
        return list(o)
    elif isinstance(o, Data):
        return jdefault(o.RecordType())
    elif isinstance(o, Anonymous3):
        return jdefault(o.Graph())
    elif isinstance(o, Graph):
        obj = []
        for i in range(0, o.UnitLength()):
            obj.append(jdefault(o.Unit(i)))
        return obj
    elif isinstance(o, Unit):
        obj = {}
        obj['filename'] = o.Filename()
        obj['slotTokenIdx'] = o.SlotTokenIdx()
        obj['ContextGraph'] = o.Graph()
        obj['SlotDummyNode'] = o.SlotDummyNode()
        vec = []
        for i in range(0, o.SymbolCandidateLength()):
            vec.append(jdefault(o.SymbolCandidate(i)))
        obj['SymbolCandidates'] = vec
        return obj
    elif isinstance(o, SymbolCandidate):
        obj = {}
        obj['SymbolDummyNode'] = o.SymbolDummyNode()
        obj['SymbolName'] = o.SymbolName()
        obj['IsCorrect'] = o.IsCorrect()
        return obj
    elif isinstance(o, ContextGraph):
        obj = {}
        obj['Edges'] = o.Edges()
        array = {}
        for i in range(0, o.NodeLabelLength()):
            nl = o.NodeLabel(i)
            array[nl.Node()] = nl.Label()
        obj['NodeLabels'] = array
        array = {}
        for i in range(0, o.NodeTypeLength()):
            nl = o.NodeType(i)
            array[nl.Node()] = nl.Type()
        obj['NodeTypes'] = array
        return obj
    elif isinstance(o, ContextEdges):
        obj = {}
        vec = []
        for i in range(0, o.NextTokenLength()):
            vec.append(jdefault(o.NextToken(i)))
        obj['NextToken'] = vec
        vec = []
        for i in range(0, o.ChildLength()):
            vec.append(jdefault(o.Child(i)))
        obj['Child'] = vec
        vec = []
        for i in range(0, o.LastLexicalUseLength()):
            vec.append(jdefault(o.LastLexicalUse(i)))
        obj['LastLexicalUse'] = vec
        vec = []
        for i in range(0, o.LastUseLength()):
            vec.append(jdefault(o.LastUse(i)))
        obj['LastUse'] = vec
        vec = []
        for i in range(0, o.LastWriteLength()):
            vec.append(jdefault(o.LastWrite(i)))
        obj['LastWrite'] = vec
        vec = []
        for i in range(0, o.ReturnsToLength()):
            vec.append(jdefault(o.ReturnsTo(i)))
        obj['ReturnsTo'] = vec
        vec = []
        for i in range(0, o.ComputesFromLength()):
            vec.append(jdefault(o.ComputesFrom(i)))
        obj['ComputesFrom'] = vec
        return obj
    elif isinstance(o, Edge):
        obj = [o.Node1(), o.Node2()]
        return obj
    elif isinstance(o, bytes):
        return str(o)
    elif isinstance(o, str):
        return o
    return o.__dict__

def add_edge_to_json(opt, edges, out, uniq_edges, src, edgetype, tgt):
    if src != tgt:
       e="%s %d %s\n" % (src, edgetype, tgt)
       if opt.dup:
          edges.append(e)
       else:
          uniq_edges.add(e)

def ggnn2json(data, map_folder='.'):
    graph = data.RecordType().Graph()
    if opt.maps or opt.edgemaps:
        maps = {}
    algorithms = []
    node2type = True
    train_graph = []
    test_graph = []
    for i in range(0, graph.UnitLength()):
        edges = []
        unit = graph.Unit(i)
        p = unit.Filename()
        t = os.path.dirname(p)
        t = os.path.dirname(t)
        if t in algorithms:
            algo = algorithms.index(t)
        else:
            algo = len(algorithms)
            algorithms.append(t)
        if (opt.maps or opt.edgemaps) and not opt.localmaps:
            input_basename, input_extension = os.path.splitext(p)
            maps_filename = "%s/maps%s.pkl" % (map_folder, input_extension.decode('ASCII'))
            if os.path.exists(maps_filename):
              with open(maps_filename, 'rb') as f:
                 maps = pickle.load(f)
        g = unit.Graph()
        edges = g.Edges()
        NT = g.NodeTypeLength()
        dict = {}
        if opt.occurrence:
            occurrence = {}
        uniq_edges = {}
        labels = {}
        for j in range(0, g.NodeLabelLength()):
            nl = g.NodeLabel(j)
            t = nl.Label()
            j1 = str(j + 1)
            labels[j1] = t
        ids = {}
        types = {}
        for j in range(0, g.NodeTypeLength()):
            nl = g.NodeType(j)
            t = str(nl.Type().decode('ASCII')) 
            j1 = str(j + 1)
            if t != 'POSITION' and t != 'COMMENT' and t != '271' and t != '6':
               types[j1] = t
               to = t
               if opt.labelling:
                  l = labels[j1]
                  if l != b'':
                     to = "%s:%s" % (t, l)
               elif opt.occurrence:
                  if not t in occurrence.keys():
                     occurrence[t] = 1 
                  else:
                     occurrence[t] = occurrence[t] + 1
                  to = "%s:%d" % (t, occurrence[t] % opt.mod)
               dict[j1] = to
               if opt.maps or opt.edgemaps:
                  if not to in maps:
                     maps[to] = str(1 + len(maps))
               if t == 'NAME':
                  ids[j1] = dict[j1] #labels[j1]
               if opt.edgemaps:
                  add_edge_to_json(opt, edges, uniq_edges, j1, 7 + int(maps[to]), j1)
            else:
               dict[j1] = 0
        for edgetype in range(1, 8):
            # out.write("====== %d\n" % edgetype)
            if edgetype == 1:
                n = edges.ChildLength()
            elif edgetype == 2:
                n = edges.NextTokenLength()
            elif edgetype == 3:
                n = edges.LastLexicalUseLength()
            elif edgetype == 4:
                n = edges.LastUseLength()
            elif edgetype == 5:
                n = edges.LastWriteLength()
            elif edgetype == 6:
                n = edges.ReturnsToLength()
            elif edgetype == 7:
                n = edges.ComputesFromLength()
            for j in range(0, n):
                if edgetype == 1:
                    e = edges.Child(j)
                elif edgetype == 2:
                    e = edges.NextToken(j)
                elif edgetype == 3:
                    e = edges.LastLexicalUse(j)
                elif edgetype == 4:
                    e = edges.LastUse(j)
                elif edgetype == 5:
                    e = edges.LastWrite(j)
                elif edgetype == 6:
                    e = edges.ReturnsTo(j)
                elif edgetype == 7:
                    e = edges.ComputesFrom(j)
                if opt.maps and not opt.edgemaps:
                   src = dict[str(e.Node1())]
                   tgt = dict[str(e.Node2())] 
                else:
                   src = str(e.Node1())
                   tgt = str(e.Node2())
                if src != 0 and tgt != 0:
                    if opt.maps:
                        s1 = maps[src]
                    else:
                        s1 = src
                    if opt.noedgetype:
                        edgetype = 1
                    else:
                        s2 = str(edgetype)
                    if opt.maps:
                        s3 = maps[tgt]
                    else:
                        s3 = tgt
                    if (s2 == '1' or s2 == '2') or not opt.syntaxonly:
                       add_edge_to_json(opt, edges, uniq_edges, s1, edgetype, s3)
                       if opt.bidirect:
                          add_edge_to_json(opt, edges, uniq_edges, s3, edgetype, s1)
                       if opt.mixing:
                          add_edge_to_json(opt, edges, uniq_edges, s1, 1, s3)
        if opt.lastuse:
            lastindex = {}
            lastuses = {}
            for j in range(0, g.NodeLabelLength()):
                nl = g.NodeLabel(j)
                t = nl.Label()
                j1 = str(j + 1)
                if t != b'' and t != b'int':
                   if t in lastindex.keys():
                      lastuses[j1] = lastindex[t]
                   lastindex[t] = j1
            for k, v in lastuses.items():
               if opt.maps:
                  t1 = dict[k]
                  t2 = dict[v]
               else:
                  t1 = str(k)
                  t2 = str(v)
               if t1 != '0' and t2 != '0' and t1 != 0 and t2 != 0:
                  if opt.maps:
                     add_edge_to_json(opt, edges, uniq_edges, maps[t2], 3, maps[t1])
                  else:
                     add_edge_to_json(opt, edges, uniq_edges, t2, 3, t1)
        out = {}
        out["graph"] = []
        for e in uniq_edges.keys():
            [src, edgetype, tgt] = e.split()
            out["graph"].append([int(src), int(edgetype), int(tgt)])
        out["target"] = []
        out["target"].append([i])
        out["node_features"] = []
        if i % 5 != 0:
            train_graph.append(out)
        else:
            test_graph.append(out)
        if (opt.maps or opt.edgemaps) and not opt.localmaps:
            # Don't assume the files in the same dataset are of the same language
            with open(maps_filename, 'wb') as f:
                pickle.dump(maps, f, 2)
    return [train_graph, test_graph]

def add_edge(opt, uniq_edges, src, edgetype, tgt):
    if src != tgt:
        e="%s %d %s" % (src, edgetype, tgt)
        # print(e)
        uniq_edges.add(e)

maps = {}

def ggnn2str(opt, unit, uniqe_edges, map_folder=".", algorithms=[], maps = {}):
    p = unit.Filename()
    t = os.path.dirname(p)
    t = os.path.dirname(t)
    uniq_edges = set()
    if t in algorithms:
        i = algorithms.index(t)
    else:
        i = len(algorithms)
        algorithms.append(t)
    if (opt.maps or opt.edgemaps) and not opt.localmaps:
        _, input_extension = os.path.splitext(p)
        maps_filename = "%s/maps%s.pkl" % (map_folder, input_extension.decode('ASCII'))
        if os.path.exists(maps_filename):
            with open(maps_filename, 'rb') as f:
                maps = pickle.load(f)
    g = unit.Graph()
    edges = g.Edges()

    dict = {}
    if opt.occurrence:
        occurrence = {}
    labels = {}
    for j in range(0, g.NodeLabelLength()):
        nl = g.NodeLabel(j)
        t = nl.Label()
        j1 = str(j + 1)
        labels[j1] = t
    ids = {}
    types = {}
    for j in range(0, g.NodeTypeLength()):
        nl = g.NodeType(j)
        t = str(nl.Type().decode('ASCII')) 
        j1 = str(j + 1)
        if t != 'POSITION' and t != 'COMMENT' and t != '271' and t != '6':
            types[j1] = t
            to = t
            if opt.labelling:
                l = labels[j1]
                if l != b'':
                    to = "%s:%s" % (t, l)
            elif opt.occurrence:
                if not t in occurrence.keys():
                    occurrence[t] = 1 
                else:
                    occurrence[t] = occurrence[t] + 1
                to = "%s:%d" % (t, occurrence[t] % opt.mod)
            dict[j1] = to
            if opt.maps or opt.edgemaps:
                if not to in maps:
                    maps[to] = str(1 + len(maps))
            if t == 'NAME':
                ids[j1] = dict[j1] #labels[j1]
            if opt.edgemaps:
                add_edge(opt, uniq_edges, j1, 7 + int(maps[to]), j1)
        else:
            dict[j1] = 0
    for edgetype in range(1, 8):
        if edgetype == 1:
            n = edges.ChildLength()
        elif edgetype == 2:
            n = edges.NextTokenLength()
        elif edgetype == 3:
            n = edges.LastLexicalUseLength()
        elif edgetype == 4:
            n = edges.LastUseLength()
        elif edgetype == 5:
            n = edges.LastWriteLength()
        elif edgetype == 6:
            n = edges.ReturnsToLength()
        elif edgetype == 7:
            n = edges.ComputesFromLength()
        for j in range(0, n):
            if edgetype == 1:
                e = edges.Child(j)
            elif edgetype == 2:
                e = edges.NextToken(j)
            elif edgetype == 3:
                e = edges.LastLexicalUse(j)
            elif edgetype == 4:
                e = edges.LastUse(j)
            elif edgetype == 5:
                e = edges.LastWrite(j)
            elif edgetype == 6:
                e = edges.ReturnsTo(j)
            elif edgetype == 7:
                e = edges.ComputesFrom(j)
            if opt.maps and not opt.edgemaps:
                src = dict[str(e.Node1())]
                tgt = dict[str(e.Node2())] 
            else:
                src = str(e.Node1())
                tgt = str(e.Node2())
            if src != 0 and tgt != 0:
                if opt.maps:
                    s1 = maps[src]
                else:
                    s1 = src
                if opt.noedgetype:
                    edgetype = 1
                else:
                    s2 = str(edgetype)
                if opt.maps:
                    s3 = maps[tgt]
                else:
                    s3 = tgt
                if (s2 == '1' or s2 == '2') or not opt.syntaxonly:
                    add_edge(opt, uniq_edges, s1, edgetype, s3)
                    if opt.bidirect:
                        add_edge(opt, uniq_edges, s3, edgetype, s1)
                    if opt.mixing:
                        add_edge(opt, uniq_edges, s1, 1, s3)
    if opt.lastuse:
        lastindex = {}
        lastuses = {}
        for j in range(0, g.NodeLabelLength()):
            nl = g.NodeLabel(j)
            t = nl.Label()
            j1 = str(j + 1)
            if t != b'' and t != b'int':
                if t in lastindex.keys():
                    lastuses[j1] = lastindex[t]
                lastindex[t] = j1
        for k, v in lastuses.items():
            if opt.maps:
                t1 = dict[k]
                t2 = dict[v]
            else:
                t1 = str(k)
                t2 = str(v)
            if t1 != '0' and t2 != '0' and t1 != 0 and t2 != 0:
                if opt.maps:
                    add_edge(opt, uniq_edges, maps[t2], 3, maps[t1])
                else:
                    add_edge(opt, uniq_edges, t2, 3, t1)
    return [maps_filename, uniq_edges]

def ggnn2txt(data, train, test, map_folder='.'):
    graph = data.RecordType().Graph()
    if opt.maps or opt.edgemaps:
        maps = {}
    algorithms = []
    for i in range(0, graph.UnitLength()):
        if (i % 5 != 0 and train != test):
            out = train
        else:
            out = test
        uniq_edges = {}
        unit = graph.unit(i)
        [maps_filename, _] = ggnn.ggnn2str(opt, unit, uniq_edges, map_folder, algorithms, maps)
        for e in uniq_edges.keys():
            out.write(e)
        out.write("? %d %s\n\n" % (i+1, p.decode('ASCII')))
        if (opt.maps or opt.edgemaps) and not opt.localmaps:
            # Don't assume the files in the same dataset are of the same language
            with open(maps_filename, 'wb') as f:
                pickle.dump(maps, f, 2)

def get_descendants(child, node):
    descendants = [node]
    for i in range(0, len(child)):
        edge = child[i]
        if edge[0] == int(node):
            descendants.extend(get_descendants(child, str(edge[1])))
    return descendants

def get_subgraph(graph, subnodes):
    idx = {}
    for i in range(0, len(subnodes)):
        idx[subnodes[i]] = i + 1
    subgraph = {}
    edges = graph["Edges"]
    subedges = {}
    child = edges["Child"]
    subchild = []
    nexttoken = edges["NextToken"]
    subnexttoken = []
    lastlexicaluse = edges["LastLexicalUse"]
    sublastlexicaluse = []
    lastuse = edges["LastUse"]
    sublastuse = []
    lastwrite = edges["LastWrite"]
    sublastwrite = []
    returnsto = edges["ReturnsTo"]
    subreturnsto = []
    computesfrom = edges["ComputesFrom"]
    subcomputesfrom = []
    nodetypes = graph["NodeTypes"]
    subnodetypes = {}
    nodelabels = graph["NodeLabels"]
    subnodelabels = {}
    for i in range(0, len(child)):
        edge = child[i]
        if str(edge[0]) in subnodes and str(edge[1]) in subnodes:
            subedge = []
            subedge.append(idx[str(edge[0])])
            subedge.append(idx[str(edge[1])])
            subchild.append(subedge)
    for i in range(0, len(nexttoken)):
        edge = nexttoken[i]
        if str(edge[0]) in subnodes and str(edge[1]) in subnodes:
            subedge = []
            subedge.append(idx[str(edge[0])])
            subedge.append(idx[str(edge[1])])
            subnexttoken.append(subedge)
    for i in range(0, len(lastlexicaluse)):
        edge = lastlexicaluse[i]
        if str(edge[0]) in subnodes and str(edge[1]) in subnodes:
            subedge = []
            subedge.append(idx[str(edge[0])])
            subedge.append(idx[str(edge[1])])
            sublastlexicaluse.append(subedge)
    for i in range(0, len(lastuse)):
        edge = lastuse[i]
        if str(edge[0]) in subnodes and str(edge[1]) in subnodes:
            subedge = []
            subedge.append(idx[str(edge[0])])
            subedge.append(idx[str(edge[1])])
            sublastuse.append(subedge)
    for i in range(0, len(lastwrite)):
        edge = lastwrite[i]
        if str(edge[0]) in subnodes and str(edge[1]) in subnodes:
            subedge = []
            subedge.append(idx[str(edge[0])])
            subedge.append(idx[str(edge[1])])
            sublastwrite.append(subedge)
    for i in range(0, len(returnsto)):
        edge = returnsto[i]
        if str(edge[0]) in subnodes and str(edge[1]) in subnodes:
            subedge = []
            subedge.append(idx[str(edge[0])])
            subedge.append(idx[str(edge[1])])
            subreturnsto.append(subedge)
    for i in range(0, len(computesfrom)):
        edge = computesfrom[i]
        if str(edge[0]) in subnodes and str(edge[1]) in subnodes:
            subedge = []
            subedge.append(idx[str(edge[0])])
            subedge.append(idx[str(edge[1])])
            subcomputesfrom.append(subedge)
    for k, v in nodetypes.items():
        if k in subnodes:
            subnodetypes[str(idx[k])] = v
    for k, v in nodelabels.items():
        if k in subnodes:
            subnodelabels[str(idx[k])] = v
    subedges["Child"] = subchild
    subedges["NextToken"] = subnexttoken
    subedges["LastLexicalUse"] = sublastlexicaluse
    subedges["LastUse"] = sublastuse
    subedges["LastWrite"] = sublastwrite
    subedges["ReturnsTo"] = subreturnsto
    subedges["ComputesFrom"] = subcomputesfrom
    subgraph["Edges"] = subedges
    subgraph["NodeTypes"] = subnodetypes
    subgraph["NodeLabels"] = subnodelabels
    return subgraph

def get_subgraphs(filename, graph):
    data = []
    edges = graph["Edges"]
    child = edges["Child"]
    nodelabels=graph["NodeLabels"]
    for k, v in nodelabels.items():
        subnodes = get_descendants(child, k)
        #
        # Each candidate should have at least 10 nodes
        #
        if len(subnodes) > 10:
            subgraph = get_subgraph(graph, subnodes)
            subdata = {}
            input_basename, input_extension = os.path.splitext(filename)
            subdata["filename"] = '%s-%s%s' % (input_basename.decode('ASCII'), k, input_extension.decode('ASCII'))
            subdata["ContextGraph"] = subgraph
            subdata["slotTokenIdx"] = 0
            subdata["SlotDummyNode"] = 0
            subdata["SymbolCandidates"] = []
            data.append(subdata)
    return data
  
def generate_subgraphs(filename, graph, out):
    with open('/tmp/t.json', 'w') as json_out:
        json.dump(graph, json_out, default=jdefault)
        json_out.close()
    with open('/tmp/t.json', 'r') as json_in:
        graph_data = json.load(json_in)
        json_in.close()
    data = get_subgraphs(filename, graph_data)
    #json.dump(data, json_out)
    builder = flatbuffers.Builder(0)
    fbs_graph = fbsGatedGraph(builder, data)
    builder.Finish(fbs_graph)
    with open('/tmp/tt.fbs', 'wb') as fbs_out:
        buf = builder.Output()
        fbs_out.write(buf)
        fbs_out.close()
    with open('/tmp/tt.fbs', 'rb') as fbs_in:
        buf = fbs_in.read()
        buf = bytearray(buf)
        fbs_graph = Graph.GetRootAsGraph(buf, 0)
        fbs_in.close()
    ggnn2txt(fbs_graph, out, out)

#
# generate a graph for the AST of each node
#
def ggnn2txt_test(graph, test):
    if opt.maps and not opt.localmaps:
        maps = {}
        if os.path.exists('maps.pkl'):
            with open('maps.pkl', 'rb') as f:
                 maps = pickle.load(f)
    algorithms = []
    node2type = True
    for i in trange(0, graph.UnitLength()):
        out = test
        unit = graph.Unit(i)
        p = unit.Filename()
        t = os.path.dirname(p);
        t = os.path.dirname(t);
        if t in algorithms:
            i = algorithms.index(t)
        else:
            i = len(algorithms)
            algorithms.append(t)
        g = unit.Graph()
        edges = g.Edges()
        array = {}
        NT = g.NodeTypeLength()
        dict = {}
        for j in range(0, g.NodeTypeLength()):
            nl = g.NodeType(j)
            j1 = str(j + 1)
            dict[j1] = str(nl.Type())
            if opt.maps:
                if not str(nl.Type()) in maps:
                    maps[str(nl.Type())] = str(1 + len(maps))
        generate_subgraphs(p, g, out)
    if not opt.localmaps:
        with open('maps.pkl', 'wb') as f:
            pickle.dump(maps, f, 2)



def get_temp_filename(ext):
    """
    Get a temporary file anme with the extension name `ext`
        ext - extension name
    """
    f = tempfile.mkstemp(suffix=ext)[1]
    return f

def fastReadData(db, filename):
    """
    Use external "fast" commands to parse the input into flatAST binary data
    """
    temp_filename = get_temp_filename(".fbs")
    f2 = open(temp_filename, 'r')
    seq = f2.read()
    f2.close()
    os.system("fast -p %s %s" % (filename, temp_filename))
    f2 = open(temp_filename, 'rb')
    tree_buf = bytearray(f2.read())
    tree = Data.GetRootAsData(tree_buf, 0)
    f2.close()
    os.system("fast -S -G %s %s" % (filename, temp_filename))
    f2 = open(temp_filename, 'rb')
    graph_buf = bytearray(f2.read())
    graph = Data.GetRootAsData(graph_buf, 0)
    f2.close()
    os.remove(temp_filename)
    return [seq, tree_buf, tree, graph_buf, graph]

def readRawData(db, filename):
    """ the data is not in the database yet, read it into sequence, tree, or graph """
    seq = None
    tree_buf = None
    tree = None
    graph_buf = None
    graph = None
    _, input_extension = os.path.splitext(filename)
    if input_extension == ".fbs":      
        f = open(filename, 'rb')
        buf = f.read()
        f.close()
        data = Data.GetRootAsData(buf, 0)
        if not data is None and not data.RecordType() is None:
            if not data.RecordType().Graph() is None:
                graph_buf = buf
                graph = data
            if not data.RecordType().Element() is None:
                tree_buf = buf
                tree = data
                temp_filename = get_temp_filename(".java")
                os.system("fast -C %s > %s" % (filename, temp_filename))
                f2 = open(temp_filename, 'r')
                seq = f2.read()
                f2.close()
            return [seq, tree_buf, tree, graph_buf, graph]
    return fastReadData(db, filename)

def found_id(db, id, hash):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c = c.execute("SELECT id FROM units WHERE id = ? OR hash = ? ", (id, hash))
    rows = c.fetchone()
    conn.close()
    return not rows is None

def readData(db, filename, id=""):
    """
    Read file as GGNN data, and save into flatAST with the hash of the original file, 
    if it is not yet in the database. On the other hand, if the file is in the database, 
    and its hash is different from the stored hash, update the record with the new data.
    """
    # print("++++++++++ %s"  % filename)
    if not os.path.exists(filename):
        print("[WARN] The file %s doesn't exist." % filename)
        return None

    if id == "":
        id = filename
        
    file = open(id, 'rb')
    seq = file.read()
    hash = hashlib.sha256(seq).hexdigest()
    file.close()

    tree_buf = None
    tree = None
    graph_buf = None
    graph = None
    if not found_id(db, id, hash):
        [_, tree_buf, tree, graph_buf, graph] = readRawData(db, filename)
        """ now the data should be stored into the database """
        if not graph is None and not tree is None:
            if not found_id(db, id, hash):
                print("INSERT INTO units (id, seq, tree, graph, hash)")
                conn = sqlite3.connect(db)                
                conn.execute("INSERT INTO units (id, seq, tree, graph, hash) VALUES (?, ?, ?, ?, ?)", (id, seq, sqlite3.Binary(tree_buf), sqlite3.Binary(graph_buf), hash) )
                conn.commit()
                conn.close()
        if not graph is None:
            if not found_id(db, id, hash):
                print("INSERT INTO units (id, seq, graph, hash)")
                conn = sqlite3.connect(db)
                conn.execute("INSERT INTO units (id, seq, graph, hash) VALUES (?, ?, ?, ?)", (id, seq, sqlite3.Binary(graph_buf), hash) )
                conn.commit()
                conn.close()
        if not tree is None:
            if not found_id(db, id, hash):
                print("INSERT INTO units (id, seq, tree, hash)")                
                conn = sqlite3.connect(db)
                conn.execute("INSERT INTO units (id, seq, tree, hash) VALUES (?, ?, ?, ?)", (id, seq, sqlite3.Binary(tree_buf), hash) )
                conn.commit()
                conn.close()
    else:
        conn = sqlite3.connect(db)
        c = conn.cursor()
        c = c.execute("SELECT id, hash FROM units WHERE id = ? OR hash = ?", (id, hash))
        rows = c.fetchone()
        c.close()
        conn.close()
        if not rows is None and id == rows[0] and hash != rows[1]:
            """ update the data record """
            [seq, tree_buf, tree, graph_buf, graph] = readRawData(db, filename)
            if not graph is None:
                print("UPDATE units SET graph")
                conn = sqlite3.connect(db)
                conn.execute("UPDATE units SET graph = ?, hash = ? WHERE id = ?", 
                    (sqlite3.Binary(graph_buf), hash, id))
                conn.commit()
                conn.close()
            if not tree is None:
                print("UPDATE units SET tree")
                conn = sqlite3.connect(db)
                conn.execute("UPDATE units SET tree = ?, hash = ? WHERE id = ?", 
                    (sqlite3.Binary(tree_buf), hash, id))
                conn.commit()
                conn.close()
            if not seq is None:
                print("UPDATE units SET seq")
                conn = sqlite3.connect(db)
                conn.execute("UPDATE units SET seq = ?, hash = ? WHERE id = ?", 
                    (seq, hash, id))
                conn.commit()
                conn.close()
        elif not rows is None and id != rows[0] and hash == rows[1]:
            id = rows[0]
    return [id, seq, tree_buf, tree, graph_buf, graph]

def add_to_oracle(db, id, label=None):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c = c.execute("SELECT label FROM classes WHERE unit_id = ?", (id, ))
    rows = c.fetchone()
    c.close()
    conn.close()

    if label is None:
        """ default label is computed from the path """
        label = os.path.basename(os.path.dirname(id))
        #if label == "":
        #    print("TO TEST => %s " % label)
    if not rows is None:
        old_label = rows[0]
        if old_label != label:
            conn = sqlite3.connect(db)
            conn.execute("UPDATE classes SET label = ? WHERE unit_id = ?", (label, id) )
            conn.commit()
        return label
    conn = sqlite3.connect(db)
    conn.execute("INSERT INTO classes (unit_id, label) VALUES (?, ?)", (id, label) )
    conn.commit()
    conn.close()
    return label

def prepare_datasets_for_learning(db, splitting = True):
    """
    For each class, split instances into three sets of 6/2/2 per 10 elements
    and mark them as in the modes of training, testing and validating respectively.
    """
    """ Clean up the learning instances table """
    conn = sqlite3.connect(db)
    conn.execute("DELETE FROM learning")
    conn.commit()
    """ Select the classes """
    c = conn.cursor()
    c = c.execute("SELECT label, count(unit_id) FROM classes GROUP BY label")
    classes = c.fetchall()
    c.close()
    conn.close()
    conn = sqlite3.connect(db)
    units = []
    class_names = []
    for i in range(0, len(classes)):
        """ randomly split instances in the class by 6/2/2 or 7/3/0 ratio into training, 
        testing, validating mode """
        n = classes[i][1]
        # print("Group %s: %d" % (classes[i][0], n))
        if not classes[i][0] == "":
            class_names.append(classes[i][0])
        c = conn.cursor()
        c = c.execute("SELECT unit_id FROM classes WHERE label = ?", (classes[i][0],))
        ids = c.fetchall()
        c.close()
        if n > 0:
            x = random.sample(range(0,n), n)
            for k in range(0, len(ids)):
                j = float(10 * x[k]) / len(ids)
                if classes[i][0] == "":
                    mode = 2       # Testing
                    units.append(ids[k][0])
                else:
                    if splitting and j < 7.0:
                        mode = 0   # Training
                    else:
                        mode = 1   # Validating
                # if j < 6.0:
                #     mode = 0   # Training
                # elif j < 8.0:
                #     mode = 1   # Validating
                # else:
                #     mode = 2   # Testing
                conn.execute("INSERT INTO learning (unit_id, mode) VALUES (?, ?)", (ids[k][0], mode))
                conn.commit()
    conn.close()
    return units, class_names

def prepare_logs_for_training(log_path):
    if log_path != "":
        previous_runs = os.listdir(log_path)
        if len(previous_runs) == 0:
            run_number = 1
        else:
            run_number = max([int(s.split("run-")[1]) for s in previous_runs]) + 1
        writer = SummaryWriter("%s/run-%03d" % (log_path, run_number))
    else:
        writer = None
    return writer

def load_model_at_epoch(opt, opt_model_path, opt_epoch):
    filename = "{}.{}".format(opt_model_path, opt_epoch)
    epoch = opt_epoch
    if os.path.exists(filename):
        dirname = os.path.dirname(filename)
        basename = os.path.basename(filename)
        epochs = os.listdir(dirname)
        if len(epochs) > 0:
            for s in epochs:
                if s.startswith(basename) and basename != s:
                    x = s.split(os.extsep)
                    e = x[len(x) - 1]
                    epoch = max(epoch, int(e))
        if epoch != -1:
            # print("Using No. {} of the saved models...".format(epoch))
            filename = "{}.{}".format(opt_model_path, epoch)
        net = torch.load(filename)
    else:
        net = GGNN(opt)
        net.double()
    return epoch, net

def delete_validation_data(db):
    conn = sqlite3.connect(db)
    conn.execute("DELETE FROM units WHERE id IN (SELECT unit_id FROM classes WHERE label='') ")
    conn.execute("DELETE FROM classes WHERE label=''")
    conn.commit()
    conn.close()

def main():
    """
    We store data into the three tables:
    -  units (id, seq, tree, graph, hash) index the data to be classified by a unique id, where data
            can be any structure in terms of sequence (seq), abstract syntax tree (tree), and/or gated graphs (graph). 
            In our case, these structures follow the flatAST schema. 
            The hash is sha256sum of the data's original content. In case the file is updated 
            with a hash different from the stored hash, we will update the record. 
    -  classes (unit_id, label) is the oracle of classifications of these units
    -  learning (unit_id, mode) is the data used for training, testing, and validation,
            during the machine learning process.
    """

    try:
        start = time.time()
        conn = sqlite3.connect(opt.db)
        conn.execute('''CREATE TABLE IF NOT EXISTS units(id TEXT PRIMARY KEY, seq TEXT, tree BLOB, graph BLOB, hash TEXT)''')
        conn.execute('''CREATE TABLE IF NOT EXISTS classes(unit_id TEXT PRIMARY KEY, label TEXT)''')
        conn.execute('''CREATE TABLE IF NOT EXISTS learning(unit_id TEXT PRIMARY KEY, mode INTEGER)''')
        conn.close()

        delete_validation_data(opt.db)
        for i in range(0, len(opt.argv)):  # adding data 
            # print("adding the file %s ..." % opt.argv[i])
            [id, seq, tree_buf, tree, graph_buf, graph] = readData(opt.db, opt.argv[i])
            print(id)
            if id != opt.argv[i]:
                print("The file %s is already in the dataset as %s" % (opt.argv[i], id))
            else:
                add_to_oracle(opt.db, id, opt.label)
        torch.manual_seed(opt.manualSeed)
        if opt.cuda:
            torch.cuda.manual_seed_all(opt.manualSeed)

        units, classes = prepare_datasets_for_learning(opt.db)

        if len(opt.argv) == 0:
            train_dataset = ProgramData(opt, opt.map_folder, opt.size_vocabulary, opt.db, 0, opt.n_classes)
            train_dataloader = bAbIDataloader(train_dataset, batch_size=opt.train_batch_size, shuffle=True, num_workers=2)

            valid_dataset = ProgramData(opt, opt.map_folder, opt.size_vocabulary, opt.db, 1, opt.n_classes)
            valid_dataloader = bAbIDataloader(valid_dataset, batch_size=opt.test_batch_size, shuffle=True, num_workers=2)
            opt.n_edge_types = train_dataset.n_edge_types
            opt.n_node = train_dataset.n_node

        else:
            test_dataset = ProgramData(opt, opt.map_folder, opt.size_vocabulary, opt.db, 2, opt.n_classes)
            if len(test_dataset) > 0:
                test_dataloader = bAbIDataloader(test_dataset, batch_size=opt.test_batch_size, shuffle=True, num_workers=2)
            opt.n_edge_types = test_dataset.n_edge_types
            opt.n_node = test_dataset.n_node

        opt.annotation_dim = 1  # for bAbI
        epoch, net = load_model_at_epoch(opt, opt.model_path, opt.epoch)
        criterion = nn.CrossEntropyLoss()
        if opt.cuda:
            net.cuda()
            criterion.cuda()
        optimizer = optim.Adam(net.parameters(), lr=opt.lr)

        if len(opt.argv) == 0:
            # print("Training and validating ...")
            writer = prepare_logs_for_training(opt.log_path)
            for epoch in range(epoch+1, epoch + opt.niter):
                train(epoch, train_dataloader, net, criterion, optimizer, opt, writer)
                if not opt.is_training_ggnn:
                    test(valid_dataloader, net, criterion, optimizer, opt, units, classes, True)
            test(valid_dataloader, net, criterion, optimizer, opt, units, classes, True)
            if not writer is None:
                writer.close()
        else:
            if len(test_dataset) > 0:
                # print("Testing...")
                test(test_dataloader, net, criterion, optimizer, opt, units, classes, False)
        end = time.time()
        print(end - start)
        os._exit(0)
    except:
        typ, value, tb = sys.exc_info()
        traceback.print_exc()
        pdb.post_mortem(tb)

if __name__ == "__main__":
    main()
