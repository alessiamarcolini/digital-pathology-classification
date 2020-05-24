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

    def box_coords(self, wsi):
        """Return Coordinates at level 0 of the box to consider for tiles extraction.

        If `check_tissue` attribute is True, the Coordinates corresponds to the tissue box,
        otherwise they correspond to the original dimensions of the whole level 0.

        Parameters
        ----------
        wsi : WSI
            The WSI from which to extract the box coordinates

        Returns
        -------
        Coordinates
            Coordinates of the box

        """
        if self.check_tissue:
            return wsi.tissue_box_coords_wsi
        else:
            w_wsi, h_wsi = wsi.get_dimensions(level=0)
            return Coordinates(0, 0, w_wsi, h_wsi)

    def box_coords_lvl(self, wsi):
        """Return Coordinates at level `level` of the box to consider for tiles extraction.

        If `check_tissue` attribute is True, the Coordinates corresponds to the tissue box,
        otherwise they correspond to the original dimensions of the whole level.

        Parameters
        ----------
        wsi : WSI
            The WSI from which to extract the box coordinates

        Returns
        -------
        Coordinates
            Coordinates of the box

        """
        box_coords_wsi = self.box_coords(wsi)

        if self.level != 0:
            box_coords_lvl = scale_coordinates(
                reference_coords=box_coords_wsi,
                reference_size=wsi.get_dimensions(level=0),
                target_size=wsi.get_dimensions(level=self.level),
            )
        else:
            box_coords_lvl = box_coords_wsi

        return box_coords_lvl

    def random_tiles_generator(self, wsi):
        """
        Generate Random Tiles within a WSI box.

        If `check_tissue` attribute is True, the box corresponds to the tissue box,
        otherwise it corresponds to the whole level.

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

        iteration = valid_tile_counter = 0

        while True:
            iteration += 1

            tile_wsi_coords = self._random_tile_coordinates(wsi)

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

        for tiles_counter, (tile, tile_wsi_coords) in enumerate(random_tiles):
            tile_filename = self._tile_output_path(tile_wsi_coords, tiles_counter)
            tile.save(tile_filename)
            print(f"\t Tile {tiles_counter} saved: {tile_filename}")
        print(f"{tiles_counter} Random Tiles have been saved.")

    def _random_tile_coordinates(self, wsi):
        """Return random tile level-0 Coordinates within the tissue box.

        Parameters
        ----------
        wsi : WSI
            WSI from which calculate the coordinates.
            Needed to calculate the box.

        Returns
        -------
        Coordinates
            Random tile Coordinates at level 0
        """
        box_coords_lvl = self.box_coords_lvl(wsi)
        tile_w_lvl, tile_h_lvl = self.tile_size

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

        return tile_wsi_coords

    def _tile_output_path(self, tile_wsi_coords, tiles_counter):
        x_ul_wsi, y_ul_wsi, x_br_wsi, y_br_wsi = tile_wsi_coords
        tile_filename = f"{self.prefix}tile_{tiles_counter}_level{self.level}_{x_ul_wsi}-{y_ul_wsi}-{x_br_wsi}-{y_br_wsi}{self.suffix}"
        return tile_filename


class GridTiler(Tiler):
    pass
