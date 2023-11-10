import os
import shutil
import codecs
import re

def read_file(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()


def list_files(dir: str) -> list:
    return [os.path.join(dir, f) for f in os.listdir(dir) if os.path.isfile(os.path.join(dir, f))]

def create_dir(dir: str):
    os.makedirs(dir, exist_ok=True)

def copy_files(src: str, dst: str, filter:str = None, opts: str = None):
    src = src.replace("\\","/")
    keep_subfolder = opts and opts.find('-r') != -1
    for file in list_all_files(src, filter):
        file_dst = file.replace("\\","/").replace(src, dst + "/") if keep_subfolder else dst
        os.makedirs(os.path.dirname(file_dst), exist_ok=True)
        shutil.copy(file, file_dst)

def remove_dir(dir: str):
    shutil.rmtree(dir)

def create_file(dir: str, body):
    with open(dir, 'w') as file:
        file.write(body)

def exists_file(dir: str):
    return os.path.exists(dir)

def parse_file_filter(filter:str):
    filter = filter.replace("\\","\\\\")
    filter = filter.replace(".","\\.")
    filter = re.sub('\*\*',".*", filter)
    filter = re.sub('(?<!(\.))\*',"\\\w*", filter)
    return filter

def list_all_files(dir: str, filter: str = None) -> list:
    files = []
    filter = parse_file_filter(filter) if filter else None
    filter = re.compile(filter) if filter else re.compile(".*")
    for folder_name, subfolders, filenames in os.walk(dir):
        for filename in filenames:
            file_path = os.path.join(folder_name, filename)
            file_path = file_path.replace("\\","/")
            if filter.fullmatch(filename) or filter.fullmatch(file_path):
                files.append(file_path)
    return files
    