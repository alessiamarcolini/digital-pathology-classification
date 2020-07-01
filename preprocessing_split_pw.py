import argparse
from pathlib import Path

import pandas as pd

from preprocessing.split import train_test_df_patient_wise


def main(labels_file, splitted_labels_file, label_cols, stratify):
    labels = pd.read_csv(labels_file)

    train_df, test_df = train_test_df_patient_wise(
        labels, "patient", label_cols, stratify=stratify
    )

    labels["split"] = labels["filename"].apply(
        lambda x: "train" if x in train_df["filename"].values else "test"
    )

    labels.to_csv(splitted_labels_file, index=None)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Dataset Train/test split")
    parser.add_argument("labels_file", type=str, help="Path of the labels file")
    parser.add_argument(
        "splitted_labels_file", type=str, help="Path of the splitted labels file",
    )
    parser.add_argument(
        "--label_cols",
        type=str,
        nargs="+",
        help="Column(s) to be used as labels. Must be present in the labels file",
    )
    parser.add_argument("--stratify", action="store_true")

    args = parser.parse_args()
    labels_file = args.labels_file
    splitted_labels_file = args.splitted_labels_file
    label_cols = args.label_cols
    stratify = args.stratify

    main(labels_file, splitted_labels_file, label_cols, stratify)
