import os
import base64
import csv
from datetime import datetime
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pandas as pd
import re

class GmailCVScanner:
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
        self.service = None
        
        self.cv_folder = "downloaded_cvs"
        self.csv_file = "data/cv_applications.csv"
        
        for folder in [self.cv_folder, "data"]:
            if not os.path.exists(folder):
                os.makedirs(folder)
    
    def authenticate_gmail(self):
        """Authenticate and create Gmail service"""
        creds = None
        
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        
        self.service = build('gmail', 'v1', credentials=creds)
        print("✅ Gmail authentication successful!")
    
    def get_unread_emails_with_attachments(self):
        """Get unread emails with PDF/DOCX attachments"""
        try:
            query = 'is:unread has:attachment'
            result = self.service.users().messages().list(userId='me', q=query).execute()
            messages = result.get('messages', [])
            
            print(f"📧 Found {len(messages)} unread emails with attachments")
            return messages
            
        except Exception as error:
            print(f"❌ Error getting emails: {error}")
            return []
    
    def is_duplicate_application(self, email):
        """Check if this email has already been processed"""
        if not os.path.exists(self.csv_file):
            return False
        
        try:
            existing_df = pd.read_csv(self.csv_file)
            return email in existing_df['email'].values
        except Exception as e:
            print(f"❌ Error checking duplicates: {e}")
            return False
    
    def extract_email_data(self, message_id):
        """Extract email data and check for CV attachments"""
        try:
            message = self.service.users().messages().get(userId='me', id=message_id).execute()
            
            headers = message['payload'].get('headers', [])
            sender_email = ""
            sender_name = ""
            subject = ""
            
            for header in headers:
                if header['name'] == 'From':
                    from_field = header['value']
                    match = re.match(r'(.*?)\s*<(.+?)>', from_field)
                    if match:
                        sender_name = match.group(1).strip().strip('"')
                        sender_email = match.group(2).strip()
                    else:
                        sender_email = from_field
                        sender_name = sender_email.split('@')[0]
                
                elif header['name'] == 'Subject':
                    subject = header['value']
            
            if self.is_duplicate_application(sender_email):
                print(f"⏭️ Skipping duplicate application from: {sender_name} ({sender_email})")
                return None
            
            cv_found = False
            attachments = self.get_attachments(message)
            
            for attachment in attachments:
                filename = attachment['filename'].lower()
                if any(ext in filename for ext in ['.pdf', '.docx', '.doc']) and \
                   any(keyword in filename for keyword in ['cv', 'resume', 'curriculum']):
                    cv_found = True
                    self.download_attachment(message_id, attachment, sender_name)
                    break
            
            if cv_found:
                return {
                    'name': sender_name,
                    'email': sender_email,
                    'subject': subject,
                    'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'message_id': message_id
                }
            
            return None
            
        except Exception as error:
            print(f"❌ Error extracting email data: {error}")
            return None
    
    def get_attachments(self, message):
        """Get attachments from email message"""
        attachments = []
        
        def extract_attachments(part):
            if 'parts' in part:
                for subpart in part['parts']:
                    extract_attachments(subpart)
            elif part.get('filename'):
                attachments.append({
                    'filename': part['filename'],
                    'attachment_id': part['body'].get('attachmentId'),
                    'size': part['body'].get('size', 0)
                })
        
        if 'parts' in message['payload']:
            for part in message['payload']['parts']:
                extract_attachments(part)
        elif message['payload'].get('filename'):
            attachments.append({
                'filename': message['payload']['filename'],
                'attachment_id': message['payload']['body'].get('attachmentId'),
                'size': message['payload']['body'].get('size', 0)
            })
        
        return attachments
    
    def download_attachment(self, message_id, attachment, sender_name):
        """Download CV attachment"""
        try:
            if attachment['attachment_id']:
                att = self.service.users().messages().attachments().get(
                    userId='me', messageId=message_id, id=attachment['attachment_id']
                ).execute()
                
                data = att['data']
                file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))
                
                safe_name = re.sub(r'[^\w\s-]', '', sender_name).strip()
                filename = f"{safe_name}_{attachment['filename']}"
                filepath = os.path.join(self.cv_folder, filename)
                
                if os.path.exists(filepath):
                    print(f"📄 CV already exists: {filename}")
                    return True
                
                with open(filepath, 'wb') as f:
                    f.write(file_data)
                
                print(f"📄 Downloaded CV: {filename}")
                return True
                
        except Exception as error:
            print(f"❌ Error downloading attachment: {error}")
            return False
    
    def save_to_csv(self, data):
        """Save CV data to CSV file"""
        try:
            file_exists = os.path.isfile(self.csv_file)
            
            with open(self.csv_file, 'a', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['name', 'email', 'subject', 'date', 'message_id']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                if not file_exists:
                    writer.writeheader()
                
                writer.writerow(data)
            
            print(f"💾 Saved to CSV: {data['name']} - {data['email']}")
            
        except Exception as error:
            print(f"❌ Error saving to CSV: {error}")
    
    def scan_and_process_cvs(self):
        """Main function to scan emails and process CVs"""
        print("🚀 Starting CV scanning process...")
        
        self.authenticate_gmail()
        
        messages = self.get_unread_emails_with_attachments()
        
        processed_count = 0
        skipped_count = 0
        
        for message in messages:
            message_id = message['id']
            cv_data = self.extract_email_data(message_id)
            
            if cv_data:
                self.save_to_csv(cv_data)
                processed_count += 1
                print(f"✅ Processed CV from: {cv_data['name']}")
            elif cv_data is None:
                skipped_count += 1
        
        print(f"\n🎉 Processing complete!")
        print(f"📊 New CVs processed: {processed_count}")
        print(f"⏭️ Duplicates skipped: {skipped_count}")
        return processed_count

if __name__ == "__main__":
    scanner = GmailCVScanner()
    scanner.scan_and_process_cvs()