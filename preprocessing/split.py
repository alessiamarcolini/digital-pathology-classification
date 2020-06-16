
import numpy as np
from sklearn.model_selection import train_test_split


def train_test_df_patient_wise(
    dataset_df, patient_col, label_col, test_size=0.2, stratify=True, seed=1234
):
    patient_with_labels = (
        dataset_df.groupby(patient_col)[label_col].apply(list)
    )
    unique_patients = patient_with_labels.index.values
    patients_labels = np.array(list(patient_with_labels.values))

    if stratify:
        train_patients, test_patients = train_test_split(
            unique_patients,
            test_size=test_size,
            random_state=seed,
            stratify=patients_labels,
        )
    else:
        train_patients, test_patients = train_test_split(
            unique_patients, test_size=test_size, random_state=seed
        )

    dataset_train_df = dataset_df.loc[dataset_df[patient_col].isin(train_patients)]
    dataset_test_df = dataset_df.loc[dataset_df[patient_col].isin(test_patients)]

    return dataset_train_df, dataset_test_df
