import os
from pathlib import Path

import numpy as np
import skimage.morphology as morph
from scipy import linalg, ndimage
from skimage import color
from skimage.filters import threshold_otsu
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

from .utils import CoordinatePair


class Tile:
    def __init__(self, image, level, coords):

        assert len(coords) == 4, "coords should be: [x_ul, y_ul, x_br, y_br]"
        # coords in level 0
        self._image = image
        self._level = level

        if not isinstance(coords, CoordinatePair):
            self.coords = CoordinatePair(*coords)
        else:
            self.coords = coords

    @property
    def image(self):
        return self._image

    @property
    def level(self):
        return self._level

    def has_enough_tissue(self, threshold=0.8, near_zero_var_threshold=0.1):
        """
        Check if the tile has enough tissue, based on `threshold` and `near_zero_var_threshold`.

        Parameters
        ----------
        threshold : float
            Number between 0.0 and 1.0 representing the minimum required proportion 
            of tissue over the total area of the image
        near_zero_var_threshold : float
            Minimum image variance after morphological operations (dilation, fill holes)
            
        Returns
        -------
        enough_tissue : bool
            Whether the image has enough tissue, i.e. if the proportion of tissue 
            over the total area of the image is more than `threshold` and the image variance
            after morphological operations is more than `near_zero_var_threshold`.

        """
        image_arr = np.array(self._image)
        image_gray = color.rgb2gray(image_arr)
        # Check if image is FULL-WHITE
        if (
            np.mean(image_gray.ravel()) > 0.9 and np.std(image_gray.ravel()) < 0.09
        ):  # full or almost white
            return False
        # Calculate the threshold of pixel-values corresponding to FOREGROUND
        # using Threshold-Otsu Method
        thresh = threshold_otsu(image_gray)
        # Filter out the Background
        image_bw = image_gray < thresh
        # Generate a Disk shaped filter of radius=5
        strel = morph.disk(5)
        # Generate Morphological Dilation, i.e. enlarge dark regions, shrinks dark regions
        image_bw_dilated = morph.dilation(image_bw, strel)
        # Fill holes in brightness based on a (minimum) reference structure to look for
        image_bw_filled = ndimage.binary_fill_holes(
            image_bw_dilated, structure=np.ones((5, 5))
        ).astype(np.uint8)

        # Near-zero variance threshold
        # This also includes cases in which there is ALL TISSUE (too clear) or NO TISSUE (zeros)
        if np.var(image_bw_filled) < near_zero_var_threshold:
            return False

        return np.mean(image_bw_filled) > threshold

    def save(self, path):
        """
        Save tile at given path. The format to use is determined from the filename
        extension (to be compatible to PIL.Image formats). 
        If no extension is provided, the image will be saved in png format.

        Arguments
        ---------
        path: str or pathlib.Path
            Path to which the tile is saved.

        """
        ext = os.path.splitext(path)[1]

        if not ext:
            path = f"{path}.png"

        Path(path).parent.mkdir(parents=True, exist_ok=True)

        self._image.save(path)

    @staticmethod
    def maxmin_norm(img):
        return (img - np.min(img)) / (np.max(img) - np.min(img))

    def invert_grays(self):
        return -1 * (self._image - np.max(self._image))

    def is_grayscale(self):
        h_r = np.histogram(self._image[:, :, 0].ravel(), bins=np.arange(0, 256))
        h_g = np.histogram(self._image[:, :, 1].ravel(), bins=np.arange(0, 256))
        h_b = np.histogram(self._image[:, :, 2].ravel(), bins=np.arange(0, 256))
        return np.all(h_r[0] == h_g[0]) and np.all(h_r[0] == h_b[0])

    # color processing

    # dummy white balance
    def balance_white(self):
        # simple white balance: the maximum value of each image should be white
        img_balanced = np.zeros_like(self._image)
        img_balanced[:, :, 0] = (
            self._image[:, :, 0] / np.max(self._image[:, :, 0].ravel()) * 255.0
        )
        img_balanced[:, :, 1] = (
            self._image[:, :, 1] / np.max(self._image[:, :, 1].ravel()) * 255.0
        )
        img_balanced[:, :, 2] = (
            self._image[:, :, 2] / np.max(self._image[:, :, 2].ravel()) * 255.0
        )
        return img_balanced

    # deconvolution
    def detect_colors(self, n_colors=3, method="kmeans"):
        assert method in ["PCA", "kmeans"]
        img = self.maxmin_norm(self._image)
        img_l = img.reshape((img.shape[0] * img.shape[1], img.shape[2]))

        if method == "PCA":
            assert n_colors <= 3, "Maximum 3 n_colors when using PCA"
            clt = PCA(n_components=n_colors)
            clt.fit(img_l)
            colors = clt.components_
            return colors

        elif method == "kmeans":
            clt = KMeans(n_clusters=n_colors)
            clt.fit(img_l)
            colors = clt.cluster_centers_
            return colors

    @staticmethod
    def find_color_base(color_1, color_2=np.array([255, 255, 255])):
        def normalize_vector(v):
            norm = np.sqrt(np.sum(v ** 2))
            return v / norm

        color_1_n = normalize_vector(color_1)
        color_2_n = normalize_vector(color_2)
        color_3_n = normalize_vector(np.cross(color_1_n, color_2_n))

        colors_norm = np.vstack([color_1_n, color_2_n, color_3_n])

        return colors_norm

    @staticmethod
    def _colorize_image(img, color):
        img_stacked = np.stack([img, img, img], axis=2)

        img_tinted = color * img_stacked
        return img_tinted

    def separate_colors(self, colors, colorize=True):
        colors_new = np.vstack([colors, colors[0, :]])
        stain_images = []
        for id_col in range(colors.shape[0]):
            color_1 = colors_new[id_col, :]
            color_2 = colors_new[id_col + 1, :]
            colors_base = self.find_color_base(color_1, color_2)
            color_matrix = linalg.inv(colors_base)

            separated = color.separate_stains(self._image, color_matrix)
            separated_main = separated[:, :, 0]
            separated_main = self.maxmin_norm(separated_main)

            if colorize:
                separated_main = self._colorize_image(separated_main, color_1)

            stain_images.append(separated_main)

        return stain_images
