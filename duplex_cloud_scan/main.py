"""
Shows basic usage of the Gmail API.

Lists the user's Gmail labels.
"""

from pprint import pprint
import base64
from apiclient import errors
import os
from settings import WATCH_LABELS, TOPIC_NAME
from services.gmail import get_gmail_service, start_watch
from subscriber import get_subscriber, setup_subscription, start_pulling

service = get_gmail_service()


# Call the Gmail API
def example_labels():
    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])
    if not labels:
        print('No labels found.')
    else:
        print('Labels:')
        for label in labels:
            # print(label['name'])
            if 'scan' in label['name']:
                print(label)


def example_mails():
    results = service.users().messages().list(
        userId='me', labelIds=['Label_4339693487728562381']).execute()

    pprint(results)


def get_email(id):
    results = service.users().messages().get(userId='me', id=id).execute()
    pprint(results)


def get_attachments(service, user_id, msg_id, store_dir):
    """Get and store attachment from Message with given id.

    Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. The special value "me"
        can be used to indicate the authenticated user.
        msg_id: ID of Message containing attachment.
        store_dir: The directory used to store attachments.
    """
    try:
        message = service.users().messages().get(
            userId=user_id, id=msg_id).execute()

        for part in message['payload']['parts']:
            if part['filename']:
                pprint(part)
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
    except errors.HttpError as error:
        print('An error occurred: {}'.format(error))


def get_attachment(service, user_id, message_id, id):
    result = service.users().messages().attachments().get(
        userId=user_id, messageId=message_id, id=id).execute()
    return result['data']


if __name__ == '__main__':
    example_labels()
    # example_mails()
    # get_email('1647dbf1a7d7b986')
    # get_attachments(
    #     service=service,
    #     user_id='me',
    #     msg_id='1647dbf1a7d7b986',
    #     store_dir='attachments/')
    res = start_watch(service)
    gmail = get_gmail_service()
    subscriber = get_subscriber()
    setup_subscription(subscriber)
    start_pulling(gmail, subscriber, start_history_id=res['historyId'])
