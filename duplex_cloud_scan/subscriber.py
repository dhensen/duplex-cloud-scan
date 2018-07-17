from google.cloud import pubsub
from settings import TOPIC_NAME, PROJECT_ID
from google.api_core.exceptions import AlreadyExists
from pprint import pprint
from services.gmail import gmail_history_list
import json
from settings import SCAN_FRONT_LABEL

sub_name = 'projects/{project}/subscriptions/{subscription}'.format(
    project=PROJECT_ID, subscription='gmail')

last_known_history_id = 1


def get_subscriber():
    return pubsub.SubscriberClient()


def setup_subscription(subscriber):
    try:
        res = subscriber.create_subscription(sub_name, TOPIC_NAME)
        pprint(res)
    except AlreadyExists:
        pass


def process_message(gmail_service, message):
    global last_known_history_id
    pprint(message)
    data = json.loads(message.data)
    print('nieuw bericht, historyId: {}'.format(data['historyId']))
    # pprint(data)
    historyId, changes = gmail_history_list(
        service=gmail_service,
        user_id='me',
        start_history_id=last_known_history_id)
    pprint(changes)
    for change in changes:
        if 'messagesAdded' in change:
            messagesAdded = change['messagesAdded']
            for item in messagesAdded:
                message = item.get('message', {})
                if SCAN_FRONT_LABEL in message.get('labelIds', []):
                    print('FOUND MESSAGE: {}'.format(message['id']))
    last_known_history_id = historyId
    # history.list callen voor elke message.data.historyId
    # die json processen:
    # pak data op key messagesAdded
    # kijk of labelIds je gewenste labels bevat
    # zo ja: markeer message als front of  back
    # als een back een front markering opvolt: merge pdfs
    # daarna:
    # OF lokaal opslaan in een map (dropbox bijv.)
    # OF mail die naar jezelf via dino.hensen+scan_duplex@gmail.com of geef de mail een label DUPLEX_TARGET_LABEL
    # OF upload scan naar dropbox via api
    # OF upload scan naar gdrive via api


def callback(gmail_service):
    def inner(message):
        process_message(gmail_service, message)
        message.ack()

    return inner


def start_pulling(gmail_service, subscriber, start_history_id=1):
    global last_known_history_id
    last_known_history_id = start_history_id
    future = subscriber.subscribe(sub_name, callback(gmail_service))

    try:
        future.result()
    except Exception as ex:
        raise
