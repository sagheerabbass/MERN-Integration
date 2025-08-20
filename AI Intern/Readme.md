### 🔧 Setup Instructions (Essential Configuration)

1. **Add your `credentials.json` file**  
   - Download it from the [Google Cloud Console](https://console.cloud.google.com/) after enabling the Gmail API.
   - Place the `credentials.json` file in the root directory of your project.

2. **Run the Gmail scanner to authenticate**  
   Run the following script to verify your Google account and generate the token:

   ```bash
   python gmail_cv_scanner.py

This will open a browser window for authentication and create a token.pickle file in your directory for future access.

3. **Update email and WhatsApp configurations in** `app.py`
Open the app.py file and set the following variables with your actual information:
admin_email = "your-admin-email@example.com"
sender_email = "your-sender-email@gmail.com"
sender_app_password = "your-sender-app-password"  # Use Gmail App Password, NOT your Gmail password

whatsapp_group_link = "https://chat.whatsapp.com/your-group-invite-code"
