from bgez.game import types

__all__ = [
    'Stage',
]

def __method_noop__(self, *args):
    ...

class Stage:
    '''
    A stage is an abstraction layer for your logic to be run inside a scene.
    Stages will replace each others within the same scene, eventually.
    '''

    logic = __method_noop__
    pre_draw_setup = __method_noop__
    pre_draw = __method_noop__
    post_draw = __method_noop__

    def __init__(self):
        self.__previous: Stage = None
        self.__scene: types.Scene = None
        self.next: Stage = None

    def __remove(self, scene):
        self.unload()

    def _attach(self, scene: types.Scene, previous: 'Stage'):
        self.__previous = previous
        self.__scene = scene
        if self.logic is not __method_noop__:
            self.logic_loop = scene.logic.interval(1, self.logic)
        if self.pre_draw_setup is not __method_noop__:
            scene.pre_draw_setup.append(self.pre_draw_setup)
        if self.pre_draw is not __method_noop__:
            scene.pre_draw.append(self.pre_draw)
        if self.post_draw is not __method_noop__:
            scene.post_draw.append(self.post_draw)
        scene.removal.append(self.__remove)
        self.load()

    def _detach(self):
        scene = self.__scene
        self.logic_loop.cancel()
        scene.pre_draw_setup.try_remove(self.pre_draw_setup)
        scene.pre_draw.try_remove(self.pre_draw)
        scene.post_draw.try_remove(self.post_draw)
        scene.removal.try_remove(self.__remove)
        self.unload()
        self.__scene = None

    @property
    def previous(self) -> 'Stage':
        return self.__previous

    @property
    def scene(self) -> types.Scene:
        return self.__scene

    def load(self):
        '''Loads the stage and its resources'''

    def unload(self):
        '''Unloads the stage and its resources'''
