import functools
import inspect
import edict.edict as eded
import io

####

#params_dict

#curr_state,trigger_checker,trigger_checker_argnames 
# :
#action,action_argnames,next_state

#curr_state,input_symbol

class FSM():
    def __init__(self,**kwargs):
        ####
        if('fsm_dict' in kwargs):
            self.fsm_dict = kwargs['fsm_dict']
        else:
            self.fsm_dict = {}
        ####
        self.stream = kwargs['stream'] 
        ####
        self.params_dict = kwargs['params_dict']
        ####
        #self.curr_state = kwargs['init_state']
        ####
        if('final_dict' in kwargs):
            self.final_dict = kwargs['final_dict']
        else:
            self.final_dict = {}
    def add(self,*args):
        args = list(args)
        if(len(args) == 6):
            args[2] = tuple(args[2])
            args[4] = tuple(args[4])
        else:
            one = tuple([None])
            args = [args[0],args[1],one,args[2],one,args[3]]
        if((args[0],args[1],args[2]) in self.fsm_dict):
            print("already in fsm_dict") 
            return(False)
        else:
            self.fsm_dict[(args[0],args[1],args[2])] = (args[3],args[4],args[5]) 
            return(True)
    def remove(self,*args):
        del self.fsm_dict[(args[0],args[1],args[2])]
    def add_final(self,*args):
        if((args[0]) in self.final_dict):
            print("already in final_dict")
            return(False)
        else:
            args = list(args)
            if(len(args) == 3):
                args[2] = tuple(args[2])
            else:
                args = [args[0],args[1],tuple([None])]
            self.final_dict[args[0]] = (args[1],args[2])
            return(True)
    def remove_final(self,*args):
        del self.final_dict[args[0]]
    def step(self):
        for key in self.fsm_dict:
            if(key[0] == self.params_dict['curr_state']):
                trigger_checker = key[1]
                trigger_checker_argnames = key[2]
                if(trigger_checker_argnames==(None,)):
                    trigger_checker_args = [self.params_dict]
                else:
                    trigger_checker_args = eded.slctvlKL(self.params_dict,trigger_checker_argnames,deepcopy=False)
                ###
                ###
                cond = trigger_checker(*trigger_checker_args)
                if(cond):
                    action,action_argnames,next_state = self.fsm_dict[key]
                    #必须再执行动作之前更新状态
                    self.params_dict['curr_state'] = next_state
                    if(action_argnames==(None,)):
                        action_args = [self.params_dict]
                    else:
                        action_args =  eded.slctvlKL(self.params_dict,action_argnames)
                    if(action==None):
                        pass
                    else:
                        if(action_argnames==(None,)):
                            action_args = [self.params_dict]
                        else:
                            action_args =  eded.slctvlKL(self.params_dict,action_argnames)
                        self.params_dict = eded._update(self.params_dict,action(*action_args),deepcopy=False)
                    return(True)
                else:
                    pass
            else:
                pass
        raise(KeyError("no matched entry"))
    def final(self):
        action,action_argnames = self.final_dict[self.params_dict['curr_state']]
        if(action_argnames==(None,)):
            action_args =  [self.params_dict]
        else:
            action_args =  eded.slctvlKL(self.params_dict,action_argnames)
        if(action):
            self.params_dict = eded._update(self.params_dict,action(*action_args),deepcopy=False)
        else:
            pass
    def scan(self):
        if(isinstance(self.stream,str)):
            txt_arr = list(self.stream)
            lngth = len(txt_arr)
            for i in range(lngth):
                self.params_dict['cursor'] = i
                self.params_dict['input_symbol'] = txt_arr[i]
                self.step()
            ###comletion
            self.final()
        elif(isinstance(self.stream,io.TextIOWrapper)):
            #not implement yet,stringIO
            pass
        elif(isinstance(self.stream,list)):
            #not implement yet,array
            pass
        else:
            #not implement yet, stream
            pass



######


def oneparamize_dict(f):
    arg_names = inspect.getfullargspec(f).args
    def _func(arg_names,d):
        args = []
        for i in range(len(arg_names)):
            k = arg_names[i]
            args.append(d[k])
        return(f(*args))
    func = functools.partial(_func,arg_names)
    return(func)


def pipeline(funcs):
    def _pipeline(funcs,arg):
        func = funcs[0]
        arg = func(arg)
        for i in range(1,len(funcs)):
            func = funcs[i]
            arg = func(arg)
        return(arg)
    p = functools.partial(_pipeline,funcs)
    return(p)

########

def bool_op(op,cond1,cond2):
    op = op.lower()
    if(op == "and"):
        return(bool(cond1 and cond2))
    elif(op == "or"):
        return(bool(cond1 or cond2))
    elif(op == "not"):
        return(not(cond1))
    elif(op == "xor"):
        c1 = bool(not(cond1) and cond2)
        c2 = bool(cond1 and not(cond2))
        c = bool(c1 or c2)
        return(c)
    else:
        raise(SyntaxError("not supported op: "+op))


def bool_funcs_ops(funcs,ops):
    def _rslt(funcs,ops,arg):
        rslts = []
        for i in range(len(funcs)):
            rslt = bool(funcs[i](arg))
            rslts.append(rslt)
        cond = rslts[0]
        for i in range(1,len(rslts)):
            op = ops[i-1]
            cond = bool_op(op,cond,rslts[i])
        return(cond)
    p = functools.partial(_rslt,funcs,ops)
    return(p)



####



