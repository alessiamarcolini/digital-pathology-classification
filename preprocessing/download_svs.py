import argparse
import os
from pathlib import Path

import pandas as pd
import requests
from tqdm import tqdm


def download_svs_tcga(file_uuid, output_filename, overwrite=False):
    """Download svs from TCGA data portal.

    Parameters
    ----------
    file_uuid : str
        TCGA UUID file reference.
    output_filename : str or pathlib.Path
        Filename to which the svs is saved.
    overwrite : bool, optional
        Whether to overwite existing file. Default is False.

    Raises
    ------
    FileExistsError
        If output_filename already exists.

    """
    if not overwrite and os.path.exists(output_filename):
        raise FileExistsError(
            f'File {output_filename} exists. Please set overwrite=True to overwrite already existing file.'
        )

    os.makedirs(Path(output_filename).parent, exist_ok=True)

    data_endpt = "https://api.gdc.cancer.gov/data/{}".format(file_uuid)

    # TODO: this can definitely break
    response = requests.get(data_endpt, headers={"Content-Type": "application/json"})

    # The file name can be found in the header within the Content-Disposition key.
    response_head_cd = response.headers["Content-Disposition"]

    with open(output_filename, "wb") as output_file:
        output_file.write(response.content)


def main(metadata_file, output_folder, data_source):

    if data_source == 'TCGA':

        csv = pd.read_csv(metadata_file)

        for i, row in tqdm(csv.iterrows()):
            uuid = row['uuid']
            filename = row['filename']

            output_path = output_folder / filename

            try:
                download_svs_tcga(uuid, output_path)
            except FileExistsError as e:
                # Add an underscore at the end to download the file anyway
                file_no_ext = os.path.splitext(output_path)[0]
                ext = os.path.splitext(output_path)[1]
                new_path = f'{file_no_ext}_{ext}'

                download_svs_tcga(uuid, new_path)


if __name__ == '__main__':
    accepted_data_sources = ['TCGA']

    parser = argparse.ArgumentParser(description='Download SVS files.')
    parser.add_argument('metadata_file', type=str, help='Metadata file')
    parser.add_argument(
        'output_folder', type=str, help='Folder to which the SVSs are saved'
    )
    parser.add_argument(
        'data_source',
        type=str,
        help=f'Repository from which retrieve the data. Accepted values: {", ".join(accepted_data_sources)}',
    )

    args = parser.parse_args()

    metadata_file = args.metadata_file
    output_folder = Path(args.output_folder)
    data_source = args.data_source

    assert (
        data_source in accepted_data_sources
    ), f'Data source {data_source} not available. Accepted values: {", ".join(accepted_data_sources)}'

    main(metadata_file, output_folder, data_source)
