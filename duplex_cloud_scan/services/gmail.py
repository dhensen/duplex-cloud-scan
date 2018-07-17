from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import logging
from settings import WATCH_LABELS, TOPIC_NAME

# logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
logger = logging.getLogger(__name__)

gmail_service = None


def get_gmail_service():
    global gmail_service
    if gmail_service:
        logger.info('return gmail service from inmemory cache')
        return gmail_service

    # Setup the Gmail API
    SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
    store = file.Storage('credentials.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
        # dont runt this one when we are not interactive
        creds = tools.run_flow(flow, store)
    gmail_service = build('gmail', 'v1', http=creds.authorize(Http()))
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

    return history['historyId'], changes


def start_watch(service):
    request = {'labelIds': [WATCH_LABELS], 'topicName': TOPIC_NAME}
    return service.users().watch(userId='me', body=request).execute()
