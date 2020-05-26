import argparse
import shutil
from pathlib import Path

import pandas as pd
from tqdm import tqdm


def main(
    tiles_dirs, valid_tiles_summaries_path, output_tiles_folder, valid_tiles_csv_path,
):
    output_tiles_folder.mkdir(parents=True, exist_ok=True)

    summaries = []
    for tile_dir, summary_path in tqdm(
        zip(tiles_dirs, valid_tiles_summaries_path), total=len(tiles_dirs)
    ):
        summary = pd.read_csv(summary_path)
        summaries.append(summary)

        for i, row in summary.iterrows():
            filename = row["filename"]
            shutil.copy(Path(tile_dir) / filename, output_tiles_folder / filename)

    valid_tiles_all = pd.concat(summaries, ignore_index=True)
    valid_tiles_all.to_csv(valid_tiles_csv_path, index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Copy valid tiles from respective folders to unique folder"
    )
    parser.add_argument(
        "--tiles_dirs", nargs="+", help="Directories where original tiles are"
    )
    parser.add_argument(
        "--valid_tiles_summaries_path",
        nargs="+",
        help="Paths of the valid tiles CSV summaries (one for each WSI)",
    )
    parser.add_argument(
        "--output_tiles_folder", type=str, help="Where to copy the tiles"
    )
    parser.add_argument(
        "--valid_tiles_csv_path",
        type=str,
        help="Path of the resulting CVS, "
        "as the concatenation of the tiles summaries provided",
    )

    args = parser.parse_args()

    tiles_dirs = args.tiles_dirs
    valid_tiles_summaries_path = args.valid_tiles_summaries_path
    output_tiles_folder = Path(args.output_tiles_folder)
    valid_tiles_csv_path = args.valid_tiles_csv_path

    assert len(tiles_dirs) == len(
        valid_tiles_summaries_path
    ), f"The number of tiles directories ({len(tiles_dirs)}) is different than "
    "the number of summaries ({valid_tiles_summaries_path})"

    main(
        tiles_dirs,
        valid_tiles_summaries_path,
        output_tiles_folder,
        valid_tiles_csv_path,
    )
