import socket as sckt
import zlib
from .fkl_math import *

class FKLSocket:
    def __init__(self,socket_type="INET",init_socket=None,time_out=None):
        self._socket_type=socket_type
        self._time_out=time_out
        if(init_socket!=None):self._socket=init_socket
        else:self._socket=self._Construct(socket_type,time_out)
    def _Construct(self,socket_type,time_out):
        if(socket_type=="INET"):
            new_socket=sckt.socket(sckt.AF_INET,sckt.SOCK_STREAM)
        elif(socket_type=="LOCAL"):
            new_socket=sckt.socket(sckt.AF_UNIX,sckt.SOCK_STREAM)
        else:
            raise Exception("FKLSocket __init__ Error: Unknown socket_type.")
        if(type(time_out)==int or type(time_out)==float):
            new_socket.settimeout(time_out)
        return new_socket
    def _GetSocket(self):
        return self._socket
    def GetSockName(self):
        try:
            return self._socket.getsockname()
        except:
            raise Exception("FKLSocket GetSockName Error: The socket was closed.")
    def GetPeerName(self):
        try:
            return self._socket.getpeername()
        except:
            raise Exception("FKLSocket GetPeerName Error: The socket is not connected.")
    def Close(self):
        self._socket.close()
        return
    def Reset(self):
        self._socket=self._Construct(self._socket_type,self._time_out)
        return 

def FKLBind(fkl_socket,host,port):
    socket_buf=fkl_socket._GetSocket()
    socket_buf.setsockopt(sckt.SOL_SOCKET, sckt.SO_REUSEADDR, 1)
    socket_buf.bind((host,port))
    return 
def FKLListen(fkl_socket):
    socket_buf=fkl_socket._GetSocket()
    socket_buf.listen()
    return
def FKLAccept(fkl_socket):
    socket_buf=fkl_socket._GetSocket()
    cnct_socket,cnct_addr=socket_buf.accept()
    fkl_socket=FKLSocket(init_socket=cnct_socket)
    return fkl_socket,cnct_addr
def FKLConnect(fkl_socket,host,port):
    socket_buf=fkl_socket._GetSocket()
    try:
        socket_buf.connect((host,port))
    except:
        fkl_socket.Reset()
        raise Exception("FKLConnect Error: Connect fail.")
    return
def FKLSend(fkl_socket,msg):
    socket_buf=fkl_socket._GetSocket()
    cmps_msg=bytearray(zlib.compress(msg.encode("utf-8")))
    cmps_msg_size=len(cmps_msg)
    bin_cmps_msg_size=FKLDecimal2Bin(cmps_msg_size)
    bin_cmps_msg_size_str=str(bin_cmps_msg_size)
    bin_cmps_msg_size_str_size=len(bin_cmps_msg_size_str)
    if(bin_cmps_msg_size_str_size>32):
        raise Exception("FKLSend Error:The msg size is out of the range(0,2^32).")
    for i in range(32-bin_cmps_msg_size_str_size):
        bin_cmps_msg_size_str="0"+bin_cmps_msg_size_str
    msg_size_byte=bytearray(4)
    msg_size_byte[0]=FKLBin2Decimal(int(bin_cmps_msg_size_str[0:8]))
    msg_size_byte[1]=FKLBin2Decimal(int(bin_cmps_msg_size_str[8:16]))
    msg_size_byte[2]=FKLBin2Decimal(int(bin_cmps_msg_size_str[16:24]))
    msg_size_byte[3]=FKLBin2Decimal(int(bin_cmps_msg_size_str[24:32]))
    
    send_bytearr=msg_size_byte+bytearray(zlib.compress(msg.encode("utf-8")))
    try:
        socket_buf.send(send_bytearr)
    except:
        fkl_socket.Reset()
        raise Exception("FKLSend Error: Send fail.")
    return 
def FKLRecv(fkl_socket,recv_buf_size=1024,max_outtime_count=10):
    socket_buf=fkl_socket._GetSocket()
    recv_bytes=socket_buf.recv(recv_buf_size)
    first_byte=str(FKLDecimal2Bin(recv_bytes[0]))
    for i in range(8-len(first_byte)):first_byte="0"+first_byte
    second_byte=str(FKLDecimal2Bin(recv_bytes[1]))
    for i in range(8-len(second_byte)):second_byte="0"+second_byte
    third_byte=str(FKLDecimal2Bin(recv_bytes[2]))
    for i in range(8-len(third_byte)):third_byte="0"+third_byte
    forth_byte=str(FKLDecimal2Bin(recv_bytes[3]))
    for i in range(8-len(forth_byte)):forth_byte="0"+forth_byte
    tot_bytes_size=FKLBin2Decimal(int(first_byte+second_byte+third_byte+forth_byte))
    tot_bytearr=recv_bytes[4:]
    curent_bytes_size=len(tot_bytearr)
    if(curent_bytes_size==tot_bytes_size):
        recv_msg=zlib.decompress(tot_bytearr).decode("utf8")
        return recv_msg
    
    outtime_count=0
    while(True):
        try:
            recv_bytes=socket_buf.recv(recv_buf_size)
        except:
            fkl_socket.Reset()
            raise Exception("FKLRecv Error: Recv fail.")
        recv_bytes_size=len(recv_bytes)
        if(recv_bytes_size==0):
            outtime_count+=1
            if(outtime_count==max_outtime_count):
                raise Exception("FKLRecv Error:Recv none is out of the max iter count.")
        else:
            outtime_count=0
            tot_bytearr+=recv_bytes
            curent_bytes_size+=len(recv_bytes)
            if(curent_bytes_size==tot_bytes_size):break
    recv_msg=zlib.decompress(tot_bytearr).decode("utf8")
    
    return recv_msg

