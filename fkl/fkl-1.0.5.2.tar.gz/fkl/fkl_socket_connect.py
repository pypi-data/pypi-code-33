from .fkl_socket import *
from .fkl_string import *
from .fkl_time import *
from .fkl_thread_pool import *
from .fkl_thread_lock import *

class FKLSwapMSG:
    def __init__(self,msg_str=None,host="127.0.0.1"):
        if(msg_str==None):
            self._arg_dict={}
            self._host=host
            self._freeze_bool=False
        elif(type(msg_str)==str):
            self._freeze_bool=True
            self._size=0
            self._create_time=None
            self._host=None
            self._arg_dict={}
            try:
                self._MsgTranslater(msg_str)
            except:
                raise Exception("FKLSwapMSG __init__ Error: Format msg_str fail.")
        else:
            raise Exception("FKLSwapMSG __init__ Error: The msg_str's type must be str.")
    def __setitem__(self,key,value):
        self.Set(key,value)
        return
    def __getitem__(self,key):
        value=self._arg_dict.get(key,None)
        if(value==None):
            raise Exception("FKLSwapMSG __getitem__ Error: The key is not in _arg_dict.")
        return value
    def __call__(self):
        return self.ToStr()
    def _FreezeCheck(self):
        if(self._freeze_bool==True):
            raise Exception("FKLSwapMSG _FreezeCheck Error: This msg is already freeze.")
    def _MsgTranslater(self,msg_str):
        dict_buf={}
        msg_str=msg_str.split("#BEGIN\n")[1].split("\n#END\n")[0]
        msg_str,args=msg_str.split("ARGS=",1)
        msgs=msg_str.split("\n")
        del msgs[-1]
        for msg in msgs:
            key,value=msg.split("=",1)
            dict_buf[key]=value
        self._size=int(dict_buf["SIZE"])
        self._create_time=dict_buf["CREATE_TIME"]
        self._host=dict_buf["HOST"]
        self._arg_dict=FKLdecodeJsonStr(args)
        return 
    def _FinalMark(self,arg_str):
        begin="#BEGIN\n"
        basic="CREATE_TIME="+FKLGetCurrentTimeStr()+"\n"+"HOST="+self._host+"\n"
        arg_str="ARGS="+arg_str+"\n"
        end="#END\n"
        msg_size_temp=len(begin.encode("utf-8"))+len(basic.encode("utf-8"))+len(arg_str.encode("utf-8"))+len(end.encode("utf-8"))
        msg_size_temp_str="SIZE="+str(msg_size_temp)+"\n"
        msg_size=msg_size_temp+len(msg_size_temp_str)
        msg_size_str="SIZE="+str(msg_size)+"\n"
        if(len(msg_size_str)>len(msg_size_temp_str)):
            msg_size=msg_size+1
            msg_size_str="SIZE="+str(msg_size)+"\n"
        msg_str=begin+msg_size_str+basic+arg_str+end
        return msg_str
    def SetHost(self,host):
        self._host=host
        return 
    def Set(self,key,value):
        self._FreezeCheck()
        if(type(key)!=str):
            raise Exception("FKLSwapMSG Set Error: The key's type must be str.")
        self._arg_dict[key]=value
        return 
    def ToStr(self):
        arg_str=FKLEncodeJsonStr(self._arg_dict)
        return self._FinalMark(arg_str)
    def GetSize(self):
        return len(self.ToStr().encode("utf-8"))
        
class FKLSimpleServer:
    def __init__(self,host,port,max_thread=3):
        self._host=host
        self._port=port
        self._main_socket=self._ConstructMainSocket(host,port)
        self._thread_pool=FKLThreadPool(max_thread)
        self._server_switch=False
        self._process_function=None
    def _ConstructMainSocket(self,host,port):
        main_socket=FKLSocket()
        FKLBind(main_socket,host,port)
        FKLListen(main_socket)
        return main_socket
    def _WaitingForRequest(self):
        while(self._server_switch==True):
            accepted_socket,cnct_addr=FKLAccept(self._main_socket)
            accepted_ip=str(cnct_addr[0])
            print("Accept a Connect from "+accepted_ip+".")
            self._thread_pool(self._Thread,[accepted_ip,accepted_socket])
        return
    def _Thread(self,args):
        accepted_ip,accepted_socket=args
        recv_msg=FKLRecv(accepted_socket)
        recv_swap_msg=FKLSwapMSG(recv_msg)
        respond_msg=self._process_function(accepted_ip,recv_swap_msg).ToStr()
        FKLSend(accepted_socket,respond_msg)
        accepted_socket.Close()
        return
    def SetProcessFunction(self,process_function):
        self._process_function=process_function
        return
    def Open(self):
        if(type(self._process_function)==type(None)):
            raise Exception("FKLSimpleServer Open Error: Before Open, to SetProcessFunction first.")
        self._server_switch=True
        self._thread_pool.Start()
        self._WaitingForRequest()
    def Close(self):
        self._server_switch=False
        self._thread_pool.Stop()

class FKLSimpleClient:
    def __init__(self,host,port,time_out=None):
        self._host=host
        self._port=port
        self._main_socket=FKLSocket(time_out=time_out)
    def _Connect(self):
        FKLConnect(self._main_socket,self._host,self._port)
        return 
    def _CloseConnect(self):
        self._main_socket.Close()
        self._main_socket=FKLSocket()
        return 
    def _Recv(self):
        recv_msg=FKLRecv(self._main_socket)
        return recv_msg
    def _Send(self,msg_str):
        FKLSend(self._main_socket,msg_str)
        return 
    def Send(self,fkl_swap_msg):
        fkl_swap_msg.SetHost(self._host)
        msg_str=fkl_swap_msg.ToStr()
        self._Connect()
        self._Send(msg_str)
        recv_msg=self._Recv()
        self._CloseConnect()
        recv_swap_msg=FKLSwapMSG(recv_msg)
        return recv_swap_msg

class FKLServer(FKLSimpleServer):
    def __init__(self,host,port,max_thread=3):
        super(FKLServer,self).__init__(host,port,max_thread=max_thread)
        self._thread_lock=FKLThreadLock()
        self._connecting_num=0
    def _Thread(self,args):
        accepted_ip,accepted_socket=args
        self._thread_lock.Acruire()
        self._connecting_num+=1
        self._thread_lock.Release()
        while(1):
            recv_msg=FKLRecv(accepted_socket)
            recv_swap_msg=FKLSwapMSG(recv_msg)
            try:
                if(recv_swap_msg["Connect"]!=1):break
            except:break
            respond_msg=self._process_function(accepted_ip,recv_swap_msg).ToStr()
            FKLSend(accepted_socket,respond_msg)
            
            try:accepted_socket.GetPeerName()
            except:break
        accepted_socket.Close()
        self._thread_lock.Acruire()
        self._connecting_num=self._connecting_num-1
        self._thread_lock.Release()
        return
    def _CloseAcceptedThread(self,time_out=3):
        client_temp=FKLClient(self._host,self._port,time_out=time_out)
        try:
            client_temp.Connect()
            client_temp.CloseConnect()
            return True
        except:
            return False
    def Close(self,time_out=3):
        super(FKLServer,self).Close()
        while(1):
            self._CloseAcceptedThread(time_out)
            if(self._thread_pool.Stop(time_out)==True):
                break
        return 
    def GetConnectingNum(self):
        return self._connecting_num
class FKLClient(FKLSimpleClient):
    def __init__(self,host,port,time_out=None):
        super(FKLClient,self).__init__(host,port,time_out=time_out)
    def Connect(self):
        self._Connect()
        return 
    def CloseConnect(self):
        fkl_swap_msg=FKLSwapMSG()
        fkl_swap_msg.SetHost(self._host)
        fkl_swap_msg["Connect"]=0
        msg_str=fkl_swap_msg.ToStr()
        self._Send(msg_str)
        self._CloseConnect()
        return
    def Send(self,fkl_swap_msg):
        fkl_swap_msg.SetHost(self._host)
        fkl_swap_msg["Connect"]=1
        msg_str=fkl_swap_msg.ToStr()
        self._Send(msg_str)
        recv_msg=self._Recv()
        recv_swap_msg=FKLSwapMSG(recv_msg)
        return recv_swap_msg