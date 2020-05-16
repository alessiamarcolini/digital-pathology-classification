import argparse
import os

from preprocessing.check_tiles import check_tile, save_csv
from preprocessing.tcga_utils import (
    tile_filename_to_wsi_filename,
    wsi_filename_to_patient,
    wsi_filename_to_wsi_id,
)


def main():
    parser = argparse.ArgumentParser(description="Perform checks on the tiles")
    parser.add_argument(
        "tiles_paths", type=str, nargs="+", help="Tiles paths to be checked"
    )
    parser.add_argument(
        "csv_out_filename",
        type=str,
        help="Filename of the output csv with correct tiles only",
    )

    args = parser.parse_args()

    tiles_paths = args.tiles_paths
    csv_out_filename = args.csv_out_filename

    correct_tiles_paths = filter(check_tile, tiles_paths)
    correct_tiles_filenames = list(map(os.path.basename, correct_tiles_paths))

    correct_wsi_filenames = list(
        map(tile_filename_to_wsi_filename, correct_tiles_filenames)
    )

    correct_patients = list(map(wsi_filename_to_patient, correct_wsi_filenames))
    correct_wsi_ids = list(map(wsi_filename_to_wsi_id, correct_wsi_filenames))

    csv_data = {
        "filename": correct_tiles_filenames,
        "patient": correct_patients,
        "wsi_id": correct_wsi_ids,
    }

    save_csv(
        csv_data, csv_out_filename,
    )


if __name__ == "__main__":
    main()
