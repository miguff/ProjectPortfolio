import os.path
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta
import osenv
# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


class EmailDownload:

    def __init__(self, query: str, subfolder, renamefile: bool = True):
        self.query = query
        self.renamefile = renamefile
        self.current_date = datetime.now()
        self.current_month = self.current_date.strftime("%m")
        self.previous_month_date = self.current_date.replace(day=1) - timedelta(days=1)
        self.previous_month = self.previous_month_date.strftime("%m")
        self.foldername = "Emailattachments"
        self.subfolder = subfolder
        os.makedirs(self.foldername, exist_ok=True)
        os.makedirs(f"{self.foldername}/{self.previous_month}", exist_ok=True)
        os.makedirs(f"{self.foldername}/{self.current_month}", exist_ok=True)
        os.makedirs(f"{self.foldername}/{self.previous_month}/{self.subfolder}", exist_ok=True)
        os.makedirs(f"{self.foldername}/{self.current_month}/{self.subfolder}", exist_ok=True)
        self.lastpath = f"{self.foldername}/{self.previous_month}/{self.subfolder}"
        self.currentpath = f"{self.foldername}/{self.current_month}/{self.subfolder}"
    
    def fileDownloader(self):
        creds = self.checkiftokenexist()
        
        try:
            # Call the Gmail API
            service = build("gmail", "v1", credentials=creds)
            results = service.users().messages().list(userId="me", q=self.query).execute()
            messages = results.get("messages", [])

            if not messages:
                print("No messages found.")
                return
            
            
            for message in messages:
                msg = service.users().messages().get(userId='me', id=message['id']).execute()
                payload = msg['payload']
                headers = payload.get('headers', [])
                subject = next((header['value'] for header in headers if header['name'].lower() == 'subject'), None)
                print(subject)
                parts = payload.get('parts', [])
                for part in parts:
                    if part.get('filename'):
                        print(f"Processing attachment: {part['filename']}")
                        if 'data' in part['body']:
                            data = part['body']['data']
                        elif 'attachmentId' in part['body']:
                            attachment_id = part['body']['attachmentId']
                            attachment = service.users().messages().attachments().get(
                                userId='me', messageId=message['id'], id=attachment_id
                            ).execute()
                            data = attachment['data']
                        else:
                            continue

                        # Decode and save the attachment
                        file_data = base64.urlsafe_b64decode(data)
                        
                        if self.renamefile:
                            filepath = os.path.join(self.lastpath, part['filename'])
                            donefilepath = os.path.join(self.lastpath, f"Done - {part['filename']}")
                            if not os.path.exists(filepath) and not os.path.exists(donefilepath):
                                with open(filepath, 'wb') as f:
                                    f.write(file_data)
                                print(f"Downloaded: {part['filename']}")
                            else:
                                print("Already Downloaded (Portfolio)")
                                break
                        else:
                            filepath = os.path.join(self.currentpath, f"{subject}.pdf")
                            donefilepath = os.path.join(self.currentpath, f"Done - {subject}.pdf")
                            if not os.path.exists(filepath) and not os.path.exists(donefilepath):
                                with open(filepath, 'wb') as f:
                                    f.write(file_data)
                                print(f"Downloaded: {filepath}")
                            else:
                                print("Already Downloaded (Dividend)")
                                break
                break

        except HttpError as error:
            # TODO(developer) - Handle errors from gmail API.
            print(f"An error occurred: {error}")
        if self.renamefile:
            return self.lastpath
        else:
            return self.currentpath

    def checkiftokenexist(self):
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(os.environ['TokenPath']):
            creds = Credentials.from_authorized_user_file(os.environ['TokenPath'], SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                flow = InstalledAppFlow.from_client_secrets_file(
                os.environ['CredentialsPath'], SCOPES
            )
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                os.environ['CredentialsPath'], SCOPES
            )
            creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(os.environ['TokenPath'], "w") as token:
                token.write(creds.to_json())
        return creds

