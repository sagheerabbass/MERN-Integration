import os
import csv
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

class AdminNotificationSystem:
    def __init__(self):
        # Input files from previous steps
        self.responses_csv = "data/candidate_responses.csv"
        self.shortlist_log_csv = "data/shortlist_invites_log.csv"
        self.admin_log_csv = "data/admin_notifications_log.csv"
        
        # Email configuration
        self.admin_email = "your-admin-email"
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = ""
        self.sender_password = ""

    def load_all_candidate_data(self):
        """Load and merge all candidate data from different steps"""
        try:
            if not os.path.exists(self.responses_csv):
                print(f"❌ {self.responses_csv} not found")
                return pd.DataFrame()
            
            responses_df = pd.read_csv(self.responses_csv)
            print(f"📊 Loaded {len(responses_df)} candidate responses")
            
            # Load shortlist status
            if os.path.exists(self.shortlist_log_csv):
                shortlist_df = pd.read_csv(self.shortlist_log_csv)
                latest_shortlist = shortlist_df.groupby('email').last().reset_index()
                responses_df = responses_df.merge(
                    latest_shortlist[['email', 'action_type', 'status', 'timestamp']], 
                    on='email', 
                    how='left',
                    suffixes=('', '_shortlist')
                )
                responses_df.rename(columns={
                    'action_type': 'final_action',
                    'status': 'action_status',
                    'timestamp': 'action_date'
                }, inplace=True)
            
            return responses_df
            
        except Exception as error:
            print(f"❌ Error loading candidate data: {error}")
            return pd.DataFrame()

    def send_simple_notification(self, subject, html_content, text_content=None):
        """Send simple email notification to admin"""
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.sender_email
            msg['To'] = self.admin_email
            msg['Subject'] = subject
            
            if not text_content:
                text_content = f"""
CodeCelix Recruitment System Notification

{subject}

Please check the HTML version for detailed information.

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                """
            
            part1 = MIMEText(text_content, 'plain')
            part2 = MIMEText(html_content, 'html')
            
            msg.attach(part1)
            msg.attach(part2)
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                text = msg.as_string()
                server.sendmail(self.sender_email, self.admin_email, text)
            
            print(f"✅ Admin notification sent successfully")
            return True, "Email sent successfully"
            
        except Exception as error:
            print(f"❌ Failed to send admin notification: {error}")
            return False, str(error)

    def log_admin_notification(self, notification_type, status, recipient_count=0, error_msg=None):
        """Log admin notification attempt"""
        log_entry = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'notification_type': notification_type,
            'admin_email': self.admin_email,
            'recipient_count': recipient_count,
            'status': status,
            'error_message': error_msg or ''
        }
        
        file_exists = os.path.isfile(self.admin_log_csv)
        
        with open(self.admin_log_csv, 'a', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['timestamp', 'notification_type', 'admin_email', 
                         'recipient_count', 'status', 'error_message']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            if not file_exists:
                writer.writeheader()
            
            writer.writerow(log_entry)

    def notify_shortlisted_candidates(self):
        """Send simple notification for newly shortlisted candidates"""
        df = self.load_all_candidate_data()
        
        if df.empty:
            print("📧 No candidate data available")
            return
        
        shortlisted = df[
            (df['final_action'] == 'shortlist') & 
            (df['action_status'] == 'Success')
        ].copy()
        
        if not shortlisted.empty:
            subject = f"✅ {len(shortlisted)} Candidates Shortlisted - CodeCelix"
            
            html_content = f"""
            <html>
            <body>
                <div style="padding: 20px;">
                    <h3>🎉 {len(shortlisted)} candidates have been shortlisted!</h3>
                    
                    <div>
                        <strong>Shortlisted Candidates:</strong><br>
            """
            
            for _, candidate in shortlisted.iterrows():
                html_content += f"""
                        <strong>• Name:</strong> {candidate.get('name', 'Unknown')} <br>
                        <strong>• Domain:</strong> {candidate.get('domain', 'Unknown')} <br>
                        <strong>• Email:</strong> {candidate.get('email', 'Unknown')} <br>
                        <strong>• Phone:</strong> {candidate.get('phone', 'Unknown')}<br><br>
                """
            
            html_content += """
                    </div>
                </div>
            </body>
            </html>
            """
            
            text_content = f"""
CodeCelix Shortlist Notification

🎉 {len(shortlisted)} candidates have been shortlisted!

Shortlisted Candidates:
"""
            for _, candidate in shortlisted.iterrows():
                text_content += f"• {candidate.get('name', 'Unknown')} - {candidate.get('domain', 'Unknown')}\n"
            
            text_content += f"""
Total shortlisted: {len(shortlisted)}
These candidates have been invited to the shortlist group automatically.

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
            
            success, message = self.send_simple_notification(subject, html_content, text_content)
            
            status = "Success" if success else "Failed"
            error_msg = None if success else message
            
            self.log_admin_notification("shortlisted", status, len(shortlisted), error_msg)
            
            if success:
                print(f"✅ Shortlist notification sent: {len(shortlisted)} candidates")
            else:
                print(f"❌ Failed to send shortlist notification: {message}")
        else:
            print("📧 No new shortlisted candidates to report")

    def notify_rejected_candidates(self):
        """Send simple notification for rejected candidates"""
        df = self.load_all_candidate_data()
        
        if df.empty:
            print("📧 No candidate data available")
            return
        
        rejected = df[
            (df['final_action'] == 'rejection') & 
            (df['action_status'] == 'Success')
        ].copy()
        
        if not rejected.empty:
            subject = f"❌ {len(rejected)} Candidates Rejected - CodeCelix"
            
            html_content = f"""
            <html>
            <body>
                
                <div style="padding: 20px;">
                    <h3>{len(rejected)} candidates have been rejected</h3>
                    
                    <div>
                        <strong>Rejected Candidates:</strong><br>
            """
            
            for _, candidate in rejected.iterrows():
                html_content += f"""
                        <strong>• Name:</strong> {candidate.get('name', 'Unknown')} <br>
                        <strong>• Domain:</strong> {candidate.get('domain', 'Unknown')} <br>
                        <strong>• Email:</strong> {candidate.get('email', 'Unknown')} <br>
                        <strong>• Phone:</strong> {candidate.get('phone', 'Unknown')}<br><br>
                """
            
            html_content += """
                    </div>
                </div>
            </body>
            </html>
            """
            
            text_content = f"""
CodeCelix Rejection Notification

{len(rejected)} candidates have been rejected

Rejected Candidates:
"""
            for _, candidate in rejected.iterrows():
                text_content += f"• {candidate.get('name', 'Unknown')} - {candidate.get('domain', 'Unknown')}\n"
            
            text_content += f"""
Total rejected: {len(rejected)}
These candidates have been notified of the decision automatically.

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
            
            success, message = self.send_simple_notification(subject, html_content, text_content)
            
            status = "Success" if success else "Failed"
            error_msg = None if success else message
            
            self.log_admin_notification("rejected", status, len(rejected), error_msg)
            
            if success:
                print(f"✅ Rejection notification sent: {len(rejected)} candidates")
            else:
                print(f"❌ Failed to send rejection notification: {message}")
        else:
            print("📧 No new rejected candidates to report")

    def send_test_notification(self):
        """Send a test notification to verify email configuration"""
        print("📧 Sending test notification...")
        
        subject = "🧪 Test Notification - CodeCelix Recruitment System"
        
        html_content = """
        <html>
        <body style="font-family: Arial, sans-serif; margin: 20px;">
            <div style="background-color: #2196F3; color: white; padding: 20px; text-align: center; border-radius: 5px;">
                <h2>🧪 Test Notification</h2>
            </div>
            
            <div style="margin: 20px 0;">
                <p>This is a test notification from the CodeCelix Recruitment System.</p>
                <p>If you received this email, the notification system is working correctly! ✅</p>
            </div>
            
            <div style="text-align: center; color: #666; font-size: 12px; margin-top: 30px;">
                <p>📧 Generated on: {}</p>
            </div>
        </body>
        </html>
        """.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        text_content = f"""
Test Notification - CodeCelix Recruitment System

This is a test notification to verify the email configuration.

If you received this email, the notification system is working correctly!

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        success, message = self.send_simple_notification(subject, html_content, text_content)
        
        if success:
            print("✅ Test notification sent successfully")
        else:
            print(f"❌ Test notification failed: {message}")
        
        return success

    def send_error_alert(self, error_message, component="System"):
        """Send error alert to admin"""
        subject = f"⚠️ System Error Alert - {component}"
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; margin: 20px;">
            <div style="background-color: #dc3545; color: white; padding: 15px; text-align: center; border-radius: 5px;">
                <h2>⚠️ System Error Alert</h2>
            </div>
            
            <div style="padding: 20px; background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 5px; margin: 15px 0;">
                <h3>Error in {component}</h3>
                <div style="color: #721c24; background-color: #f8d7da; padding: 10px; border-radius: 5px;">
                    {error_message}
                </div>
                <p>Please check the system logs and take appropriate action.</p>
            </div>
            
            <div style="text-align: center; color: #666; font-size: 12px; margin-top: 20px;">
                <p>📧 Error alert from CodeCelix System</p>
                <p>🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
CodeCelix System Error Alert

Error in {component}:
{error_message}

Please check the system logs and take appropriate action.

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        success, message = self.send_simple_notification(subject, html_content, text_content)
        self.log_admin_notification("error_alert", "Success" if success else "Failed", 0, message if not success else None)

    def show_notification_stats(self):
        """Show admin notification statistics"""
        if not os.path.exists(self.admin_log_csv):
            print("📊 No admin notifications log found yet.")
            return
        
        df = pd.read_csv(self.admin_log_csv)
        
        print("\n📈 Admin Notification Statistics:")
        print("="*50)
        print(f"Total notifications sent: {len(df[df['status'] == 'Success'])}")
        print(f"Failed notifications: {len(df[df['status'] == 'Failed'])}")
        
        if len(df) > 0:
            success_rate = (len(df[df['status'] == 'Success']) / len(df)) * 100
            print(f"Success rate: {success_rate:.1f}%")
        
        print("\n📧 By Notification Type:")
        type_stats = df[df['status'] == 'Success']['notification_type'].value_counts()
        for ntype, count in type_stats.items():
            print(f"   {ntype.title()}: {count}")
        
        recent_df = df[df['timestamp'] >= (datetime.now() - pd.Timedelta(days=7)).strftime("%Y-%m-%d")]
        print(f"\n📅 Last 7 days: {len(recent_df)} notifications")

if __name__ == "__main__":
    admin_system = AdminNotificationSystem()
    
    print("🚀 Admin Notification System")
    print("Choose an option:")
    print("1. Send shortlisted candidates notification")
    print("2. Send rejected candidates notification")
    print("3. Send test notification")
    print("4. Send error alert (test)")
    print("5. Show notification statistics")
    
    choice = input("\nEnter your choice (1-5): ")
    
    if choice == "1":
        admin_system.notify_shortlisted_candidates()
    elif choice == "2":
        admin_system.notify_rejected_candidates()
    elif choice == "3":
        admin_system.send_test_notification()
    elif choice == "4":
        admin_system.send_error_alert("Test error message", "Test Component")
    elif choice == "5":
        admin_system.show_notification_stats()
    else:
        print("Invalid choice. Exiting...")