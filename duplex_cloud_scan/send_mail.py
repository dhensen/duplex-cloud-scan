import base64
import mimetypes
import os
from email.mime.application import MIMEApplication
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from apiclient import errors


def send_message(service, user_id, message):
    """Send an email message.

    Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. The special value "me"
        can be used to indicate the authenticated user.
        message: Message to be sent.

    Returns:
        Sent Message.
    """
    try:
        message = (service.users().messages().send(
            userId=user_id, body=message).execute())
        print('Message Id: %s' % message['id'])
        return message
    except errors.HttpError as error:
        print('An error occurred: %s' % error)


def create_message(sender, to, subject, message_text):
    """Create a message for an email.

    Args:
        sender: Email address of the sender.
        to: Email address of the receiver.
        subject: The subject of the email message.
        message_text: The text of the email message.

    Returns:
        An object containing a base64url encoded email object.
    """
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    return {
        'raw': base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    }


def create_message_with_attachment(sender, to, subject, message_text, file_dir,
                                   filename):
    """Create a message for an email.

    Args:
        sender: Email address of the sender.
        to: Email address of the receiver.
        subject: The subject of the email message.
        message_text: The text of the email message.
        file_dir: The directory containing the file to be attached.
        filename: The name of the file to be attached.

    Returns:
        An object containing a base64url encoded email object.
    """
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject

    msg = MIMEText(message_text)
    message.attach(msg)

    path = os.path.join(file_dir, filename)
    content_type, encoding = mimetypes.guess_type(path)
    if content_type is None or encoding is not None:
        content_type = 'application/octet-stream'
    main_type, sub_type = content_type.split('/', 1)
    mime_by_main_type = {
        'text': MIMEText,
        'image': MIMEImage,
        'audio': MIMEAudio,
        'application': MIMEApplication
    }
    cls = mime_by_main_type.get(main_type, None)
    fp = open(path, 'rb')
    if cls:
        msg = cls(fp.read(), _subtype=sub_type)
    else:
        msg = MIMEBase(main_type, sub_type)
        msg.set_payload(fp.read())
    fp.close()

    msg.add_header('Content-Disposition', 'attachment', filename=filename)
    message.attach(msg)

    return {
        'raw': base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    }


def main():
    from services.gmail import get_gmail_service
    # this script only needs compose scope, but then I have to manage two sets of credentials
    # in dev which I'm not going to do right now
    # scopes = ['https://www.googleapis.com/auth/gmail.compose']
    service = get_gmail_service()
    front_pdf_message = create_message_with_attachment(
        'dino.hensen@gmail.com', 'dino.hensen+scan_front@gmail.com',
        'test front', 'test front', 'example_pdfs', 'front.pdf')
    back_pdf_message = create_message_with_attachment(
        'dino.hensen@gmail.com', 'dino.hensen+scan_back@gmail.com',
        'test back', 'test back', 'example_pdfs', 'back.pdf')

    send_message(service, 'me', front_pdf_message)
    send_message(service, 'me', back_pdf_message)


if __name__ == '__main__':
    main()
