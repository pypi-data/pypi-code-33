# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
from kaitaistruct import __version__ as ks_version, KaitaiStruct, KaitaiStream, BytesIO


if parse_version(ks_version) < parse_version('0.7'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.7 or later is required, but you have %s" % (ks_version))

class Eshail2(KaitaiStruct):
    """:field ao40_beacon_type: ao40_frame.ao40_beacon_type
    :field ao40_message_line1: ao40_frame.ao40_beacon_data.ao40_message_line1
    :field ao40_message_line2: ao40_frame.ao40_beacon_data.ao40_message_line2
    :field ao40_message_line3: ao40_frame.ao40_beacon_data.ao40_message_line3
    :field ao40_message_line4: ao40_frame.ao40_beacon_data.ao40_message_line4
    :field ao40_message_line5: ao40_frame.ao40_beacon_data.ao40_message_line5
    :field ao40_message_line6: ao40_frame.ao40_beacon_data.ao40_message_line6
    :field ao40_message_line7: ao40_frame.ao40_beacon_data.ao40_message_line7
    :field ao40_message_line8: ao40_frame.ao40_beacon_data.ao40_message_line8
    
    .. seealso::
       Source - https://amsat-dl.org/wp-content/uploads/2019/01/tlmspec.pdf
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.ao40_frame = self._root.Ao40Frame(self._io, self, self._root)

    class Ao40Frame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ao40_beacon_type = self._io.read_u1()
            _on = self.ao40_beacon_type
            if _on == 77:
                self._raw_ao40_beacon_data = self._io.read_bytes(511)
                io = KaitaiStream(BytesIO(self._raw_ao40_beacon_data))
                self.ao40_beacon_data = self._root.Ao40MessageSpare(io, self, self._root)
            elif _on == 69:
                self._raw_ao40_beacon_data = self._io.read_bytes(511)
                io = KaitaiStream(BytesIO(self._raw_ao40_beacon_data))
                self.ao40_beacon_data = self._root.Ao40MessageSpare(io, self, self._root)
            elif _on == 88:
                self._raw_ao40_beacon_data = self._io.read_bytes(511)
                io = KaitaiStream(BytesIO(self._raw_ao40_beacon_data))
                self.ao40_beacon_data = self._root.Ao40MessageSpare(io, self, self._root)
            elif _on == 78:
                self._raw_ao40_beacon_data = self._io.read_bytes(511)
                io = KaitaiStream(BytesIO(self._raw_ao40_beacon_data))
                self.ao40_beacon_data = self._root.Ao40MessageSpare(io, self, self._root)
            elif _on == 65:
                self._raw_ao40_beacon_data = self._io.read_bytes(511)
                io = KaitaiStream(BytesIO(self._raw_ao40_beacon_data))
                self.ao40_beacon_data = self._root.Ao40MessageSpare(io, self, self._root)
            elif _on == 76:
                self._raw_ao40_beacon_data = self._io.read_bytes(511)
                io = KaitaiStream(BytesIO(self._raw_ao40_beacon_data))
                self.ao40_beacon_data = self._root.Ao40MessageL(io, self, self._root)
            elif _on == 68:
                self._raw_ao40_beacon_data = self._io.read_bytes(511)
                io = KaitaiStream(BytesIO(self._raw_ao40_beacon_data))
                self.ao40_beacon_data = self._root.Ao40MessageSpare(io, self, self._root)
            elif _on == 75:
                self._raw_ao40_beacon_data = self._io.read_bytes(511)
                io = KaitaiStream(BytesIO(self._raw_ao40_beacon_data))
                self.ao40_beacon_data = self._root.Ao40MessageK(io, self, self._root)
            else:
                self._raw_ao40_beacon_data = self._io.read_bytes(511)
                io = KaitaiStream(BytesIO(self._raw_ao40_beacon_data))
                self.ao40_beacon_data = self._root.Ao40CommandResponse(io, self, self._root)
            self.crc = self._io.read_u2be()


    class Ao40CommandResponse(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ao40_message_line1 = (self._io.read_bytes(63)).decode(u"ASCII")
            self.ao40_message_line2 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line3 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line4 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line5 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line6 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line7 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line8 = (self._io.read_bytes(64)).decode(u"ASCII")


    class Ao40MessageSpare(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ao40_message_line1 = (self._io.read_bytes(63)).decode(u"ASCII")
            self.ao40_message_line2 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line3 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line4 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line5 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line6 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line7 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line8 = (self._io.read_bytes(64)).decode(u"ASCII")


    class Ao40MessageL(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ao40_message_line1 = (self._io.read_bytes(63)).decode(u"ASCII")
            self.ao40_message_line2 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line3 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line4 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line5 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line6 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line7 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line8 = (self._io.read_bytes(64)).decode(u"ASCII")


    class Ao40MessageK(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ao40_message_line1 = (self._io.read_bytes(63)).decode(u"ASCII")
            self.ao40_message_line2 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line3 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line4 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line5 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line6 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line7 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line8 = (self._io.read_bytes(64)).decode(u"ASCII")


    @property
    def frame_length(self):
        if hasattr(self, '_m_frame_length'):
            return self._m_frame_length if hasattr(self, '_m_frame_length') else None

        self._m_frame_length = self._io.size()
        return self._m_frame_length if hasattr(self, '_m_frame_length') else None


