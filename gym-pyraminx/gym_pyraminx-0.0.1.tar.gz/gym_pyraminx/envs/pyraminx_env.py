import gym
from gym import spaces


class PyraminxEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self):
        self.action_space = spaces.Tuple((spaces.Discrete(4),
                                          spaces.Discrete(2),
                                          spaces.Discrete(2)))

    def step(self, action):
        ...

    def reset(self):
        ...

    def render(self, mode='human', close=False):
        ...

