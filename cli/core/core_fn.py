import json
import cli as cli_module
from cli.utils.files import create_file
from cli.modules.zip_fn import zip, ZIP_DEFAULT_FILTER

def update_settings_prop(key:str, value):
    if key:
        SETTINGS = cli_module.SETTINGS
        SETTINGS[key] = value
        create_file(cli_module.USER_FILE_SETTINGS_PATH, json.dumps(SETTINGS))

def set_settings_bundler(value):
    if value:
        update_settings_prop('bundlers', value)

def set_settings_commands(value):
    if value:
        update_settings_prop('commands', value)

def eval_context(context: dict):
    return {
        **context,
        'set_settings_bundler': lambda v: set_settings_bundler(v),
        'set_settings_commands': lambda v: set_settings_commands(v),
        'zipdir': lambda dir, name : zip(dir, name, ZIP_DEFAULT_FILTER),
        'zip_w_filter': lambda dir, name, filter : zip(dir, name, filter),
        'SETTINGS': cli_module.SETTINGS.copy()
    }