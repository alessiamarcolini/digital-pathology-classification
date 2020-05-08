import os
from pathlib import Path

DATASET = 'TCGA-BRCA'
DATA_DIR = Path('data')/ DATASET
SVS_DIR = DATA_DIR / 'svs'
TILES_PER_SVS_DIR = DATA_DIR / 'tiles_per_svs'

SVS_filenames = [f for f in os.listdir(SVS_DIR) if f.endswith('.svs')]
SVS_filenames_no_ext = [os.path.splitext(f)[0] for f in SVS_filenames]


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

rule svs_to_random_tiles:
    input:
        'preprocessing/svs_to_tiles.py',
        expand('{svs_dir}/{{svs_filename_no_ext}}.svs', svs_dir=SVS_DIR)
    output:
        directory(expand('{tiles_per_svs_dir}/{{svs_filename_no_ext}}/tiles', tiles_per_svs_dir=TILES_PER_SVS_DIR))
    shell:
        'python preprocessing/svs_to_tiles.py {input[1]} {output[0]} random'

rule svs_to_random_tiles_all:
    input:
        'preprocessing/svs_to_tiles.py',
        directory(expand('{tiles_per_svs_dir}/{svs_filename_no_ext}/tiles', tiles_per_svs_dir=TILES_PER_SVS_DIR, svs_filename_no_ext=SVS_filenames_no_ext))
       

def tiles_filename(wildcards):
    filenames = sorted([f for f in os.listdir(f'{TILES_PER_SVS_DIR}/{wildcards.svs_filename_no_ext}/tiles') if f.endswith('.png')])
    return directory(expand('{tiles_per_svs_dir}/{{svs_filename_no_ext}}/tiles/{tile_filename}', tiles_per_svs_dir=TILES_PER_SVS_DIR, tile_filename=filenames))


rule check_tiles_per_svs:
    input:
        'preprocessing_check_tiles_tcga.py',
        filenames = tiles_filename
    output:
        expand('{tiles_per_svs_dir}/{{svs_filename_no_ext}}/correct_tiles_per_svs_filenames.csv', tiles_per_svs_dir=TILES_PER_SVS_DIR)
    shell:
        'python preprocessing_check_tiles.py {input.filenames} {output[0]}'

rule check_tiles_all:
    input:
        'preprocessing_check_tiles_tcga.py',
        expand('{tiles_per_svs_dir}/{svs_filename_no_ext}/correct_tiles_per_svs_filenames.csv', tiles_per_svs_dir=TILES_PER_SVS_DIR, svs_filename_no_ext=SVS_filenames_no_ext)

