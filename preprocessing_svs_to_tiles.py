import argparse
import os
from pathlib import Path

from preprocessing.svs_to_tiles import extract_random_tiles

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

    wsi_filename_no_ext = os.path.splitext(os.path.basename(wsi_filename))[0]

    extract_random_tiles(wsi_filename, prefix=f"{output_folder}/{wsi_filename_no_ext}_")
