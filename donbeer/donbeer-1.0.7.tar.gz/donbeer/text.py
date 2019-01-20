import pygame


class Text:
    """This class holds information about the text-elements. Can make them also clickable"""

    def __init__(self, name, font, size, content=""):
        self.name = name
        self.x = 0
        self.y = 0
        self.font = font  # font_path = "./fonts/newfont.ttf"
        self.fontSize = size  # font_size = 32
        self.content = [content, 0]
        self.label = self.get_font().render(content, 1, (255, 255, 0))
        self.rect = None

    def get_font(self):
        """Get a pygame font object upon the provided attributes"""

        return pygame.font.Font(self.font, self.fontSize)

    def set_coords(self, x, y):
        """Set the coordinates for the rectangle and label."""
        self.x = x
        self.y = y
        self.rect = self.label.get_rect(topleft=(x, y))

    def set_label(self, with_var):
        """Set the label for the text. If there is a var (like for points), add it."""

        if with_var:
            self.label = self.get_font().render(self.content[0] + str(self.content[1]), 1, (255, 255, 0))
        else:
            self.label = self.get_font().render(self.content[0], 1, (255, 255, 0))
