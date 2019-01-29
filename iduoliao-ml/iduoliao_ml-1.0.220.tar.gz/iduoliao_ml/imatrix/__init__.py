#! /usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np

def inOneDivOffStray(mats, ratio=0.5):
	maxOffStrays = maxOffStray(mats, ratio)
	maxOffStrays[maxOffStrays == 0] = 1
	mats = np.true_divide(mats, maxOffStrays)
	mats[mats > 1] = 1
	return mats

def inOneDiv(mats):
	return np.true_divide(mats, np.max(mats, axis=0))

def inOne(mats):
	col = mats.shape[0]
	matAvg = mats.mean(axis=0)
	matDiff = mats - matAvg
	matDiffSumAvg = np.square(matDiff).mean(axis=0)
	vari = np.sqrt(matDiffSumAvg)
	z = matDiff / vari
	zNoNaN = np.mat(np.where(np.isnan(z), np.mat(np.zeros((col, mats.shape[1]))), z))
	return sigmoid(zNoNaN)

def sigmoid(mats):
	return 1 / (1 + np.exp(-mats))

def maxOffStray(mats, ratio=0.05):
	maxOffStrays = np.mat([])

	[row, col] = mats.shape
	offCount = int(row * ratio)
	for j in range(col):
		maxOffStrays = np.hstack((maxOffStrays, sorted(mats[:, j], key=lambda item: item[0], reverse=True)[offCount]))

	return maxOffStrays

