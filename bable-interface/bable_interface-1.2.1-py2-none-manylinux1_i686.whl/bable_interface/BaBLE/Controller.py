# automatically generated by the FlatBuffers compiler, do not modify

# namespace: BaBLE

import flatbuffers

class Controller(object):
    __slots__ = ['_tab']

    @classmethod
    def GetRootAsController(cls, buf, offset):
        n = flatbuffers.encode.Get(flatbuffers.packer.uoffset, buf, offset)
        x = Controller()
        x.Init(buf, n + offset)
        return x

    # Controller
    def Init(self, buf, pos):
        self._tab = flatbuffers.table.Table(buf, pos)

    # Controller
    def Id(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            return self._tab.Get(flatbuffers.number_types.Uint16Flags, o + self._tab.Pos)
        return 0

    # Controller
    def Address(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(6))
        if o != 0:
            return self._tab.String(o + self._tab.Pos)
        return None

    # Controller
    def BtVersion(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(8))
        if o != 0:
            return self._tab.Get(flatbuffers.number_types.Uint8Flags, o + self._tab.Pos)
        return 0

    # Controller
    def Powered(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(10))
        if o != 0:
            return bool(self._tab.Get(flatbuffers.number_types.BoolFlags, o + self._tab.Pos))
        return False

    # Controller
    def Connectable(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(12))
        if o != 0:
            return bool(self._tab.Get(flatbuffers.number_types.BoolFlags, o + self._tab.Pos))
        return False

    # Controller
    def Discoverable(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(14))
        if o != 0:
            return bool(self._tab.Get(flatbuffers.number_types.BoolFlags, o + self._tab.Pos))
        return False

    # Controller
    def LowEnergy(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(16))
        if o != 0:
            return bool(self._tab.Get(flatbuffers.number_types.BoolFlags, o + self._tab.Pos))
        return False

    # Controller
    def Advertising(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(18))
        if o != 0:
            return bool(self._tab.Get(flatbuffers.number_types.BoolFlags, o + self._tab.Pos))
        return False

    # Controller
    def Name(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(20))
        if o != 0:
            return self._tab.String(o + self._tab.Pos)
        return None

def ControllerStart(builder): builder.StartObject(9)
def ControllerAddId(builder, id): builder.PrependUint16Slot(0, id, 0)
def ControllerAddAddress(builder, address): builder.PrependUOffsetTRelativeSlot(1, flatbuffers.number_types.UOffsetTFlags.py_type(address), 0)
def ControllerAddBtVersion(builder, btVersion): builder.PrependUint8Slot(2, btVersion, 0)
def ControllerAddPowered(builder, powered): builder.PrependBoolSlot(3, powered, 0)
def ControllerAddConnectable(builder, connectable): builder.PrependBoolSlot(4, connectable, 0)
def ControllerAddDiscoverable(builder, discoverable): builder.PrependBoolSlot(5, discoverable, 0)
def ControllerAddLowEnergy(builder, lowEnergy): builder.PrependBoolSlot(6, lowEnergy, 0)
def ControllerAddAdvertising(builder, advertising): builder.PrependBoolSlot(7, advertising, 0)
def ControllerAddName(builder, name): builder.PrependUOffsetTRelativeSlot(8, flatbuffers.number_types.UOffsetTFlags.py_type(name), 0)
def ControllerEnd(builder): return builder.EndObject()
