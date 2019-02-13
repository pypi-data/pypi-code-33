#!python
## -*- coding: utf-8 -*-
import joho as j
# create html output file and
# load the default web browser to open the file
j.title("Topic 12: Python: HTML SGV ")
j.insert_horizontal_line()
j.heading2("パイソンによる HTML")
j.write("Hello world")
j.heading2("パイソンによる図形、アニメションの作成")
Face =  j.line(0, 0, 100, 100) +\
        j.circle(100, 100, 50, fillcolor="none") + \
        j.polygon([200, 400, 400],[100,100,300])
j.draw(Face + j.grid(100))
j.MakeTableContent()
j.show()
