# automatically generated by the FlatBuffers compiler, do not modify

# namespace: BaBLE

import flatbuffers

class Device(object):
    __slots__ = ['_tab']

    @classmethod
    def GetRootAsDevice(cls, buf, offset):
        n = flatbuffers.encode.Get(flatbuffers.packer.uoffset, buf, offset)
        x = Device()
        x.Init(buf, n + offset)
        return x

    # Device
    def Init(self, buf, pos):
        self._tab = flatbuffers.table.Table(buf, pos)

    # Device
    def ConnectionHandle(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            return self._tab.Get(flatbuffers.number_types.Uint16Flags, o + self._tab.Pos)
        return 0

    # Device
    def Address(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(6))
        if o != 0:
            return self._tab.String(o + self._tab.Pos)
        return None

def DeviceStart(builder): builder.StartObject(2)
def DeviceAddConnectionHandle(builder, connectionHandle): builder.PrependUint16Slot(0, connectionHandle, 0)
def DeviceAddAddress(builder, address): builder.PrependUOffsetTRelativeSlot(1, flatbuffers.number_types.UOffsetTFlags.py_type(address), 0)
def DeviceEnd(builder): return builder.EndObject()
