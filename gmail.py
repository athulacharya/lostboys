from __future__ import print_function

from email.mime.text import MIMEText
import base64
import email

import os

from apiclient import errors
import oauth2client
from oauth2client import client
from oauth2client import tools

import argparse

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
    return {'raw': str(base64.urlsafe_b64encode(message.as_bytes()), "UTF-8")}

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
        message = (service.users().messages().send(userId=user_id, body=message)
                   .execute())
        return message
    except errors.HttpError as error:
        print('An error occurred: %s' % error)

def query_threads(service, user_id, query=''):
    """List all Threads of the user's mailbox matching the query.

    Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. The special value "me"
                 can be used to indicate the authenticated user.
        query: String used to filter messages returned.
               Eg. 'label:UNREAD' for unread messages only.

    Returns:
        List of threads that match the criteria of the query. Note that the returned
        list contains Thread IDs, you must use get with the appropriate
        ID to get the details for a Thread.
    """

    try:
        response = service.users().threads().list(userId=user_id, q=query).execute()
        threads = []
        if 'threads' in response:
            threads.extend(response['threads'])

        while 'nextPageToken' in response:
            page_token = response['nextPageToken']
            response = service.users().threads().list(userId=user_id, q=query,
                                                      pageToken=page_token).execute()
            threads.extend(response['threads'])

        return threads
    except errors.HttpError as error:
        print('An error occurred: %s' % error)

def query_msgs(service, user_id, query=''):
    """List all Messages of the user's mailbox matching the query.

    Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. The special value "me"
                 can be used to indicate the authenticated user.
        query: String used to filter messages returned.
               Eg. 'label:UNREAD' for unread messages only.

    Returns:
        List of Messages that match the criteria of the query. Note that the returned
        list contains Messages IDs, you must use get with the appropriate
        ID to get the details for a Messages.
    """

    try:
        response = service.users().messages().list(userId=user_id, q=query).execute()
        messages = []
        if 'messages' in response:
            messages.extend(response['messages'])

        while 'nextPageToken' in response:
            page_token = response['nextPageToken']
            response = service.users().messages().list(userId=user_id, q=query,
                                                       pageToken=page_token).execute()
            messages.extend(response['messages'])

        return messages
    except errors.HttpError as error:
        print('An error occurred: %s' % error)

def mark_message_read(service, user_id, msg_id):
    """Mark a message as read (by removing the UNREAD label).

    Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. The special value "me"
                 can be used to indicate the authenticated user.
        msg_id: The ID of the Message to mark read.

    Returns:
        Modified message.
    """
    try:
        msg_labels = {'removeLabelIds': ['UNREAD'], 'addLabelIds': []}
        message = service.users().messages().modify(userId=user_id, id=msg_id,
                                                 body=msg_labels).execute()
        return message
    except errors.HttpError as error:
        print('An error occurred: %s' % error)

def get_message(service, user_id, msg_id):
    """Get a Message and use it to create a MIME Message.

    Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. The special value "me"
                 can be used to indicate the authenticated user.
        msg_id: The ID of the Message required.

    Returns:
        A MIME Message, consisting of data from Message.
    """
    try:
        message = service.users().messages().get(userId=user_id, id=msg_id,
                                                 format='raw').execute()

        msg_str = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))
        mime_msg = email.message_from_bytes(msg_str)

        return mime_msg
    except errors.HttpError as error:
        print('An error occurred: %s' % error)

def get_credentials(client_secrets, scopes, user_agent):
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'gmail-lostboys.json')

    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
    flags.noauth_local_webserver = True

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(client_secrets, scopes)
        flow.user_agent = user_agent
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials
