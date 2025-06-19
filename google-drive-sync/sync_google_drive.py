import os
import io
import pickle
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# CONFIG
SCOPES = ['https://www.googleapis.com/auth/drive']
DRIVE_FOLDER_ID = '13coH2a1pOjbGSzZ7leJzrSyvvV0EcVh3'
DESTINATION_FOLDER = os.getenv('DESTINATION_FOLDER','/consume')
CREDENTIALS_FILE = 'credentials.json'
TOKEN_PICKLE = os.getenv('TOKEN_PICKLE','/data/token.pickle')
DELETE_AFTER_DOWNLOAD = os.getenv('DELETE_AFTER_DOWNLOAD', 'false').lower() == 'true'

def authenticate():
    creds = None
    if os.path.exists(TOKEN_PICKLE):
        with open(TOKEN_PICKLE, 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PICKLE, 'wb') as token:
            pickle.dump(creds, token)
    return creds

def list_files(service, folder_id):
    results = service.files().list(
        q=f"'{folder_id}' in parents and trashed = false",
        fields="files(id, name, mimeType)"
    ).execute()
    return results.get('files', [])

def download_file(service, file_id, file_name):
    request = service.files().get_media(fileId=file_id)
    fh = io.FileIO(os.path.join(DESTINATION_FOLDER, file_name), 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()

def main():
    creds = authenticate()
    service = build('drive', 'v3', credentials=creds)
    
    files = list_files(service, DRIVE_FOLDER_ID)
    for file in files:
        destination_path = os.path.join(DESTINATION_FOLDER, file['name'])
        if not os.path.exists(destination_path):
            print(f"Downloading {file['name']}...")
            try:
                download_file(service, file['id'], file['name'])
                print(f"Downloaded {file['name']}, deleting from Drive ...")
                service.files().delete(fileId=file['id']).execute()
            except Exception as e:
                print(f"Failed to download/delete {file['name']}: {e}")

if __name__ == '__main__':
    main()
