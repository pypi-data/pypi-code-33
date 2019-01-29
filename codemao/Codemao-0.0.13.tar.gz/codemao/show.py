import hashlib
import os
import sys

import matplotlib.pyplot as plt
import matplotlib.image as mpimg


def show_image():
    md5 = hashlib.md5()
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        raise TypeError("No path found in this image")
    md5.update(image_path.encode("utf-8"))
    figure_name = os.path.basename(image_path) + md5.hexdigest()
    img = mpimg.imread(image_path)
    plt.figure(figure_name)
    plt.axis("off")
    plt.imshow(img)
    plt.show()

if __name__ == "__main__":
    show_image()
