from apiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from httplib2 import Http
from oauth2client import client, file, tools

from duplex_cloud_scan.logger import get_logger
from ..threadsafe import build_request

logger = get_logger(__name__)

GDRIVE_DEFAULT_SCOPES = ['https://www.googleapis.com/auth/drive.file']
gdrive_service = None


def get_gdrive_service(scopes=None):
    global gdrive_service
    if gdrive_service:
        logger.info('return gdrive service from inmemory cache')
        return gdrive_service

    # Setup the Gmail API
    if not scopes:
        scopes = GDRIVE_DEFAULT_SCOPES
    store = file.Storage('gdrive_credentials.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('client_secret.json', scopes)
        # dont runt this one when we are not interactive
        creds = tools.run_flow(flow, store)
    gdrive_service = build('drive', 'v3', requestBuilder=build_request(creds))
    return gdrive_service


def gdrive_find_files(drive_service, query):
    page_token = None
    files = []
    while True:
        response = drive_service.files().list(
            q=query,
            spaces='drive',
            fields='nextPageToken, files(id, name)',
            pageToken=page_token).execute()
        files += response.get('files', [])
        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break
    return files


def gdrive_find_folder(drive_service, foldername):
    files = gdrive_find_files(
        drive_service,
        "mimeType='application/vnd.google-apps.folder' and name='{}'".format(
            foldername))
    if len(files) > 1:
        logger.info('found more than one folder named {}: {}'.format(
            foldername, files))
        raise RuntimeError(
            'Found more than one folder named {}, I can not handle this situation'
        )
    elif len(files) == 1:
        return files[0]
    else:
        return None


def gdrive_create_folder(drive_service, foldername, parents=None):
    file_metadata = {
        'name': foldername,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': parents,
    }
    file = drive_service.files().create(
        body=file_metadata, fields='id').execute()
    logger.info('folder {name} id: {file_id}'.format(
        name=foldername, file_id=file.get('id')))
    return file


def gdrive_find_or_create_folder(drive_service, foldername):
    folder = gdrive_find_folder(drive_service, foldername)
    if folder:
        return folder
    else:
        return gdrive_create_folder(drive_service, foldername)


def gdrive_create_file(drive_service, local_filepath, filename, parent):
    # simple uploads are supported up to 5MB
    media = MediaFileUpload(local_filepath, chunksize=-1, resumable=True)
    file_metadata = {
        'name': filename,
        'parents': [parent.get('id')],
    }
    file = drive_service.files().create(
        body=file_metadata, media_body=media, fields='id').execute()
    logger.info('file uploaded: {}'.format(file))
    return


if __name__ == '__main__':
    drive_service = get_gdrive_service()
    scans_folder = gdrive_find_or_create_folder(drive_service, 'Scans')
    gdrive_create_file(drive_service, 'combined_pdfs/22-07-2018_23.11.50.pdf',
                       '22-07-2018_23.11.50.pdf', scans_folder)
