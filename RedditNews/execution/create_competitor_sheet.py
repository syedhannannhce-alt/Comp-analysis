import os
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def main():
    creds = None
    if os.path.exists('token.json'):
        try:
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        except Exception as e:
            print(f"Error loading token.json: {e}")
            
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists('credentials.json'):
                print("credentials.json not found! Please provide credentials.json or use a Service Account.")
                return
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('sheets', 'v4', credentials=creds)

        # Create a new spreadsheet
        spreadsheet_body = {
            'properties': {
                'title': 'AutoNgage Competitors 2026'
            }
        }
        
        request = service.spreadsheets().create(body=spreadsheet_body)
        response = request.execute()
        spreadsheet_id = response.get('spreadsheetId')
        print(f"Spreadsheet ID: {spreadsheet_id}")
        print(f"Spreadsheet URL: {response.get('spreadsheetUrl')}")

        # Add data
        values = [
            ["Website", "Offering", "USP", "Targeted Country"],
            ["https://impel.io", "AI Conversational Platform & Merchandising", "Deep integrations with automotive CRMs and dynamic 360-degree vehicle tours", "USA / Global"],
            ["https://autoleadstar.com", "Customer Data Platform & AI Marketing", "End-to-end automation from marketing to lead capture specifically for auto dealers", "USA / Israel"],
            ["https://gubagoo.com", "Chatbot & Digital Retailing", "Chatbot with seamless handoff to human operators and integrated financing/trade-in tools", "USA / Canada"],
            ["https://carlabs.ai", "AI Conversational Commerce", "Advanced NLP for finding inventory and answering complex automotive queries", "USA"],
            ["https://www.numa.com", "AI answering service and communication platform", "AI that answers missed calls and texts customers back automatically for busy service departments", "USA"],
            ["https://www.spyne.ai", "AI Cataloging & Merchandising", "AI-driven image editing and 360-degree views for vehicle listings", "India / Global"],
            ["https://kenect.com", "Business Texting & Reputation Management", "Transforms main business lines into textable channels and automates review generation", "USA"]
        ]
        
        body = {
            'values': values
        }
        
        result = service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id, range='Sheet1!A1:D8',
            valueInputOption='USER_ENTERED', body=body).execute()
        
        print(f"{result.get('updatedCells')} cells updated.")
        
    except HttpError as err:
        print(err)

if __name__ == '__main__':
    main()
