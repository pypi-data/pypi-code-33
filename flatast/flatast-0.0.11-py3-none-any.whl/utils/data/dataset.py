import numpy as np
import os
from os import listdir
from os.path import isfile, join
import collections
import re
from tqdm import trange
import random
import pickle
import pyarrow
import sqlite3
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
import flatast.json_format
import flatast.fast_pb2
import utils

def load_graphs_from_file(file_name):
    data_list = []
    edge_list = []
    target_list = []    
    with open(file_name,'r') as f:
        for line in f:
            if len(line.strip()) == 0:
                data_list.append([edge_list,target_list])
                edge_list = []
                target_list = []
            else:
                digits = []
                line_tokens = line.split(" ")

                if line_tokens[0] == "?":
                    for i in range(1, len(line_tokens)):
                        
                        digits.append(int(line_tokens[i]))
                    target_list.append(digits)
                else:
                    for i in range(len(line_tokens)):
                        digits.append(int(line_tokens[i]))
                    edge_list.append(digits)
    return data_list

def load_program_graphs_from_directory(directory,is_train=True,n_classes=3, data_percentage=1.0):
    data_list = []
    if is_train == True:
            dir_path =  os.path.join(directory,"train")
    else:
            dir_path =  os.path.join(directory,"test")
    filenames = []
    for f in listdir(dir_path):
        if isfile(join(dir_path, f)):
            filenames.append(f)
    int_filenames = [int(re.search('_(.*).txt', x).group(1)) for x in filenames]
    ordered_filenames = sorted(int_filenames)
    lookup = {}
    for i in range(1, 1+len(ordered_filenames)):
        if is_train == True:
            lookup[i] = join(dir_path, "train_%s.txt" % str(ordered_filenames[i-1]))
        else:
            lookup[i] = join(dir_path, "test_%s.txt" % str(ordered_filenames[i-1]))
    for i in trange(1, 1+n_classes):
        path = lookup[i]
        print(path)
        label = i
        data_list_class_i = []
        edge_list_class_i = []
        target_list_class_i = []

        with open(path,'r') as f:
            for line in f: 
                if len(line.strip()) == 0:

                    data_list_class_i.append([edge_list_class_i,target_list_class_i])
                    edge_list_class_i = []
                    target_list_class_i = []
                else:
                    digits = []
                    line_tokens = line.split(" ")
                    
                    if line_tokens[0] == "?":

                        target_list_class_i.append([label])
                    else:
                        for j in range(len(line_tokens)):
                            digits.append(int(line_tokens[j]))
                        edge_list_class_i.append(digits)

        if data_percentage < 1.0:
            print("Cutting down " + str(data_percentage) + " of all data......")
            slicing = int(len(data_list_class_i)*data_percentage)
            print("Remaining data : " + str(slicing) + "......")
            data_list_class_i = data_list_class_i[:slicing]

        data_list.extend(data_list_class_i)

    return data_list

def load_program_graphs_from_db(opt, db, map_folder=".", mode=0, n_classes=3):
    """
    Load the program graph data from the database db
    """       
    """ Select the classes """
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c = c.execute("SELECT c.label, count(c.unit_id) FROM classes c, learning l WHERE c.unit_id = l.unit_id AND l.mode = ? GROUP BY c.label", (mode,))
    classes = c.fetchall()
    c.close()
    conn.close()
    conn = sqlite3.connect(db)
    data_list = []
    algorithms = []
    maps = {} 
    maps_filename = None
    # print("======> %d" % len(classes))
    for i in range(0, len(classes)):
        label = classes[i][0]
        n_instance = classes[i][1]
        if n_instance == 0:
            continue
        conn = sqlite3.connect(db)
        c = conn.cursor()
        c = c.execute("SELECT u.graph, u.id, c.label, l.mode FROM units u, classes c, learning l WHERE u.id = c.unit_id AND c.unit_id = l.unit_id AND l.mode = ? AND c.label = ?", (mode, label))
        rows = c.fetchall()
        c.close()
        conn.close()
        n_instance = len(rows)
        edge_list_class_i = []
        target_list_class_i = []
        data_list_class_i = []
        # print("======> %d" % n_instance)
        for j in range(0, n_instance):
            buf = rows[j][0]
            if rows[j][3] == 2:
                print("%s: to test" % rows[j][1])
            elif rows[j][3] == 0:
                print("%s -> %s: to train" % (rows[j][1], rows[j][2]))
            else:
                print("%s -> %s: to validate" % (rows[j][1], rows[j][2]))
            data = Data.GetRootAsData(buf, 0)
            graph = data.RecordType().Graph()
            if not graph is None:  # in case the graph has been correctly rendered
                for k in range(0, graph.UnitLength()):
                    uniq_edges = set()
                    unit = graph.Unit(k)
                    from ggnn import ggnn
                    (maps_filename, uniq_edges) = ggnn.ggnn2str(opt, unit, uniq_edges, map_folder, algorithms, maps)
                    for e in set(uniq_edges):
                        digits = e.split()
                        edge = []
                        for l in range(0, len(digits)):
                            edge.append(int(digits[l]))
                        edge_list_class_i.append(edge)
                target_list_class_i.append([i])
                data_list_class_i.append([edge_list_class_i,target_list_class_i])
        data_list.extend(data_list_class_i)
    if (opt.maps or opt.edgemaps) and not opt.localmaps and not maps_filename is None:
        # Don't assume the files in the same dataset are of the same language
        with open(maps_filename, 'wb') as f:
            pickle.dump(maps, f, 2)
    # print("======> %d" % len(data_list))
    return data_list

def find_max_edge_id(data_list):
    max_edge_id = 0
    for data in data_list:
        edges = data[0]
        for item in edges:
            if item[1] > max_edge_id:
                max_edge_id = item[1]
    return max_edge_id

def find_max_node_id(data_list):
    max_node_id = 0
    for data in data_list:
        edges = data[0]
        for item in edges:
            if item[0] > max_node_id:
                max_node_id = item[0]
            if item[2] > max_node_id:
                max_node_id = item[2]
    return max_node_id

def find_max_task_id(data_list):
    max_node_id = 0
    for data in data_list:
        target = data[1]
        for item in target:
            if item[0] > max_node_id:
                max_node_id = item[0]
    return max_node_id

def convert_program_data(data_list, n_annotation_dim, n_nodes):
    # n_nodes = find_max_node_id(data_list)
    class_data_list = []

    for item in data_list:
        edge_list = item[0]
        target_list = item[1]
        for target in target_list:
            task_type = target[0]
            task_output = target[-1]
            annotation = np.zeros([n_nodes, n_annotation_dim])   
            for edge in edge_list:
                src_idx = edge[0]
                if src_idx < len(annotation):
                    annotation[src_idx-1][0] = 1        
        class_data_list.append([edge_list, annotation, task_output])
    return class_data_list

def convert_program_data_into_group(data_list, n_annotation_dim, n_nodes, n_classes):
    class_data_list = []

    for i in range(n_classes):
        class_data_list.append([])

    for item in data_list:
        edge_list = item[0]
        target_list = item[1]
        for target in target_list:
            class_output = target[-1]
            annotation = np.zeros([n_nodes, n_annotation_dim])   
            for edge in edge_list:
                src_idx = int(edge[0])
                if src_idx < len(annotation):
                    annotation[src_idx-1][0] = 1
            class_data_list[class_output-1].append([edge_list, annotation, class_output])
    return class_data_list

def create_adjacency_matrix(edges, n_nodes, n_edge_types):
    a = np.zeros([n_nodes, n_nodes * n_edge_types * 2])

    for edge in edges:
        src_idx = edge[0]
        e_type = edge[1]
        tgt_idx = edge[2]
    
        if tgt_idx < len(a):
            a[tgt_idx-1][(e_type - 1) * n_nodes + src_idx - 1] =  1
        if src_idx <len(a):
            a[src_idx-1][(e_type - 1 + n_edge_types) * n_nodes + tgt_idx - 1] =  1
    return a

class MonoLanguageProgramData():   
    def __init__(self, size_vocabulary, path, is_train, n_classes=3,data_percentage=1.0):
        base_name = os.path.basename(path)
        if is_train:
            saved_input_filename = "%s/%s-%d-train.pkl" % (path, base_name, n_classes)
        else:
            saved_input_filename = "%s/%s-%d-test.pkl" % (path, base_name, n_classes)
        if os.path.exists(saved_input_filename): 
            input_file = open(saved_input_filename, 'rb')
            buf = input_file.read()
            all_data = pyarrow.deserialize(buf)
            input_file.close()
        else:
            all_data = load_program_graphs_from_directory(path,is_train,n_classes,data_percentage)
            all_data = np.array(all_data)[0:len(all_data)]
            buf = pyarrow.serialize(all_data).to_buffer()
            out = pyarrow.OSFile(saved_input_filename, 'wb')
            out.write(buf)
            out.close()
    
        if is_train == True:
            print("Number of all training data : " + str(len(all_data)))
        else:
            print("Number of all testing data : " + str(len(all_data)))
        self.n_edge_types =  find_max_edge_id(all_data)
        # print("Edge types : " + str(self.n_edge_types))
        max_node = find_max_node_id(all_data)
        print("Max node id : " + str(max_node))
        self.n_node = size_vocabulary
        
        all_data = convert_program_data(all_data,1, self.n_node)

        self.data = all_data
    
    def __getitem__(self, index):
        
        am = create_adjacency_matrix(self.data[index][0], self.n_node, self.n_edge_types)
        # annotation = self.data[index][1]
        target = self.data[index][2] - 1
        return am, target

    def __len__(self):
        return len(self.data)

class ProgramData():   
    def __init__(self, opt, map_folder, size_vocabulary, db, mode, n_classes=3):
        all_data = load_program_graphs_from_db(opt, db, map_folder, mode, n_classes)
        all_data = np.array(all_data)[0:len(all_data)]
        if False:
            if mode == 0:
                print("Number of all training data : " + str(len(all_data)))
            elif mode == 1:
                print("Number of all validating data : " + str(len(all_data)))
            else:
                print("Number of all testing data : " + str(len(all_data)))
        self.n_edge_types =  find_max_edge_id(all_data)
        max_node = find_max_node_id(all_data)
        # print("Max node id : " + str(max_node))
        self.n_node = size_vocabulary        
        # print("======> %d" % len(all_data))
        all_data = convert_program_data(all_data, 1, self.n_node)
        # print("======> %d" % len(all_data))
        self.data = all_data
    
    def __getitem__(self, index):        
        am = create_adjacency_matrix(self.data[index][0], self.n_node, self.n_edge_types)
        # annotation = self.data[index][1]
        target = self.data[index][2]
        return am, target

    def __len__(self):
        return len(self.data)

class CrossLingualProgramData():

    def __init__(self, size_vocabulary, left_path, right_path, is_train, loss, n_classes=3, data_percentage=1):
        
        self.loss = loss
        left_all_data = load_program_graphs_from_directory(left_path,is_train,n_classes,data_percentage)
        right_all_data = load_program_graphs_from_directory(right_path,is_train,n_classes,data_percentage)

        left_all_data = np.array(left_all_data)[0:len(left_all_data)]
        right_all_data = np.array(right_all_data)[0:len(right_all_data)]
    
        if is_train == True:
            print("Number of all left training data : " + str(len(left_all_data)))
            print("Number of all right training data : " + str(len(right_all_data)))
        else:
            print("Number of all left testing data : " + str(len(left_all_data)))
            print("Number of all right testing data : " + str(len(right_all_data)))

        self.n_edge_types =  find_max_edge_id(left_all_data)
        self.n_node = size_vocabulary
        max_left_node = find_max_node_id(left_all_data)
        max_right_node = find_max_node_id(right_all_data)

        print("Left max node id : " + str(max_left_node))
        print("Right max node id : " + str(max_right_node))

        left_all_data_by_classes = convert_program_data_into_group(left_all_data,1, self.n_node, n_classes)

        right_all_data_by_classes = convert_program_data_into_group(right_all_data,1, self.n_node, n_classes)

        pairs_1 = []
        pairs_0 = []

        for i, left_class in tqdm(enumerate(left_all_data_by_classes)):
            right_class = right_all_data_by_classes[i]

            remaining_right_class = []

            for j, other_right_class in enumerate(right_all_data_by_classes):
                if j != i:
                    remaining_right_class.extend(other_right_class)

            if len(left_class) > len(right_class):
                left_class = left_class[:len(right_class)]
            
            for k, left_data_point in enumerate(left_class):
                righ_data_point = right_class[k]
                pairs_1.append((left_data_point,righ_data_point))
                pairs_0.append((left_data_point, random.choice(remaining_right_class)))

        print("Number of all 1 pairs data : " + str(len(pairs_1)))
        print("Number of all 0 pairs data : " + str(len(pairs_0)))
        data = []
        data.extend(pairs_1)
        data.extend(pairs_0)
        random.shuffle(data)
        self.data = data

    
    def __getitem__(self, index):
        
        left_data_point = self.data[index][0]
        right_data_point = self.data[index][1]

        left_am = create_adjacency_matrix(left_data_point[0], self.n_node, self.n_edge_types)
        right_am = create_adjacency_matrix(right_data_point[0], self.n_node, self.n_edge_types)

        left_annotation = left_data_point[1]
        right_annotation = right_data_point[1]

        if left_data_point[2] == right_data_point[2]:
            target = 1.0
        else:
            target = 0.0

        if self.loss == 0:
            target = int(target)

        return (left_am,right_am), target

    def __len__(self):
        return len(self.data)

