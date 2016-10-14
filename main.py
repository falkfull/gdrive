from googleapiclient.discovery import build
from oauth2client.file import Storage
from oauth2client import client, tools
from httplib2 import Http
import os
import argparse


def get_credentials():
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
                                   'drive-skilled.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets('client_secret.json', 'https://www.googleapis.com/auth/drive.file')
        flow.user_agent = 'skilled_cli'
        flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        print('Storing credentials to ' + credential_path)
    return credentials


def upload_spreadsheet(filename, drive):
    mimeType = 'application/vnd.google-apps.spreadsheet'
    metadata = {'name': filename}
    metadata['mimeType'] = mimeType
    res = drive.files().create(body=metadata, media_body=filename).execute()
    if res:
        print('Uploaded {}, ({}), {}'.format(filename, res['mimeType'], res['id']))
    return res['id']


def add_permission(file_id, drive):
    batch = drive.new_batch_http_request()
    user_permission = {
        'type': 'user',
        'role': 'writer',
        'emailAddress': 'example@gmail.com'
    }

    batch.add(drive.permissions().create(
        fileId=file_id,
        body=user_permission,
        fields='id',
    ))
    batch.execute()


filename = 'test_upload_output.csv'

credentials = get_credentials()
drive = build('drive', 'v3', credentials.authorize(Http()))

file_id = upload_spreadsheet(filename, drive)
add_permission(file_id, drive)
