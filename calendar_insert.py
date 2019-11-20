
from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request



def CalenderInsert(event_name, event_location, event_description, event_start_time, event_end_time):
    # If modifying these scopes, delete the file token.pickle.
    SCOPES = ['https://www.googleapis.com/auth/calendar']
     
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)


    service = build('calendar', 'v3', credentials=creds)


    event = {
        'summary': event_name,
        'location': event_location,
        'description': event_description,
        'start': {
            'dateTime': event_start_time.isoformat("T") + "Z",
          },
        'end': {
            'dateTime': event_end_time.isoformat("T") + "Z",
        },
    }

    # Insert Event into the Calendar API
    event = service.events().insert(calendarId='primary', body=event).execute()
    

