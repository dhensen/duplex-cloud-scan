import base64
import os

from apiclient import errors
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import client, file, tools

from logger import get_logger
from settings import TOPIC_NAME, WATCH_LABELS

logger = get_logger(__name__)

DEFAULT_SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.compose'
]
gmail_service = None


def get_gmail_service(scopes=None):
    global gmail_service
    if gmail_service:
        logger.info('return gmail service from inmemory cache')
        return gmail_service

    # Setup the Gmail API
    if not scopes:
        scopes = DEFAULT_SCOPES
    store = file.Storage('credentials.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('client_secret.json', scopes)
        # dont runt this one when we are not interactive
        creds = tools.run_flow(flow, store)
    gmail_service = build(
        'gmail', 'v1', http=creds.authorize(Http()), cache_discovery=False)
    return gmail_service


def gmail_history_list(service, user_id, start_history_id):
    history = (service.users().history().list(
        userId=user_id, startHistoryId=start_history_id).execute())
    changes = history['history'] if 'history' in history else []
    while 'nextPageToken' in history:
        page_token = history['nextPageToken']
        history = (service.users().history().list(
            userId=user_id,
            startHistoryId=start_history_id,
            pageToken=page_token).execute())
        changes.extend(history['history'])

    return int(history['historyId']), changes


def start_watch(service):
    request = {'labelIds': [WATCH_LABELS], 'topicName': TOPIC_NAME}
    return service.users().watch(userId='me', body=request).execute()


# Call the Gmail API
def example_labels():
    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])
    if not labels:
        logger.info('No labels found.')
    else:
        logger.info('Labels:')
        for label in labels:
            if 'scan' in label['name']:
                logger.info(label)


def example_mails():
    results = service.users().messages().list(
        userId='me', labelIds=['Label_4339693487728562381']).execute()
    logger.info(results)


def get_email(id):
    results = service.users().messages().get(userId='me', id=id).execute()
    logger.info(results)


def get_attachments(service, user_id, msg_id, store_dir):
    """Get and store attachment from Message with given id.

    Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. The special value "me"
        can be used to indicate the authenticated user.
        msg_id: ID of Message containing attachment.
        store_dir: The directory used to store attachments.
    """
    attachments = []
    try:
        message = service.users().messages().get(
            userId=user_id, id=msg_id).execute()

        for part in message['payload']['parts']:
            if part['filename']:
                logger.debug('part.filename: {}'.format(part['filename']))
                base64_data = None
                if 'data' in part['body']:
                    base64_data = part['body']['data']
                elif 'attachmentId' in part['body']:
                    base64_data = get_attachment(
                        service=service,
                        user_id=user_id,
                        message_id=msg_id,
                        id=part['body']['attachmentId'])
                file_data = base64.urlsafe_b64decode(
                    base64_data.encode('UTF-8'))
                path = os.path.join(store_dir, part['filename'])
                f = open(path, 'wb')
                f.write(file_data)
                f.close()
                attachments.append(path)
    except errors.HttpError as error:
        logger.error('An error occurred: {}'.format(error))
    return attachments


def get_attachment(service, user_id, message_id, id):
    result = service.users().messages().attachments().get(
        userId=user_id, messageId=message_id, id=id).execute()
    return result['data']
