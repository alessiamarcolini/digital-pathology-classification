import argparse
import os
from pathlib import Path

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


if __name__ == "__main__":
    accepted_extraction_modes = ["random"]

    parser = argparse.ArgumentParser(description="Extract random tiles from a WSI")
    parser.add_argument("wsi_filename", type=str, help="Filename of the WSI")
    parser.add_argument(
        "output_folder", type=str, help="Folder in which to save the tiles"
    )
    parser.add_argument(
        "extraction_mode",
        type=str,
        help=f"Tiles extraction mode. Available options: {', '.join(accepted_extraction_modes)}",
    )

    args = parser.parse_args()
    wsi_filename = args.wsi_filename
    output_folder = Path(args.output_folder)
    extraction_mode = args.extraction_mode

    output_folder.parent.mkdir(parents=True, exist_ok=True)

    assert (
        extraction_mode in accepted_extraction_modes
    ), f"Extraction mode {extraction_mode} not available. Accepted values: {', '.join(accepted_extraction_modes)}"

    current_directory = Path(os.path.abspath(os.path.dirname(__file__)))
    gin.parse_config_file(current_directory / "preprocessing_config.gin")

    wsi_filename_no_ext = os.path.splitext(os.path.basename(wsi_filename))[0]

    extract_random_tiles(wsi_filename, prefix=f"{output_folder}/{wsi_filename_no_ext}_")
