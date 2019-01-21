# automatically generated by the FlatBuffers compiler, do not modify

# namespace: fast_

import flatbuffers

class Graph(object):
    __slots__ = ['_tab']

    @classmethod
    def GetRootAsGraph(cls, buf, offset):
        n = flatbuffers.encode.Get(flatbuffers.packer.uoffset, buf, offset)
        x = Graph()
        x.Init(buf, n + offset)
        return x

    # Graph
    def Init(self, buf, pos):
        self._tab = flatbuffers.table.Table(buf, pos)

    # Graph
    def Unit(self, j):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            x = self._tab.Vector(o)
            x += flatbuffers.number_types.UOffsetTFlags.py_type(j) * 4
            x = self._tab.Indirect(x)
            from fast_.Graph_.Unit import Unit
            obj = Unit()
            obj.Init(self._tab.Bytes, x)
            return obj
        return None

    # Graph
    def UnitLength(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            return self._tab.VectorLen(o)
        return 0

def GraphStart(builder): builder.StartObject(1)
def GraphAddUnit(builder, unit): builder.PrependUOffsetTRelativeSlot(0, flatbuffers.number_types.UOffsetTFlags.py_type(unit), 0)
def GraphStartUnitVector(builder, numElems): return builder.StartVector(4, numElems, 4)
def GraphEnd(builder): return builder.EndObject()
