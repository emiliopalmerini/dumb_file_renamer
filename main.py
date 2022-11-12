import glob
import numpy as np
import imageio.v2 as imageio
import PIL as PIL

from PIL import Image
from skimage.color import rgb2gray
from skimage.feature import canny
from skimage.morphology import dilation
from skimage.measure import label
from skimage.color import label2rgb
from scipy import ndimage as ndi
from skimage.measure import regionprops
import sys

sys.setrecursionlimit(15000000)


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
        for f, panel in enumerate(pans):
            if do_bboxes_overlap(region.bbox, panel):
                pans[f] = merge_bboxes(panel, region.bbox)
                break
        else:
            pans.append(region.bbox)

    return pans


def remove_too_small_pans(panels, image):
    for k, bbox in reversed(list(enumerate(pans))):
        area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
        if area < 0.01 * image.shape[0] * image.shape[1]:
            del panels[k]


def save_opt_image(img, n, f="webp", q=10):
    Image.fromarray(img).save(
        n,
        format=f,
        quality=q,
    )


dir_name = "./inputs/"
list_of_files = sorted(glob.glob(dir_name + "*"))  # filter(os.path.isfile,)


for i, file in enumerate(list_of_files):
    numero_tavola = file.split("/")[-1].split("_")[1]
    numero_episodio = file.split("/")[-1].split("_")[3]
    numero_capitolo = file.split("/")[-1].split(".")[0].split("_")[-1]
    image = imageio.imread(file)
    table_name = f"./outputs/compressed_tables/tavola_{numero_tavola}_episodio_{numero_episodio}_capitolo_{numero_capitolo}.webp"
    save_opt_image(image, table_name, "webp", 25)
    regs = transform_image_in_regions(image)
    pans = transform_regions_in_panels(regs)
    remove_too_small_pans(pans, image)

    clusters = cluster_bboxes(pans)

    for p, bbox in enumerate(flatten(clusters)):
        panel = image[bbox[0] : bbox[2], bbox[1] : bbox[3]]
        panel_name = f"./outputs/panels/tavola_{numero_tavola}_vignetta_{p}_episodio_{numero_episodio}_capitolo_{numero_capitolo}.webp"
        save_opt_image(panel, panel_name)
