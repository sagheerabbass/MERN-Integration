import os
import csv
import pandas as pd
from datetime import datetime
import urllib.parse
import webbrowser
import time

class InterviewQuestionsGenerator:
    def __init__(self):
        self.contact_log_csv = "data/whatsapp_contact_log.csv"
        self.questions_log_csv = "data/interview_questions_log.csv"
        self.responses_csv = "data/candidate_responses.csv"
        
        self.interview_questions = {
            "Web Development": [
                "What projects have you made using HTML/CSS/JS? 🌐",
                "Are you familiar with frameworks like React or Node? ⚛️",
                "How do you host your websites or backend services? 🚀",
                "Have you worked with any CSS frameworks like Bootstrap or Tailwind? 🎨",
                "Do you know about responsive design and mobile-first approach? 📱"
            ],
            
            "MERN Stack": [
                "What projects have you made using HTML/CSS/JS? 🌐",
                "Are you familiar with frameworks like React or Node? ⚛️", 
                "How do you host your websites or backend services? 🚀",
                "Have you worked with MongoDB and Express.js? 🍃",
                "Do you understand state management with Redux or Context API? 📊",
                "Have you built any REST APIs or worked with authentication? 🔐"
            ],
            
            "Full Stack Development": [
                "What projects have you made using HTML/CSS/JS? 🌐",
                "Are you familiar with frameworks like React or Node? ⚛️",
                "How do you host your websites or backend services? 🚀",
                "Which databases have you worked with (SQL/NoSQL)? 🗄️",
                "Do you have experience with version control like Git? 📝",
                "Have you deployed applications on cloud platforms (AWS, Heroku)? ☁️"
            ],
            
            "UI/UX Design": [
                "Have you used tools like Figma or Adobe XD? 🎨",
                "Can you explain what a wireframe is? 📋",
                "Share any past design work if possible. 🖼️",
                "Do you understand user research and usability testing? 👥",
                "Have you created prototypes or interactive mockups? 🔧",
                "What's your design process from concept to final product? 🎯"
            ],
            
            "AI Automation": [
                "Have you built any automation tools or used Python scripts? 🐍",
                "Do you know about tools like Zapier, n8n, or LangChain? 🔗",
                "Share a simple use case you automated. ⚡",
                "Are you familiar with APIs and webhooks? 🌐",
                "Have you worked with any AI/ML libraries like TensorFlow or OpenAI? 🤖",
                "Do you understand workflow automation and business processes? 📈"
            ],
            
            "Graphic Designing": [
                "Which tools do you use (Photoshop, Illustrator, etc)? 🎨",
                "Share some of your designs or Behance/Dribbble profile. 🖼️",
                "Do you know how to prepare print vs digital files? 📄",
                "Have you created brand identities or logo designs? 🏷️",
                "Do you understand typography and color theory? 🌈",
                "Have you worked on packaging or marketing materials? 📦"
            ],
            
            "Accounting": [
                "Which accounting software have you used (QuickBooks, Excel, etc)? 💼",
                "Do you understand financial statements (Balance Sheet, P&L)? 📊",
                "Have you handled accounts payable/receivable? 💰",
                "Are you familiar with tax preparation and compliance? 📋",
                "Do you have experience with budgeting and financial analysis? 📈",
                "Have you worked with payroll processing? 💸"
            ]
        }
        
        self.followup_intro = """Thank you for your initial response! 😊

Based on your domain interest, here are some specific technical questions to better understand your experience:

"""
        
        self.followup_outro = """

Please answer these questions when you have time. This will help us understand your skill level and match you with the right projects! 🚀

Take your time - quality answers are more important than speed. 💪"""

    def load_contacted_candidates(self):
        """Load candidates who have been contacted via WhatsApp"""
        if not os.path.exists(self.contact_log_csv):
            print(f"❌ {self.contact_log_csv} not found. Please run WhatsApp contact system first.")
            return pd.DataFrame()
        
        df = pd.read_csv(self.contact_log_csv)
        
        contacted = df[df['message_sent'] == 'Yes'].copy()
        contacted = contacted.groupby('email').last().reset_index()
        
        print(f"📊 Found {len(contacted)} successfully contacted candidates")
        
        return contacted

    def generate_questions_for_domain(self, domain):
        """Generate interview questions for specific domain"""
        domain_key = None
        for key in self.interview_questions.keys():
            if key.lower() in domain.lower() or domain.lower() in key.lower():
                domain_key = key
                break
        
        if not domain_key:
            domain_key = "Web Development"
            print(f"⚠️  Unknown domain '{domain}', using Web Development questions")
        
        questions = self.interview_questions[domain_key]
        return questions, domain_key

    def create_followup_message(self, name, domain, questions):
        """Create personalized follow-up message with interview questions"""
        questions_text = ""
        for i, question in enumerate(questions, 1):
            questions_text += f"Q{i}: {question}\n\n"
        
        full_message = f"Hi {name}! 👋\n\n{self.followup_intro}{questions_text.strip()}{self.followup_outro}"
        return full_message

    def send_whatsapp_automatically(self, phone, message):
        """Automatically send WhatsApp message"""
        try:
            encoded_message = urllib.parse.quote(message, safe='')
            whatsapp_url = f"https://web.whatsapp.com/send?phone={phone}&text={encoded_message}"
            
            webbrowser.open(whatsapp_url)
            
            time.sleep(2)
            
            print(f"✅ WhatsApp web opened for follow-up questions")
            return True, "WhatsApp web opened successfully"
            
        except Exception as error:
            return False, f"Failed to open WhatsApp: {error}"

    def log_questions_sent(self, candidate_data, questions, method, status, link=None, error_msg=None):
        """Log interview questions sent to candidate"""
        log_entry = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'name': candidate_data.get('name', ''),
            'email': candidate_data.get('email', ''),
            'domain': candidate_data.get('domain', ''),
            'phone': candidate_data.get('phone', ''),
            'questions_sent': len(questions),
            'method': method,
            'status': status,
            'whatsapp_link': link or '',
            'questions_list': ' | '.join(questions),
            'error_message': error_msg or ''
        }
        
        file_exists = os.path.isfile(self.questions_log_csv)
        
        with open(self.questions_log_csv, 'a', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['timestamp', 'name', 'email', 'domain', 'phone', 
                         'questions_sent', 'method', 'status', 'whatsapp_link', 
                         'questions_list', 'error_message']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            if not file_exists:
                writer.writeheader()
            
            writer.writerow(log_entry)

    def is_questions_already_sent(self, email):
        """Check if questions have already been sent to this candidate"""
        if not os.path.exists(self.questions_log_csv):
            return False
        
        try:
            questions_df = pd.read_csv(self.questions_log_csv)
            sent_questions = questions_df[
                (questions_df['email'] == email) & 
                (questions_df['status'] == 'Success')
            ]
            return len(sent_questions) > 0
        except Exception as e:
            print(f"❌ Error checking questions history: {e}")
            return False

    def send_followup_questions(self, candidate_data, method='auto'):
        """Send follow-up interview questions to a candidate"""
        name = candidate_data.get('name', 'Candidate')
        domain = candidate_data.get('domain', 'Unknown')
        phone = candidate_data.get('phone', 'Not found')
        email = candidate_data.get('email', '')
        
        print(f"\n📋 Processing: {name} ({email})")
        print(f"🎯 Domain: {domain}")
        
        if self.is_questions_already_sent(email):
            print(f"⏭️ Questions already sent, skipping...")
            return True, "Questions already sent"
        
        questions, matched_domain = self.generate_questions_for_domain(domain)
        
        if matched_domain != domain:
            print(f"📝 Using {matched_domain} questions (closest match)")
        
        followup_message = self.create_followup_message(name, matched_domain, questions)
        
        print(f"📱 Phone: {phone}")
        print(f"❓ Questions to send: {len(questions)}")
        
        if phone == 'Not found' or not phone:
            print("❌ No phone number available for this candidate")
            self.log_questions_sent(candidate_data, questions, method, "No phone found", 
                                  error_msg="No phone number available")
            return False, "No phone number"
        
        if method == 'auto':
            success, result = self.send_whatsapp_automatically(phone, followup_message)
            
            if success:
                print("✅ Follow-up questions sent automatically")
                self.log_questions_sent(candidate_data, questions, "Auto", "Success")
                return True, "Questions sent automatically"
            else:
                print(f"❌ Automatic sending failed: {result}")
                method = 'manual'
        
        if method == 'manual':
            encoded_message = urllib.parse.quote(followup_message, safe='')
            whatsapp_link = f"https://web.whatsapp.com/send?phone={phone}&text={encoded_message}"
            
            print(f"\n🔗 WhatsApp Link: {whatsapp_link}")
            print("\n📝 Follow-up Message Preview:")
            print("-" * 60)
            print(followup_message[:300] + "..." if len(followup_message) > 300 else followup_message)
            print("-" * 60)
            
            self.log_questions_sent(candidate_data, questions, "Manual", "Success", whatsapp_link)
            return True, whatsapp_link
        
        return False, "Unknown method"

    def send_questions_to_all_contacted(self, domain_filter=None, method='auto'):
        """Send follow-up questions to all contacted candidates"""
        df = self.load_contacted_candidates()
        
        if df.empty:
            return
        
        if domain_filter:
            df = df[df['domain'].str.contains(domain_filter, case=False, na=False)]
            print(f"🎯 Filtered to {len(df)} candidates in {domain_filter} domain")
        
        df = df[
            (df['domain'] != 'Unknown') & 
            (df['domain'] != 'File Not Found') & 
            (df['domain'] != 'Text Extraction Failed')
        ]
        
        print(f"📋 Processing {len(df)} qualified candidates for follow-up questions")
        
        questions_sent_count = 0
        failed_count = 0
        skipped_count = 0
        
        for index, row in df.iterrows():
            candidate_data = row.to_dict()
            
            print(f"\n{'='*70}")
            print(f"📋 Candidate {index + 1}/{len(df)}")
            
            success, result = self.send_followup_questions(candidate_data, method=method)
            
            if success:
                if result == "Questions already sent":
                    skipped_count += 1
                else:
                    questions_sent_count += 1
                    if method == 'auto':
                        time.sleep(3)
            else:
                failed_count += 1
        
        print(f"\n🎉 Follow-up questions session complete!")
        print(f"✅ Questions sent: {questions_sent_count}")
        print(f"⏭️ Already sent (skipped): {skipped_count}")
        print(f"❌ Failed: {failed_count}")
        print(f"📊 Total processed: {len(df)}")
        
        self.create_response_tracker()

    def create_response_tracker(self):
        """Create a template for tracking candidate responses"""
        if not os.path.exists(self.questions_log_csv):
            print("❌ No questions log found. Send questions first.")
            return
        
        questions_df = pd.read_csv(self.questions_log_csv)
        successful_questions = questions_df[questions_df['status'] == 'Success'].copy()
        
        if successful_questions.empty:
            print("❌ No successful question sends found")
            return
        
        existing_responses = pd.DataFrame()
        if os.path.exists(self.responses_csv):
            existing_responses = pd.read_csv(self.responses_csv)
        
        response_data = []
        for _, row in successful_questions.iterrows():
            if not existing_responses.empty and row['email'] in existing_responses['email'].values:
                continue
                
            response_entry = {
                'name': row['name'],
                'email': row['email'],
                'domain': row['domain'],
                'phone': row['phone'],
                'questions_sent_date': row['timestamp'],
                'response_received': 'No',
                'response_date': '',
                'response_quality': '',
                'technical_score': '',
                'notes': '',
                'next_step': ''
            }
            response_data.append(response_entry)
        
        if response_data:
            new_responses_df = pd.DataFrame(response_data)
            
            if not existing_responses.empty:
                combined_df = pd.concat([existing_responses, new_responses_df], ignore_index=True)
            else:
                combined_df = new_responses_df
            
            combined_df.to_csv(self.responses_csv, index=False)
            print(f"📋 Updated response tracker: {self.responses_csv}")
            print(f"👥 Added {len(response_data)} new candidates to track")
        else:
            print("✅ All candidates already in response tracker")

    def show_questions_stats(self):
        """Show interview questions statistics"""
        if not os.path.exists(self.questions_log_csv):
            print("📊 No interview questions log found yet.")
            return
        
        df = pd.read_csv(self.questions_log_csv)
        
        print("\n📈 Interview Questions Statistics:")
        print("="*50)
        print(f"Total follow-up attempts: {len(df)}")
        print(f"Successfully sent: {len(df[df['status'] == 'Success'])}")
        print(f"Failed attempts: {len(df[df['status'] != 'Success'])}")
        
        success_rate = (len(df[df['status'] == 'Success']) / len(df)) * 100 if len(df) > 0 else 0
        print(f"Success rate: {success_rate:.1f}%")
        
        print("\n🎯 Questions Sent by Domain:")