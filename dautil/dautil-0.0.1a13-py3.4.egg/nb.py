from IPython.display import display
from IPython.display import Math


class LatexRenderer():
    def __init__(self, chapter=None, start=1):
        self.chapter = chapter
        self.curr = start

    def number_equation(self):
        number = '('

        if self.chapter:
            number += str(self.chapter) + '.'

        number += str(self.curr) + ')\hspace{1cm}'

        return number

    def render(self, equation):
        number = self.number_equation()
        display(Math(r'%s' % (number + equation)))
        self.curr += 1
