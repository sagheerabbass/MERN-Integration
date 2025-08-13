# 🧰 CodeCelix MERN Integration

**CodeCelix MERN Integration** is a full-stack MERN (MongoDB, Express.js, React.js, Node.js) web application integrated with a Python-based automation system to manage candidate onboarding, tracking, and communication.

---

## 📦 Project Structure

MERN-Integration/
├── backend           # Express.js + MongoDB backend
├── frontend          # React.js + Tailwind CSS admin dashboard
└── python-service    # Python automation service

---

## 🧑‍💻 1. Clone and Setup the Project

```bash
git clone https://github.com/sagheerabbass/MERN-Integration.git
cd MERN-Integration
```
## Backend Setup
Navigate to 'cd backend'


## 📥 Install dependencies
npm install express mongoose cors dotenv jsonwebtoken bcryptjs helmet express-rate-limit morgan axios
npm install --save-dev nodemon

## 🔐 Create .env file
            create .env inside backend folder
PORT=5000
MONGO_URI=your_mongodb_atlas_connection
JWT_SECRET=your_strong_secret
PYTHON_SERVICE_URL=http://localhost:8000
```
## Run Backend Server
```
Command to run Backend Server "npx nodemon server.js"

## Frontend Setup
   cd ../frontend

## Install Dependencies
npx create-react-app .
npm install axios react-router-dom
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```
##📚 Configure Tailwind
module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: { extend: {} },
  plugins: [],
}
Add to src/index.css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

## ▶️ Run Frontend
npm start

## Python Service Setup
    Navigate to cd ../python-service
```
##Install Dependencies
python -m venv venv
# Activate venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
pip install flask requests pymupdf python-docx google-api-python-client google-auth google-auth-oauthlib google-auth-httplib2

```
## Run Python
python app.py

```
## MongoDB Atlas Setup
Go to MongoDB Atlas
Create a cluster.
Get your connection string.
Replace it in the .env file under MONGO_URI.

```
## Deployment(Docker)
    docker build -t mern-integration-backend .
    docker run -d -p 5000:5000 --env-file .env mern-integration-backend
```
##Frontend Build
cd frontend
npm run build


🌟 Features Implemented
✅ Admin Login using JWT Authentication
✅ Candidate Management: View, filter, shortlist, reject
✅ Python Automation: WhatsApp message sending & Gmail CV parsing
✅ MongoDB storage instead of Google Sheets/CSV
✅ Secure API with JWT, Helmet, and rate limiting
✅ Tailwind CSS-based responsive admin dashboard
✅ Deployment-ready setup for VPS + cloud hosting

📌 Notes
Ensure backend, frontend, and python-service run simultaneously for full functionality.

Keep .env files private and never push them to GitHub.

When running locally, ensure localhost ports don’t conflict.



