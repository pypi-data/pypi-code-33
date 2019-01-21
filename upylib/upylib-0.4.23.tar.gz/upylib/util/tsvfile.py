#!/usr/bin/env python
# -*- coding:utf-8 -*-⏎

from __future__ import print_function
import os
import sys

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~5~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~8
if sys.version_info<(3,0,0):
    reload(sys)
    sys.setdefaultencoding('utf8')


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~5~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~8
class TSVFile:
    f=None
    field_list=list()
    line_list=list()
    header=""
    field_idx_dict=dict()
    idx_field_list=list()

    def __init__(self):
        return

    def load( self, fn ):
        with open(fn,'r') as f:
            self.line_list = f.read().splitlines()

        if len( self.line_list ) > 0:
            first = self.line_list[0]
            if first[0] == '#':
                self.header = first
                self.line_list = self.line_list[1:]
            else:
                self.header = ""

        self.generate_field_idx()
        return
        """
        field_num = header.count("\t")+1

        for field in header.split("\t"):
            field = field[1:]
            self.add_field( field )

        for record in data:
            arr = record.split("\t")
            for x in range(len(arr)):
                value = arr[x]
                self.field_list[ x ]["data"].append( value )

        return True
        """

    def generate_field_idx(self):
        self.field_idx_dict=dict()
        self.idx_field_list=list()
        idx=0
        for w in self.header.split("\t"):
            w = w[1:]
            self.field_idx_dict[ w ] = idx
            self.idx_field_list.append( w )
            idx+=1
        return


    def field2idx( self, field_name ):
        if not self.field_idx_dict.has_key( field_name ): return None
        return self.field_idx_dict[ field_name ]

    def idx2field( self, idx ):
        if len( self.idx_field_list ) < idx: return None
        return self.idx_field_list[ idx ]

    def have_field( self, name ):
        for field in self.field_list:
            if field["name"] == name: return True
        return False

    def add_field( self, name, data=list() ):
        if self.have_field( name ):
            print( "already %s" % name )
            return False
        else:
            print( "add %s" % name )
            d = dict()
            d["name"] = name
            d["data"] = data
            self.field_list.append( d )

    def save_to( self, fn ):
        return
        fo = open( fn, "w" )

        # print header
        for i in range( len( self.field_list ) ):
            name = self.field_list[i]["name"]
            if i > 0: print( "\t", end="", file=fo )
            print( "#%s" % (name), end="", file=fo )
        print( "", file=fo )

        # print data
        for y in range( len(self.field_list[0]["data"]) ):
            for x in range( len( self.field_list ) ):

                value = self.field_list[x]["data"][y]
                if x > 0: print( "\t", end="", file=fo )
                print( "%s" % (value), end="", file=fo )
            print( "", file=fo )

        fo.close()
        return False

    def get_field_data( self, field_name ):
        for i in range( len( self.field_list ) ):
            name = self.field_list[i]["name"]
            if name == field_name:
                return self.field_list[i]["data"]
        return None


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~⏎
def tsvfile2dict( fn, keyid, valueid ):
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~⏎
    d = dict()
    with open( fn,'r') as f:
        for line in f.readlines():
            line = line.strip("\n")
            arr = line.split("\t")
            d[ arr[keyid] ] = arr[valueid]
    return d

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~⏎
def test():
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~⏎
    tsv = TSVFile()

    tsv.add_field( "id" )
    tsv.add_field( "str" )
    tsv.add_field( "str" )
    tsv.add_field( "date" )

    tsv.save_to( "out.tsv" )

    """
    field_list = tsv.get_field()
    for (idx, name) in field_list:
        print( "[%d] %s" % ( idx, name ) )
    """

    return True

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~⏎
if __name__ == "__main__": test()
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~⏎
