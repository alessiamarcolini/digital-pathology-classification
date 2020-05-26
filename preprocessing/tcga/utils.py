import os

import pandas as pd


def wsi_filename_to_patient(wsi_filename):
    """
    Compute the patient name from a TCGA WSI filename.

    Notes
    -----
    TCGA filenames reference: https://docs.gdc.cancer.gov/Encyclopedia/pages/TCGA_Barcode/

    Parameters
    ----------
    wsi_filename : str
        The filename of the WSI

    Returns
    -------
    str
        The patient name correspondent to the WSI

    """

    wsi_filename = os.path.basename(wsi_filename)
    return "-".join(wsi_filename.split("-")[:3])


def wsi_filename_to_wsi_id(wsi_filename):
    """
    Compute the WSI unique id from a TCGA WSI filename

    Parameters
    ----------
    wsi_filename : str
        The filename of the WSI

    Notes
    -----
    TCGA filenames reference: https://docs.gdc.cancer.gov/Encyclopedia/pages/TCGA_Barcode/

    Returns
    -------
    str
        The WSI unique id correspondent to the WSI

    """

    wsi_filename = os.path.basename(wsi_filename)
    return "-".join(wsi_filename.split("-")[:4])


def tile_filename_to_wsi_filename(tile_filename):
    """Compute WSI filename from a tile filename (which is extracted from that WSI)

    Parameters
    ----------
    tile_filename : str
        Tile filename

    Returns
    -------
    str
        WSI filename
        
    """
    return tile_filename.split("_")[0]


def read_clinical_file(filename):
    """Read TCGA clinical file

    Parameters
    ----------
    filename : str or pathlib.Path
        Path to the clinical file

    Returns
    -------
    pandas.DataFrame
        DataFrame representing the clinical file
    """
    clinical = pd.read_csv(filename, sep="\t")
    return clinical
