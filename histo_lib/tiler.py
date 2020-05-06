from abc import ABC, abstractmethod

import numpy as np

from .tile import Tile
from .utils import CoordinatePair, scale_coordinates
from .wsi import WSI


class Tiler(ABC):
    @abstractmethod
    def extract(self, wsi):
        raise NotImplementedError


class RandomTiler(Tiler):
    """
    Class for extracting random tiles from a WSI, at the given level, with the given size.

    Attributes
    ----------
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

    """

    def __init__(
        self,
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
        RandomTiler constructor.

        Parameters
        ----------
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

        """

        super().__init__()

        try:
            getattr(tile_size, "__len__")
            assert len(tile_size) == 2, "size should be integer or [size_w, size_h]"
            tile_w, tile_h = tile_size
        except AttributeError:
            tile_w = tile_h = int(tile_size)
        except AssertionError as ae:
            raise ae

        assert (
            max_iter >= n_tiles
        ), f"The maximum number of iterations must be grater than or equal to the maximum number of tiles. Got max_iter={max_iter} and n_tiles={n_tiles}."

        self.tile_size = (tile_w, tile_h)
        self.max_iter = max_iter
        self.level = level
        self.n_tiles = n_tiles
        self.seed = seed
        self.check_tissue = check_tissue
        self.prefix = prefix
        self.suffix = suffix

    def random_tiles_generator(self, wsi):
        """
        Generate Random Tiles within the tissue box of the wsi.

        Stops if:
        * the number of extracted tiles is equal to `n_tiles` OR
        * the maximum number of iterations `max_iter` is reached

        Parameters
        ----------
        wsi : WSI
            The Whole Slide Image from which to extract the tiles.

        Yields
        ------
        tile : Tile
            The extracted Tile
        coords : Coordinates
            The level-0 coordinates of the extracted tile

        """

        if self.check_tissue:
            box_coords_wsi = wsi.tissue_box_coords_wsi
        else:
            w_wsi, h_wsi = wsi.get_dimensions(level=0)
            box_coords_wsi = Coordinates(0, 0, w_wsi, h_wsi)

        if self.level != 0:
            box_coords_lvl = scale_coordinates(
                reference_coords=box_coords_wsi,
                reference_size=wsi.get_dimensions(level=0),
                target_size=wsi.get_dimensions(level=self.level),
            )
        else:
            box_coords_lvl = box_coords_wsi

        iteration = valid_tile_counter = 0
        tile_w_lvl, tile_h_lvl = self.tile_size

        while True:
            iteration += 1

            x_ul_lvl = np.random.randint(
                box_coords_lvl.x_ul, box_coords_lvl.x_br - (tile_w_lvl + 1),
            )
            y_ul_lvl = np.random.randint(
                box_coords_lvl.y_ul, box_coords_lvl.y_br - (tile_h_lvl + 1),
            )
            x_br_lvl = x_ul_lvl + tile_w_lvl
            y_br_lvl = y_ul_lvl + tile_h_lvl

            tile_wsi_coords = scale_coordinates(
                reference_coords=(x_ul_lvl, y_ul_lvl, x_br_lvl, y_br_lvl),
                reference_size=wsi.get_dimensions(level=self.level),
                target_size=wsi.get_dimensions(level=0),
            )

            tile = wsi.extract_tile(tile_wsi_coords, self.level)

            if not self.check_tissue or tile.has_enough_tissue():
                yield tile, tile_wsi_coords
                valid_tile_counter += 1

            if self.max_iter and iteration > self.max_iter:
                break

            if valid_tile_counter >= self.n_tiles:
                break

    def extract(self, wsi):
        """
        Extract tiles consuming `random_tiles_generator` and save them to disk,
        following this filename pattern:
            `{prefix}tile_{tiles_counter}_level{level}_{x_ul_wsi}-{y_ul_wsi}-{x_br_wsi}-{y_br_wsi}{suffix}`

        Raises
        ------
        TypeError
            If wsi is not an instance of WSI.

        """
        # TODO: manage alpha channel

        np.random.seed(self.seed)

        if not isinstance(wsi, WSI):
            raise TypeError("wsi must be of type WSI.")

        assert (
            self.level in wsi.levels
        ), f"Level {level} not available. Please select {', '.join(wsi.levels[:-1])} or {wsi.levels[-1]}"

        random_tiles = self.random_tiles_generator(wsi)

        tiles_counter = 0

        for tile, tile_wsi_coords in random_tiles:
            x_ul_wsi, y_ul_wsi, x_br_wsi, y_br_wsi = tile_wsi_coords
            tile_filename = f"{self.prefix}tile_{tiles_counter}_level{self.level}_{x_ul_wsi}-{y_ul_wsi}-{x_br_wsi}-{y_br_wsi}{self.suffix}"
            tile.save(tile_filename)
            print(f"\t Tile {tiles_counter} saved: {tile_filename}")
            tiles_counter += 1
        print(f"{tiles_counter} Random Tiles have been saved.")


class GridTiler(Tiler):
    pass
