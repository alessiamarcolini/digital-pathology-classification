from collections import namedtuple

import numpy as np

CoordinatePair = namedtuple("CoordinatePair", ("x_ul", "y_ul", "x_br", "y_br"))


def scale_coordinates(reference_coords, reference_size, target_size):
    """
    Compute the coordinates corresponding to a scaled version of the image.
    
    Parameters
    ----------
    reference_coords: tuple, array-like or Coordinates
        (x, y) pair of coordinates referring to the upper left and lower right corners respectively.
        The function expects a tuple of four elements or a tuple of two pairs of coordinates as input.
    reference_size: array_like of int
        Reference (width, height) size to which input coordinates refer to
    target_size: array_like of int
        Target (width, height) size of the resulting scaled image
    
    Returns
    -------
    coords: Coordinates
        Coordinates in the scaled image
        
    """
    assert len(reference_size) == 2
    assert len(target_size) == 2
    assert len(reference_coords) == 4

    reference_coords = np.asarray(reference_coords).ravel()
    reference_size = np.tile(reference_size, 2)
    target_size = np.tile(target_size, 2)
    return CoordinatePair(
        *np.floor((reference_coords * target_size) / reference_size).astype("int64")
    )
