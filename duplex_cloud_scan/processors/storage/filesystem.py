from os import makedirs
from os.path import join
from shutil import copyfile

from ..abc import Processor
from datetime import datetime


class FilesystemProcessor(Processor):
    def __init__(self, target_dir, filename_format):
        self.target_dir = target_dir
        self.filename_format = filename_format

    def process(self, abs_filepath: str, file, dt: datetime):
        """Save the given file somewhere on the filesystem"""
        new_filename = '{}.pdf'.format(dt.strftime(self.filename_format))
        new_filepath = join(self.target_dir, new_filename)
        makedirs(self.target_dir, exist_ok=True)
        copyfile(abs_filepath, new_filepath)
