import cv2
import sys
import pickle
import os
import time
import numpy as np
from utils import TEST_PATH, h, w, NUM_OF_WORDS, Utils
from torch import nn, optim
import torch

cv2.setUseOptimized(True)
cv2.setNumThreads(4)

def freq(curr_labels):
	# print(curr_labels.shape)
	try:
		hist = np.bincount(curr_labels, minlength=NUM_OF_WORDS)
	except:
		hist = np.bincount(np.zeros(0, dtype=np.int64), minlength=NUM_OF_WORDS)
	return hist

def getQueryVec(flow, centers):
	dists = np.zeros((centers.shape[0], flow.shape[0]))
	dists = np.sqrt((flow**2).sum(axis=1)[:, np.newaxis] + (centers**2).sum(axis=1) - 2 * flow.dot(centers.T))
	labels = np.argmin(dists, axis=1)
	query_vector = freq(labels)
	query_vector = query_vector/(np.linalg.norm(query_vector)+1e-10)
	return query_vector

def test():

	util = Utils()
	util.generate_patches()

	with open('clf.pkl', 'rb') as f:
		clf = pickle.load(f)
	
	with open('centers.pkl', 'rb') as f:
		centers = pickle.load(f)    

	correct = 0
	incorrect = 0
	for i, folder in enumerate(sorted(os.listdir(TEST_PATH))):
		print('Working on folder:', folder)
		imgs = []
		for j, files in enumerate(sorted(os.listdir(os.path.join(TEST_PATH,folder)))):
			img = cv2.imread(os.path.join(TEST_PATH,folder,files))
			gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
			resized = cv2.resize(gray,(982, 552))
			imgs.append(resized)
			
		imgs2 = [np.fliplr(img) for img in imgs]

		flow = util.optical_flow(imgs)
		if flow.shape[0] > 0:
			query_vector = getQueryVec(flow, centers).reshape(1, -1)
			pred = clf.predict(query_vector)
			if pred == 1 and folder[0] == 'F':
				correct += 1
			elif pred == -1 and folder[0] != 'F':
				correct += 1
			else:
				incorrect += 1

		print(correct, incorrect)
		
		flow = util.optical_flow(imgs2)
		if flow.shape[0] > 0:
			query_vector = getQueryVec(flow, centers).reshape(1, -1) 
			pred = clf.predict(query_vector)
			if pred == 1 and folder[0] == 'F':
				correct += 1
			elif pred == -1 and folder[0] != 'F':
				correct += 1
			else:
				incorrect += 1

		print(correct, incorrect)

		flow = util.optical_flow(imgs[::-1])
		if flow.shape[0] > 0:
			query_vector = getQueryVec(flow, centers).reshape(1, -1) 
			pred = clf.predict(query_vector)
			if pred == -1 and folder[0] == 'F':
				correct += 1
			elif pred == 1 and folder[0] != 'F':
				correct += 1
			else:
				incorrect += 1

		print(correct, incorrect)

		flow = util.optical_flow(imgs2[::-1])
		if flow.shape[0] > 0:
			query_vector = getQueryVec(flow, centers).reshape(1, -1)
			pred = clf.predict(query_vector)
			if pred == -1 and folder[0] == 'F':
				correct += 1
			elif pred == 1 and folder[0] != 'F':
				correct += 1
			else:
				incorrect += 1

		print(correct, incorrect)

		acc = correct/(correct + incorrect)
		print("Testing Accuracy after " + str(i) + "th video: " + str(acc))             


if __name__ == '__main__':

	with open('clf.pkl', 'rb') as f:
		clf = pickle.load(f)
	
	with open('test_data.pkl', 'rb') as f:
		X = pickle.load(f)[:, 0, :]

	with open('test_labels.pkl', 'rb') as f:
		Y = pickle.load(f)

	print(np.sum(clf.predict(X)==Y)/X.shape[0])
	
	# test()