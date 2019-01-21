# automatically generated by the FlatBuffers compiler, do not modify

# namespace: Graph_

import flatbuffers

class NodeType(object):
    __slots__ = ['_tab']

    @classmethod
    def GetRootAsNodeType(cls, buf, offset):
        n = flatbuffers.encode.Get(flatbuffers.packer.uoffset, buf, offset)
        x = NodeType()
        x.Init(buf, n + offset)
        return x

    # NodeType
    def Init(self, buf, pos):
        self._tab = flatbuffers.table.Table(buf, pos)

    # NodeType
    def Node(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            return self._tab.Get(flatbuffers.number_types.Int32Flags, o + self._tab.Pos)
        return 0

    # NodeType
    def Type(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(6))
        if o != 0:
            return self._tab.String(o + self._tab.Pos)
        return None

def NodeTypeStart(builder): builder.StartObject(2)
def NodeTypeAddNode(builder, node): builder.PrependInt32Slot(0, node, 0)
def NodeTypeAddType(builder, type): builder.PrependUOffsetTRelativeSlot(1, flatbuffers.number_types.UOffsetTFlags.py_type(type), 0)
def NodeTypeEnd(builder): return builder.EndObject()
