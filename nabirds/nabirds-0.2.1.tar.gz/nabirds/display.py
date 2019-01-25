#!/usr/bin/env python
if __name__ != '__main__': raise Exception("Do not import me!")

from argparse import ArgumentParser
import logging
import numpy as np

from annotations import NAB_Annotations, CUB_Annotations
from dataset import Dataset
from dataset.utils import reveal_parts, uniform_parts, \
	random_select, \
	visible_part_locs, visible_crops


import matplotlib.pyplot as plt

def init_logger(args):
	fmt = "%(levelname)s - [%(asctime)s] %(filename)s:%(lineno)d [%(funcName)s]: %(message)s"
	logging.basicConfig(
		format=fmt,
		level=getattr(logging, args.loglevel.upper(), logging.DEBUG),
		filename=args.logfile or None,
		filemode="w")

def plot_crops(crops, title, scatter_mid=False):

	fig = plt.figure(figsize=(16,9))
	fig.suptitle(title, fontsize=16)

	n_crops = crops.shape[0]
	rows = int(np.ceil(np.sqrt(n_crops)))
	cols = int(np.ceil(n_crops / rows))

	for j, crop in enumerate(crops, 1):
		ax = fig.add_subplot(rows, cols, j)
		ax.imshow(crop)
		ax.axis("off")
		if scatter_mid:
			middle_h, middle_w = crop.shape[0] / 2, crop.shape[1] / 2
			ax.scatter(middle_w, middle_h, marker="x")



def main(args):
	init_logger(args)

	annotation_cls = dict(
		nab=NAB_Annotations,
		cub=CUB_Annotations)

	logging.info("Loading \"{}\" annnotations from \"{}\"".format(args.dataset, args.data))
	annot = annotation_cls.get(args.dataset.lower())(args.data)

	subset = args.subset.lower()

	uuids = getattr(annot, "{}_uuids".format(subset))
	features = args.features[0 if subset == "train" else 1]

	data = Dataset(
		uuids=uuids, annotations=annot,
		features=features,

		uniform_parts=args.uniform_parts,

		crop_to_bb=args.crop_to_bb,
		crop_uniform=args.crop_uniform,

		parts_in_bb=args.parts_in_bb,

		rnd_select=args.rnd,
		ratio=args.ratio,
		seed=args.seed

	)
	n_images = len(data)
	logging.info("Found {} images in the {} subset".format(n_images, subset))

	for i in range(n_images):
		if i + 1 <= args.start: continue
		im, parts, label = data[i]

		idxs, xy = visible_part_locs(parts)
		part_crops = visible_crops(im, parts, ratio=args.ratio)
		if args.rnd:
			selected = parts[:, -1].astype(bool)
			parts[selected, -1] = 0
			parts[np.logical_not(selected), -1] = 1
			action_crops = visible_crops(im, parts, ratio=args.ratio)

		logging.debug(label)
		logging.debug(idxs)
		logging.debug(xy)

		fig1 = plt.figure(figsize=(16,9))
		ax = fig1.add_subplot(2,1,1)
		ax.imshow(im)
		ax.set_title("Visible Parts")
		ax.scatter(*xy, marker="x", c=idxs)
		ax.axis("off")

		ax = fig1.add_subplot(2,1,2)
		ax.set_title("{}selected parts".format("randomly " if args.rnd else ""))
		ax.imshow(reveal_parts(im, xy, ratio=args.ratio))
		# ax.scatter(*xy, marker="x", c=idxs)
		ax.axis("off")

		plot_crops(part_crops, "Selected parts")

		if args.rnd:
			plot_crops(action_crops, "Actions")

		plt.show()
		plt.close()

		if i+1 >= args.start + args.n_images: break

parser = ArgumentParser()

parser.add_argument("data",
	help="Folder containing the dataset with images and annotation files",
	type=str)

parser.add_argument("--dataset",
	help="Possible datasets: NAB, CUB",
	choices=["cub", "nab"],
	default="nab", type=str)

parser.add_argument("--features",
	help="pre-extracted train and test features",
	default=[None, None],
	nargs=2, type=str)

parser.add_argument("--subset",
	help="Possible subsets: train, test",
	choices=["train", "test"],
	default="train", type=str)

parser.add_argument("--start", "-s",
	help="Image id to start with",
	type=int, default=0)

parser.add_argument("--n_images", "-n",
	help="Number of images to display",
	type=int, default=10)

parser.add_argument("--ratio",
	help="Part extraction ratio",
	type=float, default=.2)

parser.add_argument("--rnd",
	help="select random subset of present parts",
	action="store_true")

parser.add_argument("--uniform_parts", "-u",
	help="Do not use GT parts, but sample parts uniformly from the image",
	action="store_true")

parser.add_argument("--crop_to_bb",
	help="Crop image to the bounding box",
	action="store_true")

parser.add_argument("--crop_uniform",
	help="Try to extend the bounding box to same height and width",
	action="store_true")

parser.add_argument("--parts_in_bb",
	help="Only display parts, that are inside the bounding box",
	action="store_true")



parser.add_argument(
	'--logfile', type=str, default='',
	help='File for logging output')

parser.add_argument(
	'--loglevel', type=str, default='INFO',
	help='logging level. see logging module for more information')

parser.add_argument(
	'--seed', type=int, default=12311123,
	help='random seed')

main(parser.parse_args())
