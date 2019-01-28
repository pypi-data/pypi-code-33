import configs

import io
from wand.image import Image, Color

import os
import sys
import shutil


def hex_to_rgb(value):
    try:
        value = value.lstrip('#')
        lv = len(value)
        tup = tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))
        out = []
        for i in tup:
            out.append(i / 255)
        return (out)
    except:
        sys.exit('Unable to convert color definition from HEX to RGB. Please check the palette config file.')


def pdf_page_to_png(parameters):
    try:
        resolution = parameters.config['png_dpi']
        if '.pdf' not in parameters.config['output_filename']:
            filename = parameters.config['output_filename'] + '.pdf'
        else:
            filename = parameters.config['output_filename']
        page = Image(filename=filename, resolution=resolution)
        page.format = 'png'
        page.background_color = Color('white')
        page.alpha_channel = 'remove'

        if '.png' not in parameters.config['output_filename']:
            image_filename = parameters.config['output_filename'] + '.png'
        else:
            image_filename = parameters.config['output_filename']
        # image_filename = filename + '.png'
        # image_filename = '{}-{}.png'.format(image_filename, page)
        # image_filename = os.path.join('./', image_filename)
        if '.png' in parameters.config['output_filename'] or (
                '.pdf' not in parameters.config['output_filename'] and '.png' not in parameters.config[
            'output_filename']):
            page.save(filename=image_filename)
            print('Image successfully saved to', image_filename)
        if '.pdf' not in parameters.config['output_filename'] and '.png' in parameters.config['output_filename']:
            os.remove(filename)
    except:
        sys.exit(
            'Unable to convert the pdf file to png. There might be a problem with the \'wand\' python package or with ImageMagick installation.')


def path_manager():
    users_path = os.getcwd()
    inside_path = os.path.dirname(__file__, '')

    paths = dict(users_path=users_path, inside_path=inside_path)

    return (paths)
