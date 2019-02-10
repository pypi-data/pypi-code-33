import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

p2s = ['  ', '. ', ', ', '- ', '~ ', ': ', '; ', '* ', 'o ',
       'O ', '0 ', 'G ', '% ', '& ', '# ', '@ ', '$ ']

def pic2sym():
        path = './cat.jpg'
        img = Image.open(path)
        width, height = img.size
        # width //= 5
        # height //= 5
        img = img.resize((width, height))
        data = img.getdata()
        data = np.matrix(data, dtype='float')
        data = (data.sum(axis=1)/3)//15.5
        # print(np.max(data))
        x = ''
        for i in range(len(data)):
                x += p2s[int(data[i])]
                if(i % width == 0):
                        x += '\n'

        new_img = Image.new('L', (width*16, height*16), '#fff')
        dr = ImageDraw.Draw(new_img)
        dr.multiline_text((1, 1), x, fill='#000', align='center')
        new_img.save('./new.png')
