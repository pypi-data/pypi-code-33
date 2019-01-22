import networkx as nx
import pygame

import gym
import numpy as np
from gym import spaces
from numpy import int32, float32

from nevolution_risk.constants.constants import DEFAULT_POS_PLAYER_2, DEFAULT_POS_PLAYER_1
from nevolution_risk.v2.logic import Graph
from nevolution_risk.v2.view import Gui


class RiskEnv(gym.Env):
    metadata = {
        'render.modes': ['human', 'rgb_array'],
        'video.frames_per_second': 10
    }

    node_count = 42
    player_count = 2
    troop_count = 0
    agent_territory_count = 0

    observation_space = spaces.Box(low=0, high=1, shape=[node_count * (player_count+1), ], dtype=int32)

    def __init__(self):
        self.player_positions = (DEFAULT_POS_PLAYER_1, DEFAULT_POS_PLAYER_2)
        self.graph = Graph(self.player_positions)
        self.static_agent = self.random_step
        self.gui = Gui(self.graph)
        self.current_player = 1
        self.done = False
        self.rendering = True
        self.first_render = True
        self.legal_actions = []
        for n in range(0, len(self.graph.nodes)):
            for adjacent in self.graph.nodes[n].adj_list:
                self.legal_actions.append((self.graph.nodes[n].id, adjacent.id))

        edges = []
        for line in nx.generate_edgelist(self.graph.graph):
            edges.append(line)
        edge_count = len(edges)
        self.action_space = spaces.Box(low=0, high=1, shape=[edge_count * 2, ], dtype=float32)

        self.action_len = len(self.action_space.sample())


    def set_static_agent(self, step_function):
        self.static_agent = step_function

    def set_start_positions(self, player_1, player_2):
        if player_1 == player_2:
            raise EnvironmentError('Players cannot start at the same node!')
        if player_1 > len(self.graph.nodes) - 1 or player_2 > len(self.graph.nodes) - 1:
            raise EnvironmentError('ID out of range.')
        self.player_positions = (player_1, player_2)
        self.graph = Graph(self.player_positions)

    '''
    action format:
        [probabilities]
    '''

    def step(self, action):
        if self.done:
            self.reset()

        for i, valid_action in enumerate(self.graph.players[0].valid_actions):
            action[i] *= valid_action

        source_id = self.legal_actions[np.argmax(action)][0]
        target_id = self.legal_actions[np.argmax(action)][1]

        self.graph.attack(source_id, target_id, self.graph.player1)

        """
        ----------------------------------------------------------------------------------
        code for opponent AI goes here
        """
        observation = self._graph_to_one_hot(reverse=True)

        player2_action = self.static_agent(observation)

        for i, valid_action in enumerate(self.graph.players[1].valid_actions):
            player2_action[i] *= valid_action

        source_id = self.legal_actions[np.argmax(player2_action)][0]
        target_id = self.legal_actions[np.argmax(player2_action)][1]

        self.graph.attack(source_id, target_id, self.graph.player2)
        """
        ----------------------------------------------------------------------------------
        """

        reward = self.get_reward(self.graph.player1)

        observation = self._graph_to_one_hot()
        self.done = self.graph.is_conquered()

        return observation, reward, self.done, ()

    def random_step(self, observation):
        return self.action_space.sample()

    def reset(self):
        self.graph = Graph(self.player_positions)
        self.gui.graph = self.graph
        self.done = False
        self.rendering = True
        return self._graph_to_one_hot()

    def render(self, mode='human', control="auto"):
        if self.first_render:
            pygame.init()
            self.first_render = False

        if control == "auto":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
        if mode == 'rgb_array':
            return self.gui.render(mode)
        else:
            self.gui.render(mode)

        if control == "auto":
            pygame.display.update()

    def is_action_valid(self, action, player):
        if self.graph.nodes[action[0]].player != player:
            return False

        if self.graph.nodes[action[1]].player.name != "default":
            return False
        return True

    def update_valid_actions(self):
        for player in self.graph.players:
            valid_actions = np.zeros(self.action_len, dtype=float32)
            n = 0
            for action in self.legal_actions:
                if self.is_action_valid(action, player):
                    valid_actions[n] = 1
                n = n + 1
            player.valid_actions = valid_actions

    def _graph_to_one_hot(self, reverse=False):
        one_hot = np.zeros(0, int32)
        array3 = np.zeros(5, int32)

        np.append(one_hot, array3)

        if reverse:
            player1 = self.graph.player2
            player2 = self.graph.player1
        else:
            player1 = self.graph.player1
            player2 = self.graph.player2

        for n in range(0, len(self.graph.nodes)):
            # one_hot = np.append(one_hot, to_one_hot(n, self.node_count))
            if self.graph.nodes[n].player == player1:
                one_hot = np.append(one_hot, to_one_hot(1, self.player_count))
            elif self.graph.nodes[n].player == player2:
                one_hot = np.append(one_hot, to_one_hot(2, self.player_count))
            else:
                one_hot = np.append(one_hot, to_one_hot(0, self.player_count))

        self.update_valid_actions()
        return one_hot

    def get_reward(self, player):
        total_territory = 0

        for n in range(0, len(self.graph.nodes)):
            if self.graph.nodes[n].player == player:
                total_territory += 1

        reward = total_territory - self.agent_territory_count
        self.agent_territory_count = total_territory
        return reward


def to_one_hot(n, limit):
    array = np.zeros(limit + 1, np.int32)
    array[n] = 1
    return array
