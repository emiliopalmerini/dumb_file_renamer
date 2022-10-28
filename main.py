import os
import glob
import os
import numpy as np
import imageio

from PIL import Image
from skimage.color import rgb2gray
from skimage.feature import canny
from skimage.morphology import dilation
from skimage.measure import label
from skimage.color import label2rgb
from scipy import ndimage as ndi
from skimage.measure import regionprops


def do_bboxes_overlap(a, b):
    return a[0] < b[2] and a[2] > b[0] and a[1] < b[3] and a[3] > b[1]


def merge_bboxes(a, b):
    return min(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3])


def are_bboxes_aligned(a, b, axis):
    return a[0 + axis] < b[2 + axis] and b[0 + axis] < a[2 + axis]


def cluster_bboxes(bboxes, axis=0):
    clus = []
    # Regroup bboxes which overlap along the current axis.
    # For instance, two panels on the same row overlap
    # along their verticial coordinate.
    for bbox in bboxes:
        for cluster in clus:
            if any(are_bboxes_aligned(b, bbox, axis=axis) for b in cluster):
                cluster.append(bbox)
                break
        else:
            clus.append([bbox])

    # We want rows to be ordered from top to bottom, and
    # columns to be ordered from left to right.
    clus.sort(key=lambda c: c[0][0 + axis])

    # For each row, we want to cluster the panels of that
    # row into columns, etc. etc.
    for i, cluster in enumerate(clus):
        if len(cluster) > 1:
            clus[i] = cluster_bboxes(bboxes=cluster, axis=1 if axis == 0 else 0)

    return clus


def flatten(l):
    for el in l:
        if isinstance(el, list):
            yield from flatten(el)
        else:
            yield el


def transform_image_in_regions(image):
    grayscale = rgb2gray(image)
    edges = canny(grayscale)
    thick_edges = dilation(dilation(edges))

    segmentation = ndi.binary_fill_holes(thick_edges)
    labels = label(segmentation)

    regions = regionprops(labels)

    return regions


def transform_regions_in_panels(regions):
    pans = []

    for region in regions:

        for i, panel in enumerate(pans):
            if do_bboxes_overlap(region.bbox, panel):
                pans[i] = merge_bboxes(panel, region.bbox)
                break
        else:
            pans.append(region.bbox)

    return pans


dir_name = "inputs"
list_of_files = sorted(filter(os.path.isfile, glob.glob(dir_name + "*")))

for i, im in enumerate(list_of_files):
    image = imageio.imread(im)
    regs = transform_image_in_regions(image)
    pans = transform_regions_in_panels(regs)
    for i, bbox in reversed(list(enumerate(pans))):
        area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
        if area < 0.01 * image.shape[0] * image.shape[1]:
            del pans[i]

    clusters = cluster_bboxes(pans)

    for i, bbox in enumerate(flatten(clusters)):
        panel = image[bbox[0] : bbox[2], bbox[1] : bbox[3]]
        Image.fromarray(panel).save(f"panels/vignetta_{i}.png")
