"""
Duplex Cloud Scan

Leverage your cloud enabled scanner to create a duplex scanning functionality
through the Google Gmail API and Google Pub/Sub API
"""

from services.gmail import get_gmail_service, start_watch
from subscriber import get_subscriber, setup_subscription, start_pulling

service = get_gmail_service()

if __name__ == '__main__':
    # example_labels()
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
    print('starting')
    start_pulling(gmail, subscriber, start_history_id=res['historyId'])
