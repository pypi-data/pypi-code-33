import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont


def pic2sym(src, dest=None, style=0):
        if(style != 0 and style != 1):
            print('Wrong style!')
            return -1
        p2s_big = ['$ ', '@ ', '# ', '& ', '% ', 'G ', '0 ',
                   'O ', 'o ', '* ', '; ', ': ', '~ ', '- ', ', ', '. ', '  ']
        p2s_small = ['$', '@', '#', '&', '%', 'G', '0',
                     'O', 'o', '*', ';', ':', '~', '-', ',', '.', ' ']
        if(dest == None):
            dest = src.split('.')
            dest.insert(-1, '_2sym.')
            dest = ''.join(dest)

        img = Image.open(src)
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
            if(style == 0):
                x += p2s_small[int(data[i])]
            if(style == 1):
                x += p2s_big[int(data[i])]
            if(i % width == 0):
                x += '\n'

        if(style == 0):
            new_img = Image.new('L', (width*6, height*16), '#fff')
        if(style == 1):
            new_img = Image.new('L', (width*12, height*16), '#fff')
        dr = ImageDraw.Draw(new_img)
        dr.multiline_text((1, 1), x, fill='#000', align='center')
        new_img.save(dest)
        return 0
