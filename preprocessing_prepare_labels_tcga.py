import argparse

import pandas as pd

from preprocessing.labels import encode_label
from preprocessing.tcga.utils import read_clinical_file


def main(
    valid_tiles_file,
    clinical_file,
    output_tiles_labels_file,
    patient_col_tiles_file,
    patient_col_clinical_file,
    label_cols,
):

    tiles = pd.read_csv(valid_tiles_file)
    clinical = read_clinical_file(clinical_file)

    if not set(label_cols + [patient_col_clinical_file]) <= set(clinical.columns):
        missing_cols = set(label_cols + [patient_col_clinical_file]) - set(
            clinical.columns
        )
        raise ValueError(
            f"Columns {' ,'.join(missing_cols)} are missing from the clinical file"
        )
    if not patient_col_tiles_file in tiles.columns:
        raise ValueError(
            f"Patient column {patient_col_tiles_file} not present in tiles file"
        )

    labels_w_patient = clinical[[*label_cols, patient_col_clinical_file]]

    labels_w_patient.dropna(subset=label_cols, inplace=True)
    labels_w_patient.drop_duplicates(inplace=True)

    tiles_w_labels = pd.merge(
        tiles,
        labels_w_patient,
        left_on=patient_col_tiles_file,
        right_on=patient_col_clinical_file,
        how="left",
    ).drop(patient_col_clinical_file, axis=1)

    assert len(tiles_w_labels) == len(tiles)

    for label in label_cols:
        tiles_w_labels, _ = encode_label(tiles_w_labels, label, f"{label}_encoded")

    tiles_w_labels.to_csv(output_tiles_labels_file, index=None)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "valid_tiles_file", type=str, help="Path to the valid tiles summary file"
    )
    parser.add_argument(
        "clinical_file",
        type=str,
        help="Path to the clinical file (TSV), downloaded from TCGA portal",
    )
    parser.add_argument(
        "output_tiles_labels_file",
        type=str,
        help="Path to the output file with tiles summary and labels",
    )
    parser.add_argument(
        "--patient_col_tiles_file",
        type=str,
        default="patient",
        help="Column name representing the patient "
        "- code, name, id, etc - in the tiles summary file",
    )
    parser.add_argument(
        "--patient_col_clinical_file",
        type=str,
        default="case_submitter_id",
        help="Column name representing the patient "
        "- code, name, id, etc - in the clinical file",
    )
    parser.add_argument(
        "--label_cols",
        type=str,
        nargs="+",
        help="Column(s) to be used as labels. Must be present in the clinical file",
    )

    args = parser.parse_args()
    valid_tiles_file = args.valid_tiles_file
    clinical_file = args.clinical_file
    output_tiles_labels_file = args.output_tiles_labels_file
    patient_col_tiles_file = args.patient_col_tiles_file
    patient_col_clinical_file = args.patient_col_clinical_file
    label_cols = args.label_cols

    main(
        valid_tiles_file,
        clinical_file,
        output_tiles_labels_file,
        patient_col_tiles_file,
        patient_col_clinical_file,
        label_cols,
    )
