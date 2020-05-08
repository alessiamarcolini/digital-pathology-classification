import argparse
import os
from pathlib import Path

import gin
import numpy as np
import pandas as pd
from PIL import Image, UnidentifiedImageError


def check_image_readable(tile_filename):
    """
    Check that `tile_filenames` corresponds to an image readable by PIL and converts it to "RGB"

    Parameters
    ----------
    tile_filename : str or pathlib.Path
        Path to the tile to be tested

    Returns
    -------
    PIL.Image
        Image read and converted to "RGB"

    Raises
    ------
    FileNotFoundError
        If the file cannot be found
    UnidentifiedImageError
        If the image cannot be opened and identified.
    ValueError
        If a `StringIO` instance is used for `tile_filename`.
    
    """

    return Image.open(tile_filename).convert("RGB")


@gin.configurable
def check_tile_shape(image, tile_size):
    """
    Check that the tile provided has `tile_size` shape.

    Parameters
    ----------
    image: PIL.Image
        The image to be tested
    tile_size : int or tuple/list of int of shape (2,)
        (width, height) requested for the tile or a single int value if width == height 

    Raises
    ------
    ValueError
        If `tile_size` is a sequence but doesn't have two elements (one or more than two)
    ValueError
        If the tile shape is different from `tile_size`

    """
    try:
        getattr(tile_size, "__len__")
        assert len(tile_size) == 2, "size should be integer or [size_w, size_h]"
        tile_w, tile_h = tile_size
    except AttributeError:
        tile_w = tile_h = int(tile_size)
    except AssertionError as ae:
        raise ValueError from ae

    im_array = np.array(image)
    if im_array.shape != (tile_w, tile_h, 3):
        raise ValueError(
            f"Tile shape is incorrect: {im_array.shape} instead of ({tile_w}, {tile_h}, 3)"
        )


def check_tile_uint8(image):
    """
    Check that the tile provided is of dtype uint8.

    Parameters
    ----------
    image: PIL.Image
            The image to be tested

    Raises
    ------
    TypeError
        If the tile dtype is different from uint8

    """

    im_array = np.array(image)
    if im_array.dtype != "uint8":
        raise TypeError(f'Data type is incorrect: {im_array.dtype} instead of "uint8"')


def check_tile_values_range(image):
    """
    Check that the values of the tile provided range from 0 to 255.

    Parameters
    ----------
    image: PIL.Image
        The image to be tested

    Raises
    ------
    ValueError
        If the values of the tile are not between 0 and 255

    """

    im_array = np.array(image)
    if not ((im_array >= 0).all() and (im_array <= 255).all()):
        raise ValueError("Pixel values should be between 0 and 255")


def check_tile(tile_filename):
    """
    Performs checks on the tile:
    * if the tile is readable
    * if the tile has the correct shape
    * if the tile has the correct dtype
    * if the pixel values of the tile are in the correct range

    Parameters
    ----------
    tile_filename : [type]
        [description]

    Returns
    -------
    bool
        True if the tile is compliant with all the checks, False otherwise
        
    """
    try:
        image = check_image_readable(tile_filename)

        check_tile_shape(image)
        check_tile_uint8(image)
        check_tile_values_range(image)

    except (FileNotFoundError, UnidentifiedImageError, ValueError, TypeError) as e:
        print(e)
        return False

    else:
        return True


def save_csv(data, filename):
    """
    Save provided `data` as a csv at `filename`

    Parameters
    ----------
    data : ndarray (structured or homogeneous), Iterable, dict, or DataFrame
        Dict can contain Series, arrays, constants, or list-like objects. 
    filename : str or pathlib.Path
        Where to save the csv

    """
    csv_out = pd.DataFrame(data)
    csv_out.to_csv(filename, index=False)
