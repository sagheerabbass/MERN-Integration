import streamlit as st
import os
import json
import time
import pandas as pd
import importlib.util
from datetime import datetime

st.set_page_config(
    page_title="Automatic Recruitment System",
    page_icon="👤",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .step-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .success-card {
        background: linear-gradient(135deg, #56ab2f 0%, #a8e6cf 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    .error-card {
        background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    .info-card {
        background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    .metric-container {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

class StreamlitRecruitmentSystem:
    def __init__(self):
        self.config_file = "data/recruitment_config.json"
        self.log_file = "data/master_system_log.txt"
        
        self.create_folder_structure()
        
        self.config = {
            "admin_email": "admin-email",
            "sender_email": "sender-email",
            "sender_password": "your-app-password",
            "whatsapp_group_link": "https://chat.whatsapp.com/Invite-code",
            "auto_approve_shortlist": True,
            "auto_send_rejections": True,
            "last_run": "",
            "steps_enabled": {
                "gmail_scan": True,
                "domain_detection": True,
                "whatsapp_contact": True,
                "interview_questions": True,
                "shortlist_invites": True,
                "admin_notifications": True
            }
        }
        
        self.required_files = [
            "gmail_cv_scanner.py",
            "cv_domain_detector.py",
            "whatsapp_contact_system.py",
            "interview_questions_generator.py",
            "shortlist_group_invite.py",
            "admin_notification_system.py"
        ]
        
        self.load_config()
    
    def create_folder_structure(self):
        """Create organized folder structure"""
        folders = ["data", "downloaded_cvs"]
        for folder in folders:
            if not os.path.exists(folder):
                os.makedirs(folder)
                print(f"Created folder: {folder}")
    
    def load_config(self):
        """Load configuration from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    saved_config = json.load(f)
                    self.config.update(saved_config)
            except Exception as e:
                st.error(f"Error loading config: {e}")
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, "w") as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            st.error(f"Error saving config: {e}")
    
    def check_dependencies(self):
        """Check if all required files and dependencies exist"""
        missing_files = []
        for file in self.required_files:
            if not os.path.exists(file):
                missing_files.append(file)
        
        missing_packages = []
        required_packages = [
            ("pandas", "pandas"),
            ("requests", "requests"),
            ("pdfplumber", "pdfplumber"),
            ("docx", "python-docx"),
            ("google.auth", "google-auth"),
            ("google_auth_oauthlib", "google-auth-oauthlib"),
            ("googleapiclient", "google-api-python-client")
        ]
        
        for import_name, package_name in required_packages:
            try:
                __import__(import_name)
            except ImportError:
                missing_packages.append(package_name)
        
        credentials_missing = not os.path.exists("credentials.json")
        
        return missing_files, missing_packages, credentials_missing
    
    def run_step(self, step_name, script_file, description, progress_bar, status_text):
        """Run a single workflow step"""
        if not self.config["steps_enabled"].get(step_name, True):
            status_text.text(f"⏭️ Skipping {description} (disabled)")
            return True, f"Skipped {description}"
        
        status_text.text(f"🚀 Running: {description}")
        
        if not os.path.exists(script_file):
            return False, f"Script file not found: {script_file}"
        
        try:
            spec = importlib.util.spec_from_file_location(step_name, script_file)
            if spec is None:
                return False, f"Could not load spec for {script_file}"
            
            module = importlib.util.module_from_spec(spec)
            if module is None:
                return False, f"Could not create module from {script_file}"
            
            spec.loader.exec_module(module)
            
            if step_name == "gmail_scan":
                scanner = module.GmailCVScanner()
                result = scanner.scan_and_process_cvs()
                
            elif step_name == "domain_detection":
                detector = module.CVDomainDetector()
                result = detector.process_cvs_with_domain_detection()
                
            elif step_name == "whatsapp_contact":
                whatsapp = module.WhatsAppContactSystem()
                result = whatsapp.contact_all_candidates(method='auto')
                
            elif step_name == "interview_questions":
                questions = module.InterviewQuestionsGenerator()
                result = questions.send_questions_to_all_contacted(method='auto')
                
            elif step_name == "shortlist_invites":
                shortlist = module.ShortlistGroupInvite()
                if self.config["whatsapp_group_link"]:
                    shortlist.set_group_link(self.config["whatsapp_group_link"])
                
                result = shortlist.process_all_shortlisted(
                    send_rejections=self.config["auto_send_rejections"],
                    method='auto'
                )
                
            elif step_name == "admin_notifications":
                admin = module.AdminNotificationSystem()
                admin.sender_email = self.config["sender_email"]
                admin.sender_password = self.config["sender_password"]
                admin.admin_email = self.config["admin_email"]
                
                admin.notify_shortlisted_candidates()
                admin.notify_rejected_candidates()
                
                result = True
            
            status_text.text(f"✅ Completed: {description}")
            return True, f"Successfully completed {description}"
            
        except Exception as e:
            return False, f"Error in {description}: {str(e)}"
    
    def get_system_stats(self):
        """Get current system statistics"""
        stats = {
            "total_candidates": 0,
            "cvs_downloaded": 0,
            "domains_detected": 0,
            "contacts_made": 0,
            "questions_sent": 0,
            "shortlisted": 0,
            "rejected": 0,
            "admin_notifications": 0
        }
        
        try:
            if os.path.exists("data/cv_applications.csv"):
                df = pd.read_csv("data/cv_applications.csv")
                stats["total_candidates"] = len(df)
            
            if os.path.exists("downloaded_cvs"):
                stats["cvs_downloaded"] = len([f for f in os.listdir("downloaded_cvs") 
                                             if f.endswith(('.pdf', '.docx', '.doc'))])
            
            if os.path.exists("data/cv_with_domains.csv"):
                df = pd.read_csv("data/cv_with_domains.csv")
                stats["domains_detected"] = len(df[df['domain'].notna() & (df['domain'] != 'Unknown')])
            
            if os.path.exists("data/whatsapp_contact_log.csv"):
                df = pd.read_csv("data/whatsapp_contact_log.csv")
                stats["contacts_made"] = len(df[df['message_sent'] == 'Yes'])
            
            if os.path.exists("data/interview_questions_log.csv"):
                df = pd.read_csv("data/interview_questions_log.csv")
                stats["questions_sent"] = len(df[df['status'] == 'Success'])
            
            if os.path.exists("data/shortlist_invites_log.csv"):
                df = pd.read_csv("data/shortlist_invites_log.csv")
                stats["shortlisted"] = len(df[(df['action_type'] == 'shortlist') & (df['status'] == 'Success')])
                stats["rejected"] = len(df[(df['action_type'] == 'rejection') & (df['status'] == 'Success')])
            
            if os.path.exists("data/admin_notifications_log.csv"):
                df = pd.read_csv("data/admin_notifications_log.csv")
                stats["admin_notifications"] = len(df[df['status'] == 'Success'])
                
        except Exception as e:
            st.error(f"Error getting stats: {e}")
        
        return stats

def main():
    if 'recruitment_system' not in st.session_state:
        st.session_state.recruitment_system = StreamlitRecruitmentSystem()
    
    system = st.session_state.recruitment_system
    
    st.markdown('<h1 class="main-header">👤 Automatic Recruitment System</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    with st.sidebar:
        
        st.markdown("### 🔄 Workflow Steps")
        for step, enabled in system.config["steps_enabled"].items():
            new_enabled = st.checkbox(step.replace("_", " ").title(), value=enabled, key=f"step_{step}")
            system.config["steps_enabled"][step] = new_enabled
    
    tab1, tab2, tab3, tab4 = st.tabs(["🏠 Dashboard", "🚀 Run Workflow", "📊 Statistics", "🗂️ Data View"])
    
    with tab1:
        st.markdown("## 📊 Dashboard Overview")
        
        stats = system.get_system_stats()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("👥 Total Candidates", stats["total_candidates"])
            st.metric("📄 CVs Downloaded", stats["cvs_downloaded"])
        
        with col2:
            st.metric("🎯 Domains Detected", stats["domains_detected"])
            st.metric("📱 Contacts Made", stats["contacts_made"])
        
        with col3:
            st.metric("❓ Questions Sent", stats["questions_sent"])
            st.metric("✅ Shortlisted", stats["shortlisted"])
        
        with col4:
            st.metric("❌ Rejected", stats["rejected"])
            st.metric("📧 Admin Alerts", stats["admin_notifications"])
        
        st.markdown("## 📁 File Organization")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📄 Downloaded CVs")
            if os.path.exists("downloaded_cvs"):
                cv_files = [f for f in os.listdir("downloaded_cvs") if f.endswith(('.pdf', '.docx', '.doc'))]
                st.write(f"**Location:** `downloaded_cvs/`")
                st.write(f"**Count:** {len(cv_files)} files")
                if cv_files:
                    st.write("**Recent files:**")
                    for file in cv_files[-3:]:
                        st.write(f"- {file}")
            else:
                st.info("No CVs downloaded yet")
        
        with col2:
            st.markdown("### 📊 Data Files")
            if os.path.exists("data"):
                data_files = [f for f in os.listdir("data") if f.endswith('.csv')]
                st.write(f"**Location:** `data/`")
                st.write(f"**Count:** {len(data_files)} files")
                if data_files:
                    st.write("**Available files:**")
                    for file in data_files:
                        st.write(f"- {file}")
            else:
                st.info("No data files created yet")
        
        if system.config["last_run"]:
            st.success(f"🕒 Last successful run: {system.config['last_run']}")
    
    with tab2:
        st.markdown("## 🚀 Run Recruitment Workflow")
        
        missing_files, missing_packages, credentials_missing = system.check_dependencies()
        
        if missing_files or missing_packages or credentials_missing:
            st.error("⚠️ System dependencies not satisfied!")
            
            if missing_files:
                st.markdown("### ❌ Missing Files:")
                for file in missing_files:
                    st.write(f"- {file}")
            
            if missing_packages:
                st.markdown("### ❌ Missing Packages:")
                install_cmd = f"pip install {' '.join(missing_packages)}"
                st.code(install_cmd)
                st.write("Run the above command to install missing packages")
            
            if credentials_missing:
                st.markdown("### ❌ Missing Credentials:")
                st.write("- credentials.json (Download from Google Cloud Console)")
        
        else:
            st.success("✅ All dependencies satisfied!")
            
            st.markdown("### 🚀 Workflow Execution")
            col1, col2 = st.columns([3, 1])
            
            with col2:
                if st.button("🚀 Run Complete Workflow", type="primary", use_container_width=True):
                    st.session_state.run_workflow = True
            
            with col1:
                if st.button("🧪 Test Individual Steps", use_container_width=True):
                    st.session_state.show_individual_steps = True
            
            if st.session_state.get('show_individual_steps', False):
                st.markdown("### 🧪 Test Individual Steps")
                
                workflow_steps = [
                    ("gmail_scan", "gmail_cv_scanner.py", "Gmail CV Scanning"),
                    ("domain_detection", "cv_domain_detector.py", "Domain Detection"),
                    ("whatsapp_contact", "whatsapp_contact_system.py", "WhatsApp Contact"),
                    ("interview_questions", "interview_questions_generator.py", "Interview Questions"),
                    ("shortlist_invites", "shortlist_group_invite.py", "Shortlist Invites"),
                    ("admin_notifications", "admin_notification_system.py", "Admin Notifications")
                ]
                
                for step_name, script_file, description in workflow_steps:
                    if st.button(f"▶️ Run {description}", key=f"individual_{step_name}"):
                        with st.spinner(f"Running {description}..."):
                            progress_bar = st.progress(0)
                            status_text = st.empty()
                            
                            success, message = system.run_step(step_name, script_file, description, progress_bar, status_text)
                            
                            if success:
                                st.success(f"✅ {message}")
                            else:
                                st.error(f"❌ {message}")
            
            if st.session_state.get('run_workflow', False):
                st.markdown("### 🚀 Running Complete Workflow")
                
                workflow_steps = [
                    ("gmail_scan", "gmail_cv_scanner.py", "Gmail CV Scanning"),
                    ("domain_detection", "cv_domain_detector.py", "Domain Detection & CV Analysis"),
                    ("whatsapp_contact", "whatsapp_contact_system.py", "WhatsApp Initial Contact"),
                    ("interview_questions", "interview_questions_generator.py", "Interview Questions"),
                    ("shortlist_invites", "shortlist_group_invite.py", "Shortlist Group Invites"),
                    ("admin_notifications", "admin_notification_system.py", "Admin Notifications")
                ]
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                results_container = st.container()
                
                successful_steps = 0
                total_steps = len(workflow_steps)
                
                for i, (step_name, script_file, description) in enumerate(workflow_steps):
                    progress_bar.progress((i) / total_steps)
                    
                    with results_container:
                        st.markdown(f"#### Step {i+1}/{total_steps}: {description}")
                    
                    success, message = system.run_step(step_name, script_file, description, progress_bar, status_text)
                    
                    with results_container:
                        if success:
                            st.success(f"✅ {message}")
                            successful_steps += 1
                        else:
                            st.error(f"❌ {message}")
                    
                    time.sleep(1)
                
                progress_bar.progress(1.0)
                status_text.text("🎉 Workflow completed!")
                
                system.config["last_run"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                system.save_config()
                
                if successful_steps == total_steps:
                    st.balloons()
                    st.success(f"🎉 All {total_steps} steps completed successfully!")
                else:
                    st.warning(f"⚠️ {successful_steps}/{total_steps} steps completed successfully")
                
                st.session_state.run_workflow = False
    
    with tab3:
        st.markdown("## 📊 Detailed Statistics")
        
        csv_files = {
            "CV Applications": "data/cv_applications.csv",
            "Domain Detection": "data/cv_with_domains.csv", 
            "WhatsApp Contacts": "data/whatsapp_contact_log.csv",
            "Interview Questions": "data/interview_questions_log.csv",
            "Candidate Responses": "data/candidate_responses.csv",
            "Shortlist Invites": "data/shortlist_invites_log.csv",
            "Admin Notifications": "data/admin_notifications_log.csv"
        }
        
        for name, filename in csv_files.items():
            if os.path.exists(filename):
                try:
                    df = pd.read_csv(filename)
                    
                    with st.expander(f"📋 {name} ({len(df)} records)"):
                        st.write(f"**Total Records:** {len(df)}")
                        
                        if 'domain' in df.columns:
                            domain_counts = df['domain'].value_counts()
                            st.write("**Domain Distribution:**")
                            for domain, count in domain_counts.items():
                                st.write(f"- {domain}: {count}")
                        
                        if 'status' in df.columns:
                            status_counts = df['status'].value_counts()
                            st.write("**Status Distribution:**")
                            for status, count in status_counts.items():
                                st.write(f"- {status}: {count}")
                        
                        st.write("**Recent Records:**")
                        st.dataframe(df.tail(5))
                        
                except Exception as e:
                    st.error(f"Error loading {name}: {e}")
            else:
                st.info(f"📄 {name}: No data yet")
    
    with tab4:
        st.markdown("## 🗂️ Data Files View & Management")
        
        available_files = []
        data_folder = "data"
        if os.path.exists(data_folder):
            for filename in os.listdir(data_folder):
                if filename.endswith('.csv'):
                    available_files.append(os.path.join(data_folder, filename))
        
        if available_files:
            selected_file = st.selectbox("Select file to view/edit:", available_files)
            
            if selected_file:
                try:
                    df = pd.read_csv(selected_file)
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("📄 File", os.path.basename(selected_file))
                    with col2:
                        st.metric("📊 Records", len(df))
                    with col3:
                        st.metric("🏷️ Columns", len(df.columns))
                    
                    st.write(f"**Columns:** {', '.join(df.columns)}")
                    
                    file_tab1, file_tab2, file_tab3 = st.tabs(["👀 View Data", "✏️ Edit Records", "➕ Add New Record"])
                    
                    with file_tab1:
                        search_term = st.text_input("🔍 Search in data:", key=f"search_{selected_file}")
                        if search_term:
                            mask = df.astype(str).apply(lambda x: x.str.contains(search_term, case=False, na=False)).any(axis=1)
                            filtered_df = df[mask]
                            st.write(f"Found {len(filtered_df)} matching records")
                            st.dataframe(filtered_df)
                        else:
                            st.dataframe(df)
                        
                        csv_data = df.to_csv(index=False)
                        st.download_button(
                            label="📥 Download CSV",
                            data=csv_data,
                            file_name=os.path.basename(selected_file),
                            mime="text/csv"
                        )
                    
                    with file_tab2:
                        st.markdown("### ✏️ Edit Existing Records")
                        
                        if not df.empty:
                            edit_search_term = st.text_input("🔍 Search record to edit:", key=f"edit_search_{selected_file}")
                            
                            if edit_search_term:
                                edit_mask = df.astype(str).apply(
                                    lambda x: x.str.contains(edit_search_term, case=False, na=False)
                                ).any(axis=1)
                                edit_filtered_df = df[edit_mask]
                            else:
                                edit_filtered_df = df
                            
                            if not edit_filtered_df.empty:
                                record_options = []
                                record_indices = []
                                for idx, row in edit_filtered_df.iterrows():
                                    display_parts = []
                                    if 'name' in row:
                                        display_parts.append(f"Name: {row['name']}")
                                    if 'email' in row:
                                        display_parts.append(f"Email: {row['email']}")
                                    if 'domain' in row:
                                        display_parts.append(f"Domain: {row['domain']}")
                                    if 'timestamp' in row:
                                        display_parts.append(f"Date: {str(row['timestamp'])[:10]}")
                                    
                                    display_string = " | ".join(display_parts) if display_parts else f"Record {idx}"
                                    record_options.append(display_string)
                                    record_indices.append(idx)
                                
                                selected_record_display = st.selectbox("Select record to edit:", record_options, key=f"record_select_{selected_file}")
                                
                                if selected_record_display:
                                    selected_idx = record_options.index(selected_record_display)
                                    original_idx = record_indices[selected_idx]
                                    record_row = df.loc[original_idx]
                                    
                                    st.markdown("### Edit Record Data")
                                    st.info(f"Editing record {original_idx}")
                                    
                                    edit_data = {}
                                    
                                    columns = list(df.columns)
                                    mid_point = len(columns) // 2
                                    
                                    col1, col2 = st.columns(2)
                                    
                                    with col1:
                                        for col in columns[:mid_point]:
                                            current_value = str(record_row[col]) if pd.notna(record_row[col]) else ""
                                            edit_data[col] = st.text_input(f"{col}:", value=current_value, key=f"edit_{col}_{original_idx}")
                                    
                                    with col2:
                                        for col in columns[mid_point:]:
                                            current_value = str(record_row[col]) if pd.notna(record_row[col]) else ""
                                            edit_data[col] = st.text_input(f"{col}:", value=current_value, key=f"edit_{col}_{original_idx}")
                                    
                                    col_save, col_cancel = st.columns(2)
                                    
                                    with col_save:
                                        if st.button("💾 Update Record", type="primary", key=f"save_edit_{original_idx}"):
                                            try:
                                                for col, value in edit_data.items():
                                                    df.at[original_idx, col] = value
                                                
                                                if 'timestamp' in df.columns:
                                                    df.at[original_idx, 'timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                                
                                                df.to_csv(selected_file, index=False)
                                                st.success(f"✅ Record {original_idx} updated successfully!")
                                                st.rerun()
                                                
                                            except Exception as e:
                                                st.error(f"Error updating record: {e}")
                                    
                                    with col_cancel:
                                        if st.button("❌ Cancel", key=f"cancel_edit_{original_idx}"):
                                            st.rerun()
                                
                            else:
                                st.info("No records found matching your search")
                        else:
                            st.info("No records in this file")
                    
                    with file_tab3:
                        st.markdown("### ➕ Add New Record")
                        
                        new_data = {}
                        
                        columns = list(df.columns)
                        mid_point = len(columns) // 2
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            for col in columns[:mid_point]:
                                if col.lower() in ['timestamp', 'date']:
                                    new_data[col] = st.text_input(f"{col}:", value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"), key=f"new_{col}")
                                else:
                                    new_data[col] = st.text_input(f"{col}:", key=f"new_{col}")
                        
                        with col2:
                            for col in columns[mid_point:]:
                                if col.lower() in ['timestamp', 'date']:
                                    new_data[col] = st.text_input(f"{col}:", value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"), key=f"new_{col}")
                                else:
                                    new_data[col] = st.text_input(f"{col}:", key=f"new_{col}")
                        
                        if st.button("➕ Add New Record", type="primary", key=f"add_new_{selected_file}"):
                            try:
                                new_df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
                                new_df.to_csv(selected_file, index=False)
                                st.success(f"✅ New record added to {os.path.basename(selected_file)}!")
                                st.rerun()
                                
                            except Exception as e:
                                st.error(f"Error adding record: {e}")
                    
                except Exception as e:
                    st.error(f"Error loading file: {e}")
        else:
            st.info("No data files found yet. Run the workflow to generate data.")

if __name__ == "__main__":
    main()