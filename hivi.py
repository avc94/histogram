# Histogram vision

import numpy as np
import cv2
import csv


class ColorDescriptor:
    def __init__(self, bins):
        # store the number of bins for the 3D histogram
        self._bins = bins

    def describe(self, image):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        h, w = image.shape[:2]
        c_x, c_y = int(w * 0.5), int(h * 0.5)  # center x, y
        features = []
        corner_mask = np.zeros(image.shape[:2], dtype="uint8")

        # loop over the segments
        # list contains coordinates for 4 image rectangle segments corners
        for (start_x, start_y, end_x, end_y) in [(0, 0, c_x, c_y), (c_x, 0, w, c_y), (0, c_y, c_x, h), (c_x, c_y, w, h)]:
            # construct a mask for each corner of the image, subtracting
            corner_mask.fill(0)
            cv2.rectangle(corner_mask, (start_x, start_y), (end_x, end_y), 255, -1)
            features.extend(self.histogram(image, corner_mask))

        return features

    def histogram(self, image, mask):
        """Extract a 3D color histogram from the masked region of the
        image, using the supplied number of bins per channel; then
        normalize the histogram"""

        hist = cv2.calcHist([image], [0, 1, 2], mask, self._bins, [0, 180, 0, 256, 0, 256])
        return cv2.normalize(hist, hist).flatten()


class Searcher:
    def __init__(self, indexes_path):
        self._indexes_path = indexes_path
        self._indexes = {}
        self._load_indexes()

    def _load_indexes(self):
        with open(self._indexes_path) as file:
            reader = csv.reader(file)
            for row in reader:
                self._indexes[row[0]] = [float(x) for x in row[1:]]

    def search_best(self, query_features):
        result = ["Init value", float('inf')]
        # loop over indexes DB and find lesser distance between query and records
        # lesser dist means more 'similar' images
        for key in self._indexes:
            d = self.chi2_distance(self._indexes[key], query_features)
            if d < result[1]:
                result[0], result[1] = key, d

        return result

    def chi2_distance(self, hist_a, hist_b, eps=1e-10):
        # compute the chi-squared distance
        return 0.5 * np.sum([((a - b) ** 2) / (a + b + eps) for (a, b) in zip(hist_a, hist_b)])
