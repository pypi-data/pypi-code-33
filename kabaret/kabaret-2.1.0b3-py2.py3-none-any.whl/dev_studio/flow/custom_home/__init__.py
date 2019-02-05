

from kabaret import flow


class Home(flow.Object):

    congrat = flow.Param('You made your own Home !').ui(editable=False)


class MyHomeRoot(flow.Root):
    '''
    '''

    Home = flow.Child(Home)

    def set_flow_actor(self, flow_actor):
        self.flow_actor = flow_actor
