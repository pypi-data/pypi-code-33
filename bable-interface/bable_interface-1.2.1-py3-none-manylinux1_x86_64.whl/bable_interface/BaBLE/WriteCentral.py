# automatically generated by the FlatBuffers compiler, do not modify

# namespace: BaBLE

import flatbuffers

class WriteCentral(object):
    __slots__ = ['_tab']

    @classmethod
    def GetRootAsWriteCentral(cls, buf, offset):
        n = flatbuffers.encode.Get(flatbuffers.packer.uoffset, buf, offset)
        x = WriteCentral()
        x.Init(buf, n + offset)
        return x

    # WriteCentral
    def Init(self, buf, pos):
        self._tab = flatbuffers.table.Table(buf, pos)

    # WriteCentral
    def ConnectionHandle(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            return self._tab.Get(flatbuffers.number_types.Uint16Flags, o + self._tab.Pos)
        return 0

    # WriteCentral
    def AttributeHandle(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(6))
        if o != 0:
            return self._tab.Get(flatbuffers.number_types.Uint16Flags, o + self._tab.Pos)
        return 0

    # WriteCentral
    def Value(self, j):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(8))
        if o != 0:
            a = self._tab.Vector(o)
            return self._tab.Get(flatbuffers.number_types.Uint8Flags, a + flatbuffers.number_types.UOffsetTFlags.py_type(j * 1))
        return 0

    # WriteCentral
    def ValueAsNumpy(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(8))
        if o != 0:
            return self._tab.GetVectorAsNumpy(flatbuffers.number_types.Uint8Flags, o)
        return 0

    # WriteCentral
    def ValueLength(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(8))
        if o != 0:
            return self._tab.VectorLen(o)
        return 0

def WriteCentralStart(builder): builder.StartObject(3)
def WriteCentralAddConnectionHandle(builder, connectionHandle): builder.PrependUint16Slot(0, connectionHandle, 0)
def WriteCentralAddAttributeHandle(builder, attributeHandle): builder.PrependUint16Slot(1, attributeHandle, 0)
def WriteCentralAddValue(builder, value): builder.PrependUOffsetTRelativeSlot(2, flatbuffers.number_types.UOffsetTFlags.py_type(value), 0)
def WriteCentralStartValueVector(builder, numElems): return builder.StartVector(1, numElems, 1)
def WriteCentralEnd(builder): return builder.EndObject()
