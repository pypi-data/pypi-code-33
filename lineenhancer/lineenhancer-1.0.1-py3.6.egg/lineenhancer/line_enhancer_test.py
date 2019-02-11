import argparse
import matplotlib.pyplot as plt
from .maskstackcreator import MaskStackCreator
import scipy.misc as sp
import time
import numpy as np
import sys
from . import image_reader
from . import line_enhancer

argparser = argparse.ArgumentParser(
    description='Enhances line images',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)

argparser.add_argument(
    '-i',
    '--input',
    help='path to input file')

argparser.add_argument(
    '-d',
    '--downsamplesize',
    default=1024,
    type=int,
    help='size image is downsampled to (should be a power of 2')

argparser.add_argument(
    '-lw',
    '--linewidth',
    default=50,
    type=int,
    help='line width with after downsampling')

argparser.add_argument(
    '-m',
    '--maskwidth',
    default=100,
    type=int,
    help='mask width')

argparser.add_argument(
    '-a',
    '--angle_step',
    default=2,
    type=int,
    help='angle step size')

#cuda.init()
#context = make_default_context()
#stream = cuda.Stream()




def _main_():


    args = argparser.parse_args()

    '''
    LOAD IMAGE DATA AS EXAMPLE
    '''

    if args.input is not None:
        example_path = args.input
    else:
        sys.exit("No input is given")
    mask_size = args.downsamplesize
    filament_width = args.linewidth
    mask_width = args.maskwidth
    angleStep = args.angle_step
    example = image_reader.image_read(example_path)
    '''
    CREATE EXAMPLE: RESIZE IMAGE, REPEAT IT 12 TIMES (simulates 12 input images)
    '''
    example = sp.imresize(example, size=(args.downsamplesize, args.downsamplesize))
    example = example
    examples = np.repeat(example[:, :, np.newaxis], 12, axis=2)
    examples = np.moveaxis(examples, 2, 0)

    '''
    CREATE EXAMPLE WITH PATHS
    '''
    example_paths = [example_path]*12

    '''
    INIT MASK CREATOR
    '''
    mask_creator = MaskStackCreator(filament_width, mask_size, mask_width, angleStep, bright_background=True)
    mask_creator.init()

    '''
    DO ENHANCEMENT
    '''
    start = time.time()
    enhanced_images = line_enhancer.enhance_images(example_paths, mask_creator)
    end = time.time()
    print("Enhancement of 12 images")
    print("Enhancement time per image (first run)", (end - start) / 12)

    '''
    PLOT RESULT
    '''
    fig = plt.figure(figsize=(2, 2))
    fig.add_subplot(2,2,1)
    plt.imshow(enhanced_images[0]["max_value"])
    fig.add_subplot(2, 2, 2)
    plt.imshow(enhanced_images[0]["max_angle"])
    fig.add_subplot(2, 2, 3)
    plt.imshow(mask_creator.get_mask_stack()[0])
    fig.add_subplot(2, 2, 4)
    plt.imshow(mask_creator.get_mask_stack()[23])

    plt.show()
    #np.savetxt("/home/twagner/angle_image.txt",enhanced_images[0]["max_angle"])

    np.savetxt("/home/twagner/3200_enhanced.txt",enhanced_images[0]["max_angle"])


if __name__ == '__main__':
    _main_()