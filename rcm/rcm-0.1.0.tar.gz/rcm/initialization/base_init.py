

class BaseInitialization(object):
    def __init__(self, **kwargs):
        if 'agent_class' not in kwargs:
            raise Exception("RandomInitialization requires an agent_class keyword argument")
        self.AgentClass = kwargs['agent_class']
        self.kwargs = kwargs
        del self.kwargs['agent_class']
