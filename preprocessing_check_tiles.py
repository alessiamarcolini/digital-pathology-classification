import argparse

from preprocessing.check_tiles import check_tile, save_csv


def main():
    parser = argparse.ArgumentParser(description="Perform checks on the tiles")
    parser.add_argument(
        "tiles_filenames", type=str, nargs="+", help="Tiles filenames to be checked"
    )
    parser.add_argument(
        "csv_out_filename",
        type=str,
        help="Filename of the output csv with correct tiles only",
    )

    args = parser.parse_args()

    tiles_filenames = args.tiles_filenames
    csv_out_filename = args.csv_out_filename

    correct_tiles_filenames = filter(check_tile, tiles_filenames)
    save_csv({"filename": correct_tiles_filenames}, csv_out_filename)


if __name__ == "__main__":
    main()
