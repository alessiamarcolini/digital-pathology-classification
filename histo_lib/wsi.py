import os
from collections import namedtuple
from pathlib import Path

import numpy as np
import openslide
import skimage.morphology as morph
from scipy import ndimage
from skimage import color
from skimage.filters import threshold_otsu
from skimage.measure import label, regionprops

from .tile import Tile
from .utils import CoordinatePair, scale_coordinates

Region = namedtuple("Region", ("index", "area", "bbox", "center"))


class WSI:
    def __init__(self, filename):
        assert os.path.exists(filename) and os.path.isfile(
            filename
        ), f"Make sure {filename} exists and it is a file."

        self.filename = Path(filename)
        self.image = openslide.open_slide(filename)

    @property
    def levels(self):
        return list(range(len(self.image.level_dimensions)))

    def get_dimensions(self, level=0):
        return self.image.level_dimensions[level]

    def info(self):
        """
        Print information about the image, such as 
        image dimensions, number of levels and corresponding mm per pixel.

        """
        prop = self.image.properties
        mpp_x = float(prop["openslide.mpp-x"])
        mpp_y = float(prop["openslide.mpp-y"])
        print(f"Image size:       {self.get_dimensions()}")
        print(f"Number of levels: {self.image.level_count}")
        print("Micron x:         {:.3f}".format(mpp_x))
        print("Micron y:         {:.3f}".format(mpp_y))

    def get_thumbnail(self, size):
        """
        Get image thumbnail.

        Parameters
        ----------
        size: int or array_like of int
            The size of the returned thumbnail

        Returns
        -------
        thumbnail: Openslide image
            The image thumbnail

        """
        # TODO: check for Sequence? ndarrays?
        if isinstance(size, list) or isinstance(size, tuple):
            assert len(size) == 2, f"Size shape should be (2,), got {len(size)}"
        elif isinstance(size, int):
            size = (size, size)
        else:
            raise TypeError(
                f"Size parameter must be a int or a Sequence, got {type(size)}"
            )

        return self.image.get_thumbnail(size)

    @property
    def tissue_box_coords_wsi(self):
        """
        Returns the coordinates of the box containing the tissue.
        
        Returns
        -------
        box_coords: Coordinates
            [x_ul, y_ul, x_br, y_br] coordinates of the box containing the tissue

        """

        w_out, h_out = self.get_dimensions(level=0)  # ! openslide image dimensions: WxH

        thumb = np.array(self.get_thumbnail(1000))
        h_in, w_in, ch = thumb.shape

        thumb = color.rgb2gray(thumb)
        thumb_threshold = threshold_otsu(thumb)
        thumb_filter = thumb < thumb_threshold
        strel = morph.disk(3)
        thumb_filter_dilated = morph.dilation(thumb_filter, strel)
        thumb_filter_dilated_filled = ndimage.binary_fill_holes(
            thumb_filter_dilated, structure=np.ones((5, 5))
        ).astype(int)

        # get biggest region
        thumb_labeled_regions = label(thumb_filter_dilated_filled)
        labeled_region_properties = regionprops(thumb_labeled_regions)

        regions = [
            Region(index=i, area=rp.area, bbox=rp.bbox, center=rp.centroid)
            for i, rp in enumerate(labeled_region_properties)
        ]
        biggest_region = max(regions, key=lambda r: r.area)
        y_ul, x_ul, y_br, x_br = biggest_region.bbox
        out_coords = scale_coordinates(
            reference_coords=(x_ul, y_ul, x_br, y_br),
            reference_size=(w_in, h_in),
            target_size=(w_out, h_out),
        )

        return out_coords

    def extract_tile(self, coords, level):
        """
        Extract a tile of the image, scaled to the selected level
        
        Parameters
        ----------
        coords : Coordinates
            Coordinates in the first level (0)
        level : int 
            Level from which to extract the tile
        
        Returns
        -------
        tile : Tile
            Image containing the selected tile

        """
        # TODO: check for Coordinates
        assert len(coords) == 4, "coords should be: (x_ul, y_ul, x_br, y_br)"
        assert level < len(
            self.image.level_dimensions
        ), f"this image has only {len(self.image.level_dimensions)} levels"

        coords_level = scale_coordinates(
            reference_coords=coords,
            reference_size=self.get_dimensions(level=0),
            target_size=self.get_dimensions(level=level),
        )

        h_l = coords_level.y_br - coords_level.y_ul
        w_l = coords_level.x_br - coords_level.x_ul

        patch = self.image.read_region(
            location=(coords[0], coords[1]), level=level, size=(w_l, h_l)
        )
        tile = Tile(patch, level, coords)
        return tile
