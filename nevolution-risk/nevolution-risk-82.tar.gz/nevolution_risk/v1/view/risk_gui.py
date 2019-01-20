import os
import numpy as np
import pygame
from pygame.cursors import load_xbm

from nevolution_risk.constants.colors import deep_pink, blue, black
from nevolution_risk.constants.view_settings import coordinates, width, height, radius, line_thickness


class Gui(object):

    def __init__(self, graph):
        self.graph = graph
        self.game_display = None
        self.rendering = True

        dir_name = os.path.dirname(os.path.realpath(__file__))
        self.sword = pygame.image.load(os.path.join(dir_name, '../../res', 'sword.png'))
        void_mask_path = os.path.join(dir_name, '../../res', 'void-mask.xbm')
        void_path = os.path.join(dir_name, '../../res', 'void.xbm')
        self.void_cursor = load_xbm(void_path, void_mask_path)

        self.grid = []
        for n in range(1, 11):
            for adjacent in self.graph.nodes[n].adj_list:
                self.grid.append((coordinates[n], coordinates[adjacent.id]))

    def render(self, mode="human"):
        if self.game_display is None:
            self.init()

        self.game_display.fill(deep_pink)

        for edge in self.grid:
            pygame.draw.line(self.game_display, blue, edge[0], edge[1], 10)

        n = 0
        for position in coordinates:
            pygame.draw.circle(self.game_display, self.graph.nodes[n].player.color, position, radius)
            n = n + 1

        if mode == 'rgb_array':
            raw_pxarray = pygame.PixelArray(self.game_display)
            pxarray = []
            for row in raw_pxarray:
                row_px = []
                for pix in row:
                    tup = self.game_display.unmap_rgb(pix)
                    rgb = [tup[0], tup[1], tup[2]]
                    row_px.append(rgb)
                pxarray.append(row_px)
            return np.array(pxarray).astype(np.uint8)

        return None

    def init(self):
        pygame.init()
        self.game_display = pygame.display.set_mode((width, height))

    def set_cursor_arrow(self):
        pygame.mouse.set_cursor(*pygame.cursors.arrow)

    def set_cursor_sword(self):
        pygame.mouse.set_cursor(*self.void_cursor)

    def draw_sword(self, pos1, pos2):
        # en garde!
        pygame.draw.line(self.game_display, black, pos1, pos2, line_thickness)
        self.game_display.blit(self.sword, pos2)
