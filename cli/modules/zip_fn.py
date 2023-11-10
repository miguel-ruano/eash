from zipfile import ZipFile
from os.path import basename
from cli.utils import files
import os

ZIP_DEFAULT_FILTER = "**"

# Zip the files from given directory that matches the filter
def zip(dir_name:str, file_name:str, filter:str = ZIP_DEFAULT_FILTER):
    dir_name = dir_name.replace("\\","/")
    with ZipFile(file_name, 'w') as zip_obj:
       # Iterate over all the files in directory
        for file_path in files.list_all_files(dir_name, filter):
            zip_path = file_path.replace("\\","/").replace(dir_name, "")
            zip_obj.write(file_path, zip_path)
        return zip_obj
