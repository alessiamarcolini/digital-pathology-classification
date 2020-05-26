#!/bin/bash
DATASET=TCGA-BRCA
SVS_DIR=data/$DATASET/svs

# download data
python preprocessing_download_wsi.py data/$DATASET/slides_filename_uuid_red.csv $SVS_DIR TCGA

