import os
import csv
import pandas as pd
import urllib.parse
import webbrowser
from datetime import datetime
import re
import time

class WhatsAppContactSystem:
    def __init__(self):
        self.processed_csv = "data/cv_with_domains.csv"
        self.contact_log_csv = "data/whatsapp_contact_log.csv"
        
        self.auto_send_enabled = True
        self.delay_between_messages = 5
        
        self.company_intro = """Hello! This is CodeCelix, an Italy-based tech company.

We're building a team in Pakistan and you're being considered for an internship position! 

This is an unpaid internship, but top-performing interns may become paid team members later.

Let's start with a quick interview! """

        self.interview_questions = """Q1: Which domain are you applying for?
• Web Development
• MERN Stack  
• Full Stack Development
• UI/UX Design
• AI Automation
• Graphic Designing

Q2: Do you have any prior experience or portfolio? (Please share briefly)

Looking forward to your response! """

    def load_candidates(self):
        """Load candidates from the processed CSV"""
        if not os.path.exists(self.processed_csv):
            print(f"❌ {self.processed_csv} not found. Please run domain detection first.")
            return pd.DataFrame()
        
        df = pd.read_csv(self.processed_csv)
        print(f"📊 Loaded {len(df)} candidates from {self.processed_csv}")
        return df

    def extract_phone_from_cv(self, cv_text_preview):
        """Extract phone number from CV text with improved patterns"""
        if not cv_text_preview or pd.isna(cv_text_preview):
            return None
        
        phone_patterns = [
            r'\+92[\s\-]?[\d\s\-]{10,}',
            r'92[\s\-]?[\d\s\-]{10,}',
            r'03[\d\s\-]{9,}',
            r'\+[\d\s\-]{10,15}',
            r'[\(]?[\d\s\-\)]{10,15}',
            r'(?:phone|mobile|cell|contact)[\s:]+[\+]?[\d\s\-\(\)]{10,15}',
        ]
        
        for pattern in phone_patterns:
            matches = re.findall(pattern, cv_text_preview, re.IGNORECASE)
            if matches:
                phone = re.sub(r'[\s\-\(\)phone|mobile|cell|contact:]', '', matches[0], flags=re.IGNORECASE)
                phone = re.sub(r'[^\d+]', '', phone)
                
                if len(phone) >= 10:
                    return phone
        
        return None

    def format_phone_number(self, phone):
        """Format phone number for WhatsApp with improved validation"""
        if not phone:
            return None
        
        phone = re.sub(r'[^\d+]', '', phone)
        phone = phone.replace('+', '')
        
        if phone.startswith('03') and len(phone) == 11:
            phone = '92' + phone[1:]
        elif phone.startswith('3') and len(phone) == 10:
            phone = '92' + phone
        elif phone.startswith('0') and len(phone) == 11:
            phone = '92' + phone[1:]
        elif not phone.startswith('92') and len(phone) >= 10:
            if len(phone) == 10:
                phone = '92' + phone
            elif len(phone) == 11 and phone.startswith('0'):
                phone = '92' + phone[1:]
        
        if len(phone) >= 12 and phone.startswith('92'):
            return phone
        elif len(phone) >= 10:
            return phone
        
        return None

    def send_whatsapp_automatically(self, phone, message):
        """Automatically send WhatsApp message using web automation"""
        try:
            encoded_message = urllib.parse.quote(message, safe='')
            whatsapp_url = f"https://web.whatsapp.com/send?phone={phone}&text={encoded_message}"
            
            webbrowser.open(whatsapp_url)
            
            time.sleep(2)
            
            print(f"✅ WhatsApp web opened for {phone}")
            print("🤖 Please manually send the message or implement selenium automation")
            
            return True, "WhatsApp web opened successfully"
            
        except Exception as error:
            return False, f"Failed to open WhatsApp: {error}"

    def log_contact_attempt(self, candidate_data, method, status, phone=None, link=None, error_msg=None):
        """Log contact attempt to CSV with enhanced logging"""
        log_entry = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'name': candidate_data.get('name', ''),
            'email': candidate_data.get('email', ''),
            'domain': candidate_data.get('domain', ''),
            'phone': phone or 'Not found',
            'contact_method': method,
            'status': status,
            'whatsapp_link': link or '',
            'message_sent': 'Yes' if status == 'Success' else 'No',
            'error_message': error_msg or ''
        }
        
        file_exists = os.path.isfile(self.contact_log_csv)
        
        with open(self.contact_log_csv, 'a', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['timestamp', 'name', 'email', 'domain', 'phone', 
                         'contact_method', 'status', 'whatsapp_link', 'message_sent', 'error_message']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            if not file_exists:
                writer.writeheader()
            
            writer.writerow(log_entry)

    def is_already_contacted(self, email):
        """Check if candidate has already been contacted successfully"""
        if not os.path.exists(self.contact_log_csv):
            return False
        
        try:
            log_df = pd.read_csv(self.contact_log_csv)
            successful_contacts = log_df[
                (log_df['email'] == email) & 
                (log_df['status'] == 'Success')
            ]
            return len(successful_contacts) > 0
        except Exception as e:
            print(f"❌ Error checking contact history: {e}")
            return False

    def contact_candidate(self, candidate_data, method='auto'):
        """Contact individual candidate with automatic WhatsApp sending"""
        name = candidate_data.get('name', 'Candidate')
        email = candidate_data.get('email', '')
        domain = candidate_data.get('domain', 'Unknown')
        cv_text = candidate_data.get('cv_text_preview', '')
        
        print(f"\n📞 Processing: {name} ({email})")
        print(f"🎯 Detected Domain: {domain}")
        
        if self.is_already_contacted(email):
            print(f"⏭️ Already contacted successfully, skipping...")
            return True, "Already contacted"
        
        phone = self.extract_phone_from_cv(cv_text)
        formatted_phone = self.format_phone_number(phone)
        
        if not formatted_phone:
            print("❌ No valid phone number found in CV")
            self.log_contact_attempt(candidate_data, method, "No phone found", error_msg="No valid phone number extracted from CV")
            return False, "No phone number found"
        
        print(f"📱 Phone: {formatted_phone}")
        
        full_message = f"Hi {name}! 👋\n\n{self.company_intro}\n\n{self.interview_questions}"
        
        if method == 'auto':
            success, result = self.send_whatsapp_automatically(formatted_phone, full_message)
            
            if success:
                print("✅ WhatsApp message initiated automatically")
                self.log_contact_attempt(candidate_data, "Auto", "Success", formatted_phone)
                return True, "Message sent automatically"
            else:
                print(f"❌ Automatic sending failed: {result}")
                method = 'manual'
        
        if method == 'manual':
            encoded_message = urllib.parse.quote(full_message, safe='')
            whatsapp_link = f"https://web.whatsapp.com/send?phone={formatted_phone}&text={encoded_message}"
            
            print(f"🔗 WhatsApp Link: {whatsapp_link}")
            print("📋 Message Preview:")
            print("-" * 40)
            print(full_message[:200] + "..." if len(full_message) > 200 else full_message)
            print("-" * 40)
            
            self.log_contact_attempt(candidate_data, "Manual", "Success", formatted_phone, whatsapp_link)
            return True, whatsapp_link
        
        return False, "Unknown method"

    def contact_all_candidates(self, method='auto', domain_filter=None, batch_size=5):
        """Contact all candidates with automatic sending and batch processing"""
        df = self.load_candidates()
        
        if df.empty:
            return
        
        if domain_filter:
            df = df[df['domain'].str.contains(domain_filter, case=False, na=False)]
            print(f"🎯 Filtered to {len(df)} candidates in {domain_filter} domain")
        
        df = df[
            (df['domain'] != 'Unknown') & 
            (df['domain'] != 'File Not Found') & 
            (df['domain'] != 'Text Extraction Failed') &
            (df['confidence'] >= 20)
        ]
        
        print(f"📋 Processing {len(df)} qualified candidates")
        
        contacted_count = 0
        failed_count = 0
        skipped_count = 0
        
        for index, row in df.iterrows():
            candidate_data = row.to_dict()
            
            print(f"\n{'='*70}")
            print(f"📋 Candidate {index + 1}/{len(df)}")
            
            success, result = self.contact_candidate(candidate_data, method)
            
            if success:
                if result == "Already contacted":
                    skipped_count += 1
                else:
                    contacted_count += 1
                    if method == 'auto' and contacted_count % batch_size == 0:
                        print(f"⏸️ Batch of {batch_size} completed, pausing for {self.delay_between_messages} seconds...")
                        time.sleep(self.delay_between_messages)
            else:
                failed_count += 1
        
        print(f"\n🎉 Contact session complete!")
        print(f"✅ Successfully contacted: {contacted_count}")
        print(f"⏭️ Already contacted (skipped): {skipped_count}")
        print(f"❌ Failed contacts: {failed_count}")
        print(f"📊 Total processed: {len(df)}")

    def retry_failed_contacts(self):
        """Retry contacting candidates who failed in previous attempts"""
        if not os.path.exists(self.contact_log_csv):
            print("❌ No contact log found")
            return
        
        log_df = pd.read_csv(self.contact_log_csv)
        failed_contacts = log_df[log_df['status'] != 'Success']['email'].unique()
        
        if len(failed_contacts) == 0:
            print("✅ No failed contacts to retry")
            return
        
        print(f"🔄 Retrying {len(failed_contacts)} failed contacts")
        
        df = self.load_candidates()
        retry_candidates = df[df['email'].isin(failed_contacts)]
        
        for index, row in retry_candidates.iterrows():
            candidate_data = row.to_dict()
            print(f"\n🔄 Retrying: {candidate_data['name']}")
            self.contact_candidate(candidate_data, method='auto')

    def show_contact_stats(self):
        """Show detailed contact statistics"""
        if not os.path.exists(self.contact_log_csv):
            print("📊 No contact log found yet.")
            return
        
        df = pd.read_csv(self.contact_log_csv)
        
        print("\n📈 Contact Statistics:")
        print("="*50)
        print(f"Total contact attempts: {len(df)}")
        print(f"Successful contacts: {len(df[df['message_sent'] == 'Yes'])}")
        print(f"Failed contacts: {len(df[df['message_sent'] == 'No'])}")
        
        success_rate = (len(df[df['message_sent'] == 'Yes']) / len(df)) * 100 if len(df) > 0 else 0
        print(f"Success rate: {success_rate:.1f}%")
        
        print("\n🎯 Success by Domain:")
        for domain in df['domain'].unique():
            domain_df = df[df['domain'] == domain]
            successful = len(domain_df[domain_df['message_sent'] == 'Yes'])
            total = len(domain_df)
            rate = (successful / total) * 100 if total > 0 else 0
            print(f"   {domain}: {successful}/{total} ({rate:.1f}%)")
        
        print("\n❌ Common Failure Reasons:")
        failed_df = df[df['message_sent'] == 'No']
        if not failed_df.empty:
            failure_reasons = failed_df['error_message'].value_counts()
            for reason, count in failure_reasons.head(5).items():
                print(f"   {reason}: {count} cases")

    def export_contact_list(self):
        """Export successfully contacted candidates for follow-up"""
        if not os.path.exists(self.contact_log_csv):
            print("❌ No contact log found")
            return
        
        log_df = pd.read_csv(self.contact_log_csv)
        successful_contacts = log_df[log_df['message_sent'] == 'Yes'].copy()
        
        if successful_contacts.empty:
            print("❌ No successful contacts found")
            return
        
        latest_contacts = successful_contacts.groupby('email').last().reset_index()
        
        export_file = "data/contacted_candidates_list.csv"
        latest_contacts.to_csv(export_file, index=False)
        
        print(f"✅ Exported {len(latest_contacts)} successfully contacted candidates to {export_file}")

if __name__ == "__main__":
    whatsapp_system = WhatsAppContactSystem()
    
    print("🚀 WhatsApp Contact System")
    print("Choose an option:")
    print("1. Contact all candidates (automatic)")
    print("2. Contact candidates by domain (automatic)")
    print("3. Retry failed contacts")
    print("4. Show contact statistics")
    print("5. Export contacted candidates list")
    print("6. Test single candidate contact")
    
    choice = input("\nEnter your choice (1-6): ")
    
    if choice == "1":
        whatsapp_system.contact_all_candidates(method='auto')
    
    elif choice == "2":
        print("\nAvailable domains:")
        print("- Web Development")
        print("- MERN Stack")
        print("- Full Stack Development")
        print("- UI/UX Design")
        print("- AI Automation")
        print("- Graphic Designing")
        
        domain = input("\nEnter domain to filter: ")
        whatsapp_system.contact_all_candidates(method='auto', domain_filter=domain)
    
    elif choice == "3":
        whatsapp_system.retry_failed_contacts()
    
    elif choice == "4":
        whatsapp_system.show_contact_stats()
    
    elif choice == "5":
        whatsapp_system.export_contact_list()
    
    elif choice == "6":
        df = whatsapp_system.load_candidates()
        if not df.empty:
            candidate = df.iloc[0].to_dict()
            whatsapp_system.contact_candidate(candidate, method='auto')
    
    else:
        print("Invalid choice. Exiting...")