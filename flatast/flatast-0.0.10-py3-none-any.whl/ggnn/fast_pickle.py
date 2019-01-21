import flatast
import os
import sys
import pickle
sys.path.insert(0, os.path.dirname(flatast.__file__))
from fast_pb2 import Data as PBData
from fast_.Element import *
from fast_.Data import *
from google.protobuf import text_format
import flatbuffers
#import pyarrow

# write data as flatbuffers Data
def _serialize_Data(data):
    return data

# read data as flatbuffers Data
def _deserialize_Data(data):
    buf = bytearray(data)
    return Data.GetRootAsData(buf, 0)

def main():
    #context = pyarrow.SerializationContext()
    #context.register_type(Data, 'Data',
    #    custom_serializer=_serialize_Data,
    #    custom_deserializer=_deserialize_Data)

    if sys.argv[1].endswith('.pb') and (sys.argv[2].endswith('.pickle') or sys.argv[2].endswith('.pkl')):
        data = PBData()
        with open(sys.argv[1], 'rb') as f:
            data.ParseFromString(f.read())
            f.close()
        with open(sys.argv[2], 'wb') as f:
            pickle.dump(data, f);
    #elif sys.argv[1].endswith('.fbs') and sys.argv[2].endswith('.pa'):
    #    with open(sys.argv[1], 'rb') as f:
    #        data = f.read()
    #        buf = bytearray(data)
    #        data = Data.GetRootAsData(buf, 0)
    #        f.close()
    #    with open(sys.argv[2], 'wb') as f:
    #        buf = context.serialize(data).to_buffer()
    #        f.write(buf)
    #        f.close()
    elif sys.argv[2].endswith('.pb') and (sys.argv[1].endswith('.pickle') or sys.argv[1].endswith('.pkl')):
        with open(sys.argv[1], 'rb') as f:
            data = pickle.load(f);
        with open(sys.argv[2], 'wb') as f:
            serializedMessage = data.SerializeToString()
            f.write(serializedMessage)
            f.close()
    #elif sys.argv[2].endswith('.fbs') and sys.argv[1].endswith('.pa'):
    #    with open(sys.argv[1], 'rb') as f:
    #        buf = f.read()
    #        data = context.deserialize(buf)
    #        f.close()
    #    with open(sys.argv[2], 'wb') as f:
    #        builder = flatbuffers.Builder(0)
    #        builder.Finish(data)
            buf = builder.Output()
            f.write(buf)
            f.close()
    else:
        print("Please choose either .pb, .pkl, or .pickle as file extensions")

if __name__ == "__main__":
    main()
