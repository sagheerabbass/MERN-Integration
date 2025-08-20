import os
import csv
import pandas as pd
import urllib.parse
import webbrowser
from datetime import datetime
import time

class ShortlistGroupInvite:
    def __init__(self):
        self.responses_csv = "data/candidate_responses.csv"
        self.shortlist_log_csv = "data/shortlist_invites_log.csv"
        
        self.whatsapp_group_link = "https://chat.whatsapp.com/YOUR_GROUP_INVITE_LINK_HERE"
        
        self.shortlist_message = """🎉 Congratulations! 🎉

You are shortlisted for the CodeCelix Internship! 

We were impressed with your responses and believe you'd be a great fit for our team. 

Please join the shortlisted interns group using this link:

{group_link}

Welcome to the CodeCelix family! 🚀

Next steps will be shared in the group. Looking forward to working with you! 💪

Best regards,
CodeCelix Team"""

        self.rejection_message = """Thank you for your interest in CodeCelix internship! 

After careful consideration, we have decided to move forward with other candidates for this round.

However, we encourage you to keep improving your skills and apply again in the future. 

Best of luck with your career journey! 💪

Best regards,
CodeCelix Team"""

    def load_candidate_responses(self):
        """Load candidate responses with phone numbers from contact log"""
        if not os.path.exists(self.responses_csv):
            print(f"❌ {self.responses_csv} not found. Please create response tracker first.")
            return pd.DataFrame()
        
        responses_df = pd.read_csv(self.responses_csv)
        
        contact_log_file = "data/whatsapp_contact_log.csv"
        if os.path.exists(contact_log_file):
            contact_df = pd.read_csv(contact_log_file)
            latest_contacts = contact_df.groupby('email').last().reset_index()
            responses_df = responses_df.merge(
                latest_contacts[['email', 'phone']], 
                on='email', 
                how='left',
                suffixes=('', '_contact')
            )
            responses_df['phone'] = responses_df['phone_contact'].fillna(responses_df.get('phone', ''))
            responses_df = responses_df.drop(columns=['phone_contact'], errors='ignore')
        
        print(f"📊 Loaded {len(responses_df)} candidate responses with phone numbers")
        return responses_df

    def auto_evaluate_candidates(self):
        """Automatically evaluate candidates based on response quality and technical score"""
        df = self.load_candidate_responses()
        
        if df.empty:
            return df
        
        updated_count = 0
        
        for index, row in df.iterrows():
            if pd.notna(row['next_step']) and row['next_step'] != '':
                continue
            
            response_quality = str(row.get('response_quality', '')).strip()
            technical_score = row.get('technical_score', '')
            
            try:
                score = int(float(technical_score)) if technical_score != '' else 0
            except (ValueError, TypeError):
                score = 0
            
            if response_quality.lower() == 'poor' or score <= 5:
                df.at[index, 'next_step'] = "Reject"
                df.at[index, 'notes'] = df.at[index, 'notes'] + f" [Auto-rejected: Quality={response_quality}, Score={score}]"
                print(f"❌ Auto-rejected: {row['name']} (Quality: {response_quality}, Score: {score})")
                
            elif response_quality.lower() in ['good', 'excellent'] and score > 5:
                df.at[index, 'next_step'] = "Shortlist"
                df.at[index, 'notes'] = df.at[index, 'notes'] + f" [Auto-approved: Quality={response_quality}, Score={score}]"
                print(f"✅ Auto-shortlisted: {row['name']} (Quality: {response_quality}, Score: {score})")
                
            else:
                if response_quality.lower() != 'poor' and score != 0:
                    df.at[index, 'next_step'] = "Shortlist"
                    df.at[index, 'notes'] = df.at[index, 'notes'] + f" [Auto-approved (default): Quality={response_quality}, Score={score}]"
                    print(f"✅ Auto-shortlisted (default): {row['name']} (Quality: {response_quality}, Score: {score})")
                else:
                    df.at[index, 'next_step'] = "More Questions"
                    print(f"❓ Needs review: {row['name']} (Quality: {response_quality}, Score: {score})")
            
            updated_count += 1
        
        df.to_csv(self.responses_csv, index=False)
        print(f"\n💾 Auto-evaluated {updated_count} candidates")
        
        return df

    def get_shortlisted_candidates(self, df=None):
        """Get candidates marked for shortlisting"""
        if df is None:
            df = self.load_candidate_responses()
        
        if df.empty:
            return pd.DataFrame()
        
        shortlisted = df[df['next_step'].str.contains('Shortlist', case=False, na=False)].copy()
        print(f"🎯 Found {len(shortlisted)} candidates marked for shortlisting")
        
        return shortlisted

    def get_rejected_candidates(self, df=None):
        """Get candidates marked for rejection"""
        if df is None:
            df = self.load_candidate_responses()
        
        if df.empty:
            return pd.DataFrame()
        
        rejected = df[df['next_step'].str.contains('Reject', case=False, na=False)].copy()
        print(f"❌ Found {len(rejected)} candidates marked for rejection")
        
        return rejected

    def set_group_link(self, group_link):
        """Set the WhatsApp group invite link"""
        self.whatsapp_group_link = group_link
        print(f"✅ WhatsApp group link updated: {group_link}")

    def send_whatsapp_automatically(self, phone, message):
        """Automatically send WhatsApp message"""
        try:
            encoded_message = urllib.parse.quote(message, safe='')
            whatsapp_url = f"https://web.whatsapp.com/send?phone={phone}&text={encoded_message}"
            
            webbrowser.open(whatsapp_url)
            
            time.sleep(2)
            
            print(f"✅ WhatsApp web opened for automated message")
            return True, "WhatsApp web opened successfully"
            
        except Exception as error:
            return False, f"Failed to open WhatsApp: {error}"

    def is_already_processed(self, email, action_type):
        """Check if candidate has already been processed for this action"""
        if not os.path.exists(self.shortlist_log_csv):
            return False
        
        try:
            log_df = pd.read_csv(self.shortlist_log_csv)
            processed = log_df[
                (log_df['email'] == email) & 
                (log_df['action_type'] == action_type) & 
                (log_df['status'] == 'Success')
            ]
            return len(processed) > 0
        except Exception as e:
            print(f"❌ Error checking processing history: {e}")
            return False

    def send_shortlist_invite(self, candidate_data, method='auto'):
        """Send shortlist group invite to a candidate"""
        name = candidate_data.get('name', 'Candidate')
        email = candidate_data.get('email', '')
        domain = candidate_data.get('domain', 'Unknown')
        phone = candidate_data.get('phone', 'Not found')
        
        print(f"\n🎉 Processing shortlist invite: {name} ({email})")
        print(f"🎯 Domain: {domain}")
        print(f"📱 Phone: {phone}")
        
        if self.is_already_processed(email, 'shortlist'):
            print(f"⏭️ Shortlist invite already sent, skipping...")
            return True, "Already processed"
        
        if phone == 'Not found' or not phone:
            print("❌ No phone number available for this candidate")
            self.log_shortlist_invite(candidate_data, "shortlist", "No phone found", 
                                    error_msg="No phone number available")
            return False, "No phone number"
        
        if "YOUR_GROUP_INVITE_LINK_HERE" in self.whatsapp_group_link:
            print("⚠️  WhatsApp group link not set! Please set group link first.")
            self.log_shortlist_invite(candidate_data, "shortlist", "No group link", 
                                    error_msg="WhatsApp group link not configured")
            return False, "No group link set"
        
        personalized_message = f"Hi {name}! 👋\n\n" + self.shortlist_message.format(
            group_link=self.whatsapp_group_link
        )
        
        if method == 'auto':
            success, result = self.send_whatsapp_automatically(phone, personalized_message)
            
            if success:
                print("✅ Shortlist invite sent automatically")
                self.log_shortlist_invite(candidate_data, "shortlist", "Success")
                return True, "Invite sent automatically"
            else:
                print(f"❌ Automatic sending failed: {result}")
                method = 'manual'
        
        if method == 'manual':
            encoded_message = urllib.parse.quote(personalized_message, safe='')
            whatsapp_link = f"https://web.whatsapp.com/send?phone={phone}&text={encoded_message}"
            
            print(f"\n🔗 WhatsApp Link: {whatsapp_link}")
            print("\n🎉 Shortlist Message Preview:")
            print("-" * 60)
            print(personalized_message[:300] + "..." if len(personalized_message) > 300 else personalized_message)
            print("-" * 60)
            
            self.log_shortlist_invite(candidate_data, "shortlist", "Success", whatsapp_link)
            return True, whatsapp_link
        
        return False, "Unknown method"

    def send_rejection_message(self, candidate_data, method='auto'):
        """Send rejection message to a candidate"""
        name = candidate_data.get('name', 'Candidate')
        email = candidate_data.get('email', '')
        phone = candidate_data.get('phone', 'Not found')
        
        print(f"\n❌ Processing rejection message: {name} ({email})")
        print(f"📱 Phone: {phone}")
        
        if self.is_already_processed(email, 'rejection'):
            print(f"⏭️ Rejection message already sent, skipping...")
            return True, "Already processed"
        
        if phone == 'Not found' or not phone:
            print("❌ No phone number available for this candidate")
            self.log_shortlist_invite(candidate_data, "rejection", "No phone found",
                                    error_msg="No phone number available")
            return False, "No phone number"
        
        personalized_message = f"Hi {name},\n\n{self.rejection_message}"
        
        if method == 'auto':
            success, result = self.send_whatsapp_automatically(phone, personalized_message)
            
            if success:
                print("✅ Rejection message sent automatically")
                self.log_shortlist_invite(candidate_data, "rejection", "Success")
                return True, "Rejection sent automatically"
            else:
                print(f"❌ Automatic sending failed: {result}")
                method = 'manual'
        
        if method == 'manual':
            encoded_message = urllib.parse.quote(personalized_message, safe='')
            whatsapp_link = f"https://web.whatsapp.com/send?phone={phone}&text={encoded_message}"
            
            print(f"\n🔗 WhatsApp Link: {whatsapp_link}")
            print("\n📝 Rejection Message Preview:")
            print("-" * 60)
            print(personalized_message[:300] + "..." if len(personalized_message) > 300 else personalized_message)
            print("-" * 60)
            
            self.log_shortlist_invite(candidate_data, "rejection", "Success", whatsapp_link)
            return True, whatsapp_link
        
        return False, "Unknown method"

    def log_shortlist_invite(self, candidate_data, action_type, status, link=None, error_msg=None):
        """Log shortlist invite or rejection message"""
        log_entry = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'name': candidate_data.get('name', ''),
            'email': candidate_data.get('email', ''),
            'domain': candidate_data.get('domain', ''),
            'phone': candidate_data.get('phone', ''),
            'action_type': action_type,
            'status': status,
            'whatsapp_link': link or '',
            'group_link': self.whatsapp_group_link if action_type == 'shortlist' else 'N/A',
            'error_message': error_msg or ''
        }
        
        file_exists = os.path.isfile(self.shortlist_log_csv)
        
        with open(self.shortlist_log_csv, 'a', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['timestamp', 'name', 'email', 'domain', 'phone', 
                         'action_type', 'status', 'whatsapp_link', 'group_link', 'error_message']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            if not file_exists:
                writer.writeheader()
            
            writer.writerow(log_entry)

    def process_all_shortlisted(self, send_rejections=True, method='auto'):
        """Process all shortlisted candidates and optionally send rejections"""
        df = self.auto_evaluate_candidates()
        
        if df.empty:
            return
        
        shortlisted = self.get_shortlisted_candidates(df)
        
        shortlist_success = 0
        shortlist_failed = 0
        shortlist_skipped = 0
        
        if not shortlisted.empty:
            print(f"\n🎉 Processing {len(shortlisted)} shortlisted candidates...")
            
            for index, row in shortlisted.iterrows():
                candidate_data = row.to_dict()
                
                print(f"\n{'='*70}")
                print(f"🎉 Shortlist {index + 1}/{len(shortlisted)}")
                
                success, result = self.send_shortlist_invite(candidate_data, method=method)
                
                if success:
                    if result == "Already processed":
                        shortlist_skipped += 1
                    else:
                        shortlist_success += 1
                        if method == 'auto':
                            time.sleep(3)
                else:
                    shortlist_failed += 1
        
        rejection_success = 0
        rejection_failed = 0
        rejection_skipped = 0
        
        if send_rejections:
            rejected = self.get_rejected_candidates(df)
            
            if not rejected.empty:
                print(f"\n❌ Processing {len(rejected)} rejected candidates...")
                
                for index, row in rejected.iterrows():
                    candidate_data = row.to_dict()
                    
                    print(f"\n{'='*70}")
                    print(f"❌ Rejection {index + 1}/{len(rejected)}")
                    
                    success, result = self.send_rejection_message(candidate_data, method=method)
                    
                    if success:
                        if result == "Already processed":
                            rejection_skipped += 1
                        else:
                            rejection_success += 1
                            if method == 'auto':
                                time.sleep(3)
                    else:
                        rejection_failed += 1
        
        print(f"\n🎉 Processing complete!")
        print(f"✅ Shortlist invites sent: {shortlist_success}")
        print(f"⏭️ Shortlist already sent: {shortlist_skipped}")
        print(f"❌ Shortlist failed: {shortlist_failed}")
        
        if send_rejections:
            print(f"✅ Rejection messages sent: {rejection_success}")
            print(f"⏭️ Rejections already sent: {rejection_skipped}")
            print(f"❌ Rejections failed: {rejection_failed}")

    def show_shortlist_stats(self):
        """Show shortlist and rejection statistics"""
        if not os.path.exists(self.shortlist_log_csv):
            print("📊 No shortlist log found yet.")
            return
        
        df = pd.read_csv(self.shortlist_log_csv)
        
        print("\n📈 Shortlist & Rejection Statistics:")
        print("="*50)
        
        shortlist_success = len(df[(df['action_type'] == 'shortlist') & (df['status'] == 'Success')])
        rejection_success = len(df[(df['action_type'] == 'rejection') & (df['status'] == 'Success')])
        
        print(f"✅ Shortlist invites sent: {shortlist_success}")
        print(f"❌ Rejection messages sent: {rejection_success}")
        print(f"📊 Total communications: {len(df)}")
        
        shortlist_total = len(df[df['action_type'] == 'shortlist'])
        rejection_total = len(df[df['action_type'] == 'rejection'])
        
        if shortlist_total > 0:
            shortlist_rate = (shortlist_success / shortlist_total) * 100
            print(f"Shortlist success rate: {shortlist_rate:.1f}%")
        
        if rejection_total > 0:
            rejection_rate = (rejection_success / rejection_total) * 100
            print(f"Rejection success rate: {rejection_rate:.1f}%")
        
        print("\n🎯 Shortlisted Candidates by Domain:")
        shortlisted_df = df[(df['action_type'] == 'shortlist') & (df['status'] == 'Success')]
        if not shortlisted_df.empty:
            domain_stats = shortlisted_df['domain'].value_counts()
            for domain, count in domain_stats.items():
                print(f"   {domain}: {count} candidates")
        else:
            print("   No shortlisted candidates yet")

if __name__ == "__main__":
    shortlist_system = ShortlistGroupInvite()
    
    print("🚀 Shortlist Group Invite System")
    print("Choose an option:")
    print("1. Auto-evaluate and process all candidates (shortlist + rejections)")
    print("2. Process shortlisted candidates only (automatic)")
    print("3. Process both shortlist and rejections (automatic)")
    print("4. Show shortlist statistics")
    print("5. Set WhatsApp group link")
    print("6. Test shortlist invite for single candidate")
    
    choice = input("\nEnter your choice (1-6): ")
    
    if choice == "1":
        shortlist_system.process_all_shortlisted(send_rejections=True, method='auto')
    
    elif choice == "2":
        shortlist_system.process_all_shortlisted(send_rejections=False, method='auto')
    
    elif choice == "3":
        shortlist_system.process_all_shortlisted(send_rejections=True, method='auto')
    
    elif choice == "4":
        shortlist_system.show_shortlist_stats()
    
    elif choice == "5":
        group_link = input("Enter WhatsApp group invite link: ").strip()
        if group_link:
            shortlist_system.set_group_link(group_link)
        else:
            print("❌ No group link provided")
    
    elif choice == "6":
        df = shortlist_system.get_shortlisted_candidates()
        if not df.empty:
            candidate = df.iloc[0].to_dict()
            shortlist_system.send_shortlist_invite(candidate, method='auto')
        else:
            print("❌ No shortlisted candidates found")
    
    else:
        print("Invalid choice. Exiting...")