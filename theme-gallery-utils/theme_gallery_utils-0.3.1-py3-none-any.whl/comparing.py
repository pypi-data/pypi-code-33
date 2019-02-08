# -*- coding: utf-8 -*-

"""
Module for creating image histograms.
"""

import datetime
import logging
import os
import subprocess

logger = logging.getLogger(__name__)


def compare_args(new_dir, old_dir, output_dir, image, metric=False):
    """Return the compare arguments to be executed."""

    new_image = os.path.join(new_dir, image)
    old_image = os.path.join(old_dir, image)
    output_image = os.path.join(output_dir, image)

    if metric:
        args = [
            "compare",
            "-metric",
            "AE",
            new_image,
            old_image,
            "null:",
        ]
    else:
        args = [
            "compare",
            new_image,
            old_image,
            "-compose",
            "src",
            output_image,
        ]

    return args


def find_images(new_dir, old_dir):
    """Return a list of paired image full paths."""

    new_images = [i for i in os.listdir(new_dir) if i.endswith(".png")]
    old_images = [i for i in os.listdir(old_dir) if i.endswith(".png")]

    paired = []
    unpaired = []
    for image in new_images:
        if image in old_images:
            paired.append(image)
        else:
            unpaired.append(image)

    return sorted(paired), sorted(unpaired)


def write_report(image_dict, output_dir):
    """Write a report of the image differences for later reference."""

    start_divider = "=" * 80
    end_divider = "-" * 80

    def format_category(name, items):
        """Create a string representation of the category."""
        body = "\n".join(items)
        return "\n".join(
            [
                name,
                start_divider,
                body,
                end_divider,
            ]
        )

    with open(os.path.join(output_dir, "compare_report.txt"), "w") as buf:
        buf.write(datetime.datetime.now().isoformat())
        for key, value in image_dict.items():
            buf.write("\n\n")
            buf.write(format_category(key, value))
        buf.write("\n")


def compare_images(compressed_dir, gallery_dir, output_dir):
    """Check the image directories and create histograms of the differences."""

    # ensure output dir exists
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    # find images that are paired by name
    paired_images, unpaired_images = find_images(compressed_dir, gallery_dir)

    # create image category dict
    image_dict = {
        "paired": paired_images,
        "unpaired": unpaired_images,
        "changed": [],
        "unchanged": [],
        "resized": [],
    }

    for image in paired_images:

        # run compare to check if images are identical
        output = subprocess.run(
            compare_args(
                compressed_dir,
                gallery_dir,
                output_dir,
                image,
                metric=True
            ),
            stderr=subprocess.PIPE
        ).stderr.decode()

        if output == "0":
            logger.debug("Image is unchanged: {}".format(image))
            image_dict["unchanged"].append(image)
        elif "image widths or heights differ" in output:
            logger.debug("Image has been resized: {}".format(image))
            image_dict["resized"].append(image)
        else:
            logger.debug("Image has changed: {}".format(image))
            image_dict["changed"].append(image)

            # create the histogram
            subprocess.run(
                compare_args(compressed_dir, gallery_dir, output_dir, image))

    # write list of images to the report file
    write_report(image_dict, output_dir)
