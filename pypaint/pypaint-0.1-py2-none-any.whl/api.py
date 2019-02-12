class Painter:
    def __init__(self):
        from turtle import speed, penup, hideturtle, degrees
        speed(0)
        penup()
        hideturtle()
        degrees(360)

    def set_pencolor(self, color):
        from turtle import pencolor
        pencolor(color)

    def set_fillcolor(self, color):
        from turtle import fillcolor
        fillcolor(color)

    def set_screensize(self, width, height, background=None):
        from turtle import screensize
        screensize(canvwidth=width, canvheight=height, bg=background)

    def draw_line(self, from_pos, to_pos, width):
        from turtle import penup, setpos, pendown, pensize
        oldWidth = pensize()
        pensize(width)
        setpos(from_pos)
        pendown()
        setpos(to_pos)
        penup()
        pensize(oldWidth)

    def draw_circle(self, origin, radius, width, degrees, steps):
        from turtle import circle, setpos, penup, pendown, pensize
        x = origin[0]
        y = origin[1]
        y = y - radius
        oldWidth = pensize()
        pensize(width)
        setpos((x, y))
        pendown()
        circle(radius, degrees, steps)
        penup()
        pensize(oldWidth)

    def draw_dot(self, origin, radius):
        from turtle import dot, setpos, pendown, penup
        setpos(origin)
        pendown()
        dot(radius)
        penup

    def write_text(self, pos, arg, align, font):
        from turtle import write, setpos
        setpos(pos)
        write(arg, False, align, font)

    def begin_filling(self):
        from turtle import begin_fill
        begin_fill()

    def end_filling(self):
        from turtle import end_fill
        end_fill()

    def clean(self):
        from turtle import clear
        clear()

    def done(self):
        from turtle import done
        done()