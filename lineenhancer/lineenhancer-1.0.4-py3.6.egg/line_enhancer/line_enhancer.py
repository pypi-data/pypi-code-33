import argparse
import numpy as np
import matplotlib.pyplot as plt
import mrcfile
import time
import sys
import multiprocessing
from maskstackcreator import MaskStackCreator
import scipy.misc as sp

#from pyfft.cuda import Plan
#import pycuda.driver as cuda
#from pycuda.tools import make_default_context
#import pycuda.gpuarray as gpuarray

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
    help='mask size')

argparser.add_argument(
    '-f',
    '--filamentwidth',
    default=16,
    type=int,
    help='filament with after downsampling')

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

    example_path = "/home/twagner/Actin-ADP-BeFx_0001_60e_DW.mrc"
    if args.input is not None:
        example_path = args.input
    mask_size = args.downsamplesize
    filament_width = args.filamentwidth
    mask_width = args.maskwidth
    angleStep = args.angle_step

    with mrcfile.open(example_path, permissive=True) as mrc:
        mrc_image_data = np.copy(mrc.data)
    example = np.flipud(mrc_image_data)

    '''
    RESIZE IMAGE, REPEAT IT 12 TIMES (simulates 12 input images)
    '''
    example = sp.imresize(example, size=(args.downsamplesize, args.downsamplesize))
    example = example
    examples = np.repeat(example[:, :, np.newaxis], 12, axis=2)
    examples = np.moveaxis(examples, 2, 0)


    '''
    INIT MASK CREATOR
    '''
    mask_creator = MaskStackCreator(filament_width, mask_size, mask_width, angleStep, bright_background=True)


    '''
    DO ENHANCEMENT
    '''
    start = time.time()
    enhanced_images = enhance_images(examples, mask_creator)
    end = time.time()
    print "Enhancement of 12 images"
    print "Enhancement time per image (first run)", (end - start) / 12

    start = time.time()
    enhanced_images = enhance_images(examples, mask_creator)
    end = time.time()
    print "Enhancement time per image (second run)", (end - start) / 12

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


def enhance_images(input_images, maskcreator):
    if input_images.shape[1] != maskcreator.get_mask_size() or input_images.shape[2] != maskcreator.get_mask_size():
        sys.exit("Mask and image dimensions are different. Stop")

    fft_masks = maskcreator.get_mask_fft_stack()

    global all_kernels
    all_kernels = fft_masks
    pool = multiprocessing.Pool()
    enhanced_images = pool.map(wrapper_fourier_stack, input_images)
    pool.close()
    pool.join()
    for img in enhanced_images:
        img["max_angle"] = img["max_angle"]*maskcreator.get_angle_step()

    return enhanced_images

def convolve(fft_image, fft_mask):

   # fft_mask = np.array(fft_mask)
    if len(fft_mask.shape) > 2:
        fft_image = np.expand_dims(fft_image, 2)
    result_fft = np.multiply(fft_mask, fft_image)
    result = np.fft.irfft2(result_fft, axes=(0, 1))
    result = np.fft.fftshift(result, axes=(0, 1))

    return result

all_kernels = None
def wrapper_fourier_stack(example):
    return enhance_image(fourier_kernel_stack=all_kernels,input_image=example)

def enhance_image(fourier_kernel_stack, input_image):
    input_image_fft = np.fft.rfft2(input_image)
    number_kernels = fourier_kernel_stack.shape[2]


    result = convolve(input_image_fft, fourier_kernel_stack[:, :, 0])
    enhanced_images = np.empty((result.shape[0], result.shape[1], number_kernels))
    enhanced_images[:, :, 0] = result
    for i in range(1,number_kernels):
        result = convolve(input_image_fft, fourier_kernel_stack[:, :, i])
        enhanced_images[:, :, i] = result

    max = np.amax(enhanced_images, axis=2)
    maxID = np.argmax(enhanced_images, axis=2)
    return {"max_value": max, "max_angle": maxID}


if __name__ == '__main__':
    _main_()