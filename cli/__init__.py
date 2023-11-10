import os
import platform
import json
from .utils.files import exists_file, read_file
from pathlib import Path

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
CWD_PATH = os.getcwd()
OS_TYPE = platform.system().lower()
USER_HOME = str(Path.home())
USER_FILE_SETTINGS_PATH = os.path.join(USER_HOME, '.eash-cli')
SETTINGS = json.loads(read_file(USER_FILE_SETTINGS_PATH)
                      ) if exists_file(USER_FILE_SETTINGS_PATH) else {'commands': None, 'bundlers': None}

def root_file(rel_path):
    return os.path.join(ROOT_DIR, rel_path)
