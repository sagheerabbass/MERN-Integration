from flask import Flask, request, jsonify
import os
# Import your workflow classes
from gmail_cv_scanner import GmailCVScanner
from cv_domain_detector import CVDomainDetector
from whatsapp_contact_system import WhatsAppContactSystem
from interview_questions_generator import InterviewQuestionsGenerator
from admin_notification_system import AdminNotificationSystem
from shortlist_group_invite import ShortlistGroupInvite

app = Flask(__name__)

# Instantiate objects once
gmail_scanner = GmailCVScanner()
domain_detector = CVDomainDetector()
whatsapp_system = WhatsAppContactSystem()
interview_generator = InterviewQuestionsGenerator()
admin_notifier = AdminNotificationSystem()
shortlist_inviter = ShortlistGroupInvite()

# -------------------------------
# Endpoint 1: Full Workflow
# -------------------------------
@app.route("/run-workflow", methods=["POST"])
def run_workflow():
    try:
        # Step 1: Gmail scanning (process inbox)
        processed_count = gmail_scanner.scan_and_process_cvs()

        # For simplicity, get last processed candidate from CSV
        latest_candidate = None
        if os.path.exists(gmail_scanner.csv_file):
            import pandas as pd
            df = pd.read_csv(gmail_scanner.csv_file)
            if not df.empty:
                latest_candidate = df.iloc[-1].to_dict()

        if not latest_candidate:
            return jsonify({"error": "No new candidate found"}), 400

        email = latest_candidate.get("email")
        name = latest_candidate.get("name")

        # Step 2: Domain detection
        domain,cv_text_preview = domain_detector.process_cvs_with_domain_detection()

        # Step 3: WhatsApp auto-contact
        success, whatsapp_result = whatsapp_system.contact_candidate(
            {"name": name, "email": email, "domain": domain,"cv_text_preview":cv_text_preview},
            method="auto"
        )

        # Step 4: Interview questions
        interview_questions = interview_generator.send_questions_to_all_contacted()

        # Step 5: Admin notification
        #admin_notice = admin_notifier.send_simple_notification()

        candidate_data = {
            "name": name,
            "email": email,
            "domain": domain,
            "interview_answers": interview_questions,
            "status": "New"
        }

        return jsonify({
            "success": True,
            "candidate": candidate_data,
            "whatsapp_result": whatsapp_result,
            #"admin_notice": admin_notice
        })

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500



# -------------------------------
# Endpoint 2: WhatsApp Shortlist Invite
# -------------------------------
@app.route("/send-invite", methods=["POST"])
def send_invite():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "Invalid payload"}), 400

        candidate_data = {
            "name": data.get("name", "Candidate"),
            "email": data.get("email", ""),
            "domain": data.get("domain", ""),
            "cv_text_preview": data.get("cv_text_preview", "")
        }

        # Step: Shortlist Group Invite
        shortlist_inviter.process_all_shortlisted()

        return jsonify({
            
            "candidate": candidate_data
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
