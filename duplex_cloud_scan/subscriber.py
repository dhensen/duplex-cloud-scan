from google.cloud import pubsub
from settings import TOPIC_NAME, PROJECT_ID
from google.api_core.exceptions import AlreadyExists
from pprint import pprint
from services.gmail import gmail_history_list, get_attachments
import json
from settings import SCAN_FRONT_LABEL, SCAN_BACK_LABEL
from logger import get_logger
from os import makedirs
from combine_pdf import combine_two_pdfs

logger = get_logger(__name__)

subscription_name = 'projects/{project}/subscriptions/{subscription}'.format(
    project=PROJECT_ID, subscription='gmail')

last_known_history_id = 1
front_pdf_message_ids = []
back_pdf_message_ids = []


def get_subscriber():
    return pubsub.SubscriberClient()


def setup_subscription(subscriber):
    try:
        res = subscriber.create_subscription(subscription_name, TOPIC_NAME)
        pprint(res)
    except AlreadyExists:
        pass


def _mark_front(message_id):
    front_pdf_message_ids.append(message_id)


def _mark_back(message_id):
    back_pdf_message_ids.append(message_id)


def process_pair(service):
    front_msg_id = front_pdf_message_ids.pop()
    back_msg_id = back_pdf_message_ids.pop()
    logger.info('{} and {} belong together'.format(front_msg_id, back_msg_id))
    target_dir = 'attachments/{}-{}'.format(front_msg_id, back_msg_id)
    makedirs(target_dir, exist_ok=True)
    front_attachments = get_attachments(service, 'me', front_msg_id,
                                        target_dir)
    back_attachments = get_attachments(service, 'me', back_msg_id, target_dir)

    if len(front_attachments) == 1 and len(back_attachments) == 1:
        combine_two_pdfs(
            front_attachments[0],
            back_attachments[0], 'example_pdfs/combined-{}-{}.pdf'.format(
                front_msg_id, back_msg_id))
    # download front and back attachment


def process_message(gmail_service, message):
    """
    This calls history.list for an incoming message.data.historyId
    Look if there is a messagesAdded key inside each history change
    If there is look for the labelIds key and mark e-mails front or back
    depending on the label attached to it.
    Then if there is a front and a back message marked, process them.
    """
    global last_known_history_id
    data = json.loads(message.data.decode('utf-8'))
    logger.info('nieuw bericht, historyId: {}'.format(data['historyId']))

    historyId = int(data['historyId'])
    if historyId <= last_known_history_id:
        logger.info('given historyId={} is smaller or equal to last known'
                    'historyId={}, already up to date'.format(
                        historyId, last_known_history_id))
        return
    nextHistoryId, changes = gmail_history_list(
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
                    print('FOUND FRONT SIDE PDF MESSAGE: {}'.format(
                        message['id']))
                    _mark_front(message['id'])
                if SCAN_BACK_LABEL in message.get('labelIds', []):
                    print('FOUND BACK SIDE SIDE PDF MESSAGE: {}'.format(
                        message['id']))
                    _mark_back(message['id'])
        if back_pdf_message_ids and front_pdf_message_ids:
            process_pair(gmail_service)
    last_known_history_id = nextHistoryId
    # [ ] lokaal opslaan in een map (dropbox bijv.)
    # [ ] mail die naar jezelf via dino.hensen+scan_duplex@gmail.com of geef de mail een label DUPLEX_TARGET_LABEL
    # [ ] upload scan naar dropbox via api
    # [ ] upload scan naar gdrive via api


def callback(gmail_service):
    def inner(message):
        logger.info('START CALLBACK')
        try:
            process_message(gmail_service, message)
            message.ack()
        except Exception as e:
            message.nack()
            logger.error('error while processing message {}'.format(message))
            raise e
        logger.info('END CALLBACK')

    return inner


def start_pulling(gmail_service, subscriber, start_history_id=1):
    global last_known_history_id
    last_known_history_id = int(start_history_id)
    logger.info('before subscriber.subscribe()')
    future = subscriber.subscribe(subscription_name, callback(gmail_service))
    logger.info('before future.result()')
    try:
        future.result()
    except KeyboardInterrupt:
        future.cancel()
    except Exception as ex:
        raise
