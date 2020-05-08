import gin

from .check_tiles import *
from .svs_to_tiles import *

current_directory = Path(os.path.abspath(os.path.dirname(__file__)))
gin.parse_config_file(current_directory / "preprocessing_config.gin")
