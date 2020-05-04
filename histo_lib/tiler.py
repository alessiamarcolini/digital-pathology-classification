from abc import ABC, abstractmethod

import numpy as np

from .tile import Tile
from .util import CoordinatePair, scale_coordinates


class Tiler(ABC):
    @abstractmethod
    def extract(self, image):
        raise NotImplementedError


class RandomTiler(Tiler):
    def __init__(
        self,
        wsi,
        tile_size,
        n_tiles,
        level=0,
        seed=7,
        check_tissue=True,
        prefix="",
        suffix=".png",
        max_iter=1e4,
    ):
        super().__init__()
        np.random.seed(seed)
        self.wsi = wsi

        try:
            getattr(tile_size, "__len__")
            assert len(tile_size) == 2, "size should be integer or [size_w, size_h]"
            tile_w, tile_h = tile_size
        except AttributeError:
            tile_w = tile_h = int(tile_size)
        except AssertionError as ae:
            raise ae

        self.tile_size = tile_size

        assert (
            level in self.wsi.levels
        ), f"Level {level} not available. Please select {', '.join(self.wsi.levels[:-1])} or {self.wsi.levels[-1]}"

        self.level = level
        self.n_tiles = n_tiles
        self.seed = seed
        self.check_tissue = check_tissue
        self.prefix = prefix
        self.suffix = suffix
        self.max_iter = max_iter

        if check_tissue:
            self.box_coords_wsi = self.wsi.tissue_box_coords_wsi
        else:
            w_wsi, h_wsi = self.wsi.get_dimensions(level=0)
            self.box_coords_wsi = Coordinates(0, 0, w_wsi, h_wsi)

        if level != 0:
            self.box_coords_lvl = scale_coordinates(
                reference_coords=self.box_coords_wsi,
                reference_size=self.wsi.get_dimensions(level=0),
                target_size=self.wsi.get_dimensions(level=level),
            )
        else:
            self.box_coords_lvl = self.box_coords_wsi

    def random_tiles_generator(self):
        """
        
        """

        iteration = valid_tile_counter = 0
        tile_w_lvl, tile_h_lvl = self.tile_size

        fake_tile_coords_lvl = CoordinatePair(0, 0, tile_w_lvl, tile_h_lvl)
        print(fake_tile_coords_lvl)

        fake_tile_coords_wsi = scale_coordinates(
            reference_coords=fake_tile_coords_lvl,
            reference_size=self.wsi.get_dimensions(level=self.level),
            target_size=self.wsi.get_dimensions(level=0),
        )

        tile_w_wsi = fake_tile_coords_wsi.x_br
        tile_h_wsi = fake_tile_coords_wsi.y_br

        print(fake_tile_coords_wsi)

        tissue_box_coords_wsi = self.box_coords_wsi

        while True:
            iteration += 1

            x_ul_wsi = np.random.randint(
                tissue_box_coords_wsi.x_ul,
                tissue_box_coords_wsi.x_br - (tile_w_wsi + 1),
            )
            y_ul_wsi = np.random.randint(
                tissue_box_coords_wsi.y_ul,
                tissue_box_coords_wsi.y_br - (tile_w_wsi + 1),
            )
            x_br_wsi = x_ul_wsi + tile_w_wsi
            y_br_wsi = y_ul_wsi + tile_w_wsi

            tile_wsi_coords = CoordinatePair(x_ul_wsi, y_ul_wsi, x_br_wsi, y_br_wsi)

            tile = self.wsi.extract_tile(tile_wsi_coords, self.level)

            if not self.check_tissue or tile.has_enough_tissue():
                yield tile, tile_wsi_coords
                valid_tile_counter += 1

            if self.max_iter and iteration > self.max_iter:
                break

            if valid_tile_counter >= self.n_tiles:
                break

    def extract(self):
        """
        """
        # TODO: manage alpha channel

        random_tiles = self.random_tiles_generator()

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
