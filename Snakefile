import os
from pathlib import Path
import subprocess

DATASET = 'TCGA-BRCA'
DATA_DIR = Path('data')/ DATASET
SVS_DIR = DATA_DIR / 'svs'
TILES_DIR = DATA_DIR / 'tiles'
TILES_PER_SVS_DIR = DATA_DIR / 'tiles_per_svs'
VALID_TILES_CSV_FILENAME = DATA_DIR / 'valid_tiles.csv'

SVS_filenames = [f for f in os.listdir(SVS_DIR) if f.endswith('.svs')]
SVS_filenames_no_ext = [os.path.splitext(f)[0] for f in SVS_filenames]


# -------------
# PREPROCESSING
# -------------

rule svs_to_random_tiles:
    input:
        'preprocessing_svs_to_tiles.py',
        ancient(SVS_DIR / '{svs_filename_no_ext}.svs')
    output:
        dynamic('{tiles_per_svs_dir}/{svs_filename_no_ext}/tiles/{tile_filename}')
    run:
        output_folder = Path(output[0]).parent
        subprocess.call(f'python preprocessing_svs_to_tiles.py {input[1]} {output_folder} random', shell=True)

rule check_tiles_per_svs:
    input:
        'preprocessing_check_tiles_tcga.py',
        filenames = dynamic(expand('{tiles_per_svs_dir}/{{svs_filename_no_ext}}/tiles/{{tile_filename}}', tiles_per_svs_dir=TILES_PER_SVS_DIR))
    output:
        expand('{tiles_per_svs_dir}/{{svs_filename_no_ext}}/valid_tiles_per_svs_filenames.csv', tiles_per_svs_dir=TILES_PER_SVS_DIR)
    shell:
        'python preprocessing_check_tiles_tcga.py {input.filenames} {output[0]}'

rule check_tiles_all:
    input:
        'preprocessing_check_tiles_tcga.py',
        expand('{tiles_per_svs_dir}/{svs_filename_no_ext}/valid_tiles_per_svs_filenames.csv', tiles_per_svs_dir=TILES_PER_SVS_DIR, svs_filename_no_ext=SVS_filenames_no_ext)

rule recompact_valid_tiles:
    input:
        tiles_dirs = expand('{tiles_per_svs_dir}/{svs_filename_no_ext}/tiles', tiles_per_svs_dir=TILES_PER_SVS_DIR,  svs_filename_no_ext=SVS_filenames_no_ext),
        valid_tiles_summaries = expand('{tiles_per_svs_dir}/{svs_filename_no_ext}/valid_tiles_per_svs_filenames.csv', tiles_per_svs_dir=TILES_PER_SVS_DIR,  svs_filename_no_ext=SVS_filenames_no_ext)
    output:
        directory(TILES_DIR),
        VALID_TILES_CSV_FILENAME
    shell:
        'python recompact_valid_tiles.py --tiles_dirs {input.tiles_dirs} --valid_tiles_summaries_path {input.valid_tiles_summaries} --output_tiles_folder {output[0]} --valid_tiles_csv_path {output[1]}'
