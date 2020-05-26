import argparse
from pathlib import Path

from preprocessing.tcga import TCGAWSIDownloader


def main(metadata_path, output_folder, data_source):

    if data_source == "TCGA":

        downloader = TCGAWSIDownloader(metadata_path, output_folder)
        downloader.download(overwrite_mode="overwrite")


if __name__ == "__main__":
    accepted_data_sources = ["TCGA"]

    parser = argparse.ArgumentParser(description="Download WSI files.")
    parser.add_argument("metadata_path", type=str, help="Metadata file")
    parser.add_argument(
        "output_folder", type=str, help="Folder to which the WSI are saved"
    )
    parser.add_argument(
        "data_source",
        type=str,
        help=f'Repository from which retrieve the data. Accepted values: {", ".join(accepted_data_sources)}',
    )

    args = parser.parse_args()

    metadata_path = args.metadata_path
    output_folder = Path(args.output_folder)
    data_source = args.data_source

    assert (
        data_source in accepted_data_sources
    ), f'Data source {data_source} not available. Accepted values: {", ".join(accepted_data_sources)}'

    main(metadata_path, output_folder, data_source)
