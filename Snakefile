DATASET = 'TCGA-BRCA'
DATA_DIR = f'data/{DATASET}'
SVS_DIR = f'{DATA_DIR}/svs'


# -------------
# PREPROCESSING
# -------------

rule download_svs:
    input:
        'preprocessing/download_svs.py',
        f'data/{DATASET}/slides_filename_uuid.csv'
    output:
        directory(SVS_DIR)
    shell:
        'python preprocessing/download_svs.py {input[1]} {output[0]} TCGA'