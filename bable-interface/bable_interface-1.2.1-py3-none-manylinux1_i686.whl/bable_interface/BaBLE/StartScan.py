# automatically generated by the FlatBuffers compiler, do not modify

# namespace: BaBLE

import flatbuffers

class StartScan(object):
    __slots__ = ['_tab']

    @classmethod
    def GetRootAsStartScan(cls, buf, offset):
        n = flatbuffers.encode.Get(flatbuffers.packer.uoffset, buf, offset)
        x = StartScan()
        x.Init(buf, n + offset)
        return x

    # StartScan
    def Init(self, buf, pos):
        self._tab = flatbuffers.table.Table(buf, pos)

    # StartScan
    def ActiveScan(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            return bool(self._tab.Get(flatbuffers.number_types.BoolFlags, o + self._tab.Pos))
        return True

def StartScanStart(builder): builder.StartObject(1)
def StartScanAddActiveScan(builder, activeScan): builder.PrependBoolSlot(0, activeScan, 1)
def StartScanEnd(builder): return builder.EndObject()
