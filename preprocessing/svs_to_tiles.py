import os

import gin

from histo_lib import WSI, RandomTiler


@gin.configurable
def extract_random_tiles(
    wsi_filename,
    tile_size,
    n_tiles,
    level=0,
    seed=7,
    check_tissue=True,
    prefix="",
    suffix=".png",
    max_iter=1e4,
):
    """
    Extract random tiles from the WSI and save them to disk.

    Parameters
    ----------
    wsi_filename : str or pathlib.Path
        The filename of the wsi from which to extract the tiles.
    tile_size : int, tuple or list of int
        (width, height) of the extracted tiles.
    n_tiles : int
        Maximum number of tiles to extract.
    level : int
        Level from which extract the tiles. Default is 0.
    seed : int
        Seed for RandomState. Must be convertible to 32 bit unsigned integers. Default is 7.
    check_tissue : bool
        Whether to check if the tile has enough tissue to be saved. Default is True.
    prefix : str
        Prefix to be added to the tile filename. Default is an empty string.
    suffix : str
        Suffix to be added to the tile filename. Default is '.png'
    max_iter : int
        Maximum number of iterations performed when searching for eligible (if check_tissue=True) tiles.
        Must be grater than or equal to `n_tiles`.

    Raises
    ------
    FileNotFoundError
        If wsi_filename does not exist.
    IsADirectoryError
        If wsi_filename is a directory and not a file

    """
    if not os.path.exists(wsi_filename):
        raise FileNotFoundError(f"File {wsi_filename} does not exist.")
    if os.path.isdir(wsi_filename):
        raise IsADirectoryError(
            f"{wsi_filename} is a directory, while a file is needed."
        )

    wsi = WSI(wsi_filename)

    tiler = RandomTiler(
        tile_size, n_tiles, level, seed, check_tissue, prefix, suffix, max_iter
    )
    tiler.extract(wsi)
