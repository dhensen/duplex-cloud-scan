from ..abc import Processor
from datetime import datetime
from ...settings import GDRIVE_SCANS_FOLDER
from os.path import basename
from ...services.gdrive import get_gdrive_service, gdrive_find_or_create_folder, gdrive_create_file


class GdriveProcessor(Processor):
    def __init__(self, filename_format):
        self.filename_format = filename_format

    def process(self, abs_filepath: str, file, dt: datetime):
        """Save the given file to Google Drive"""
        new_filename = '{}.pdf'.format(dt.strftime(self.filename_format))
        drive_service = get_gdrive_service()
        scans_folder = gdrive_find_or_create_folder(drive_service,
                                                    GDRIVE_SCANS_FOLDER)
        gdrive_create_file(drive_service, abs_filepath, new_filename,
                           scans_folder)
