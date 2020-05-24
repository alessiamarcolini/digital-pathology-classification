import os
from pathlib import Path

import pandas as pd
import requests
from requests import RequestException
from tqdm import tqdm


class TCGAWSIDownloader:
    """TCGA WSI Downloader. 

    Attributes
    ----------
    metadata_path : str or pathlib.Path
        Path to the CSV file containing `uuid` and `filename` columns.
        The UUID is the TCGA file unique identifier.
    metadata : pandas.DataFrame
        The metadata DataFrame
    output_folder : str or pathlib.Path
        Folder where to save the downloaded WSI
    not_downloaded : list of str
        UUIDs of the WSI for which some error happened during download

    """

    def __init__(self, metadata_path, output_folder):
        self._metadata_path = Path(metadata_path)
        self._output_folder = Path(output_folder)
        self._not_downloaded = []

    @property
    def metadata(self):
        return pd.read_csv(self.metadata_path)

    @property
    def metadata_path(self):
        return self._metadata_path

    @property
    def output_folder(self):
        return self._output_folder

    @property
    def not_downloaded(self):
        return self._not_downloaded

    @staticmethod
    def _download_single_wsi(file_uuid, output_filename):
        """Download a single WSI from TCGA data portal.

        Parameters
        ----------
        file_uuid : str
            TCGA UUID file reference.
        output_filename : str or pathlib.Path
            Filename to which the WSI is saved.

        Raises
        ------
        FileExistsError
            If output_filename already exists.

        """
        os.makedirs(Path(output_filename).parent, exist_ok=True)

        data_endpt = "https://api.gdc.cancer.gov/data/{}".format(file_uuid)

        response = requests.get(
            data_endpt, headers={"Content-Type": "application/json"}
        )

        try:
            # "Content-Disposition" key is found only if the UUID corresponds to a valid file
            response_head_cd = response.headers["Content-Disposition"]
        except KeyError as e:
            # TODO: log the exception
            raise
        else:
            with open(output_filename, "wb") as output_file:
                output_file.write(response.content)

    def download(self, n=0, overwrite_mode="skip"):
        """Download WSI from TCGA data portal.

        Parameters
        ----------
        n : int, optional
            Number of WSI to download. By default is 0, which means unlimited.
        overwrite_mode : {strict, overwrite, skip}, optional
            How to handle existing file:
            * strict: raise FileExistsError if file exists
            * overwrite: overwrite existing file with the new one
            * skip: Skip download

            Default is skip.

        Raises
        ------
        ValueError
            If overwrite_mode is not 'strict', 'overwrite' or 'skip'
        FileExistsError
            If output_filename already exists.
            
        """
        if overwrite_mode not in ["strict", "overwrite", "skip"]:
            raise ValueError(
                f"overwrite_mode must be 'strict', 'overwrite' or 'skip'. Got {overwrite_mode}."
            )

        total_wsi_to_download = len(self.metadata) if n == 0 else n
        for i, row in tqdm(self.metadata.iterrows(), total=total_wsi_to_download):

            if n != 0 and i == n:
                break

            uuid = row["uuid"]
            filename = row["filename"]

            output_path = self.output_folder / filename
            if os.path.exists(output_path):
                if overwrite_mode == "strict":
                    raise FileExistsError(
                        f"File {output_path} exists. Please set overwrite_mode='overwrite'"
                        " to overwrite already existing file, or overwrite_mode='skip' to skip download."
                    )
                elif overwrite_mode == "overwrite":
                    os.remove(output_path)
                else:
                    continue
            try:
                self._download_single_wsi(uuid, output_path)
            except (RequestException, KeyError) as e:
                print(f"{type(e).__name__}: {e}")

                self._not_downloaded.append(uuid)

        if self._not_downloaded:
            print("Not downloaded: ", "\n".join(self._not_downloaded))
