🎤 VAANI - Voice-Powered Website Builder
AI for Good | Empowering everyone to build their online presence through the power of voice

Unsupported image
 
Unsupported image
 
Unsupported image
 
Unsupported image

🌟 Vision
VAANI (Voice-Activated Automated Natural Interface) breaks down barriers to website creation by enabling anyone—regardless of technical skills or physical abilities—to build and manage their online presence using just their voice.

AI for Good Impact
🌍 Accessibility First: Empowers people with disabilities to create websites independently
💡 Digital Inclusion: Reduces technical barriers for non-tech-savvy users
🚀 Economic Empowerment: Enables small businesses and entrepreneurs in developing regions to establish online presence
🗣️ Language Democratization: Voice commands work in natural language, reducing literacy barriers
✨ Features
Voice-Powered CMS
🎙️ Real-time Voice Commands: Speak naturally to update your website
🤖 AI Intent Recognition: Google Gemini understands what you want to change
📝 Instant Updates: Changes reflect immediately on your public website
User-Friendly Dashboard
🎬 YouTube Studio Style: Familiar, intuitive interface
📊 Analytics at a Glance: Track visitor views in real-time
🎨 Beautiful Design: Modern dark mode with professional aesthetics
Public Website Hosting
🌐 Instant Publishing: Each user gets a public URL at /public/<username>
📱 Responsive Design: Looks great on all devices
🔒 Secure & Private: User authentication protects your dashboard
🏗️ Architecture
Tech Stack
Backend: Flask (Python)
Database: SQLite with comprehensive CRUD operations
AI Services:
Hugging Face Whisper API (Speech-to-Text)
Google Gemini API (Intent Extraction)
Authentication: Session-based with password hashing
Frontend: HTML5, CSS3, Tailwind CSS
System Flow
User Voice Command → Whisper (Transcription) → Gemini (Intent) → Database Update → Public Website

🚀 Quick Start
Prerequisites
Python 3.8+
Hugging Face Account (free)
Google AI Studio Account (free)
Installation
Clone the repository
git clone <your-repo-url>
cd vaani

Install dependencies
pip install -r requirements.txt

Set up API Keys Add these secrets in Replit or create a .env file:
HF_TOKEN=your_huggingface_token
GEMINI_API_KEY=your_gemini_api_key
FLASK_SECRET_KEY=your_random_secret_key

Get your API keys:

Hugging Face: https://huggingface.co/settings/tokens
Google Gemini: https://makersuite.google.com/app/apikey
Run the application
python app.py

Access the app Open your browser to http://localhost:5000
🎯 Usage
For Users
Register an Account

Visit the homepage and click "Get Started"
Create your username and password
Access Your Dashboard

Log in to see your YouTube Studio-style control panel
View your website statistics and current content
Update via Voice

Click the microphone button
Speak naturally: "Change shop name to Fresh Bakery"
Watch your website update instantly!
Share Your Website

Your public URL: yourdomain.com/public/<username>
Share it with the world!
Voice Command Examples
"Change my shop name to Tech Solutions"
"Update description to We provide innovative software solutions"
"Set announcement to Grand opening sale - 50% off!"

📂 Project Structure
vaani/
├── app.py                      # Main Flask application
├── database.py                 # Database layer with CRUD operations
├── api_helper.py               # AI integration (Whisper + Gemini)
├── requirements.txt            # Python dependencies
├── templates/
│   ├── index.html              # Marketing landing page
│   ├── login.html              # User login
│   ├── register.html           # User registration
│   ├── dashboard.html          # Voice-powered control panel
│   ├── public_template.html    # User's public website
│   └── 404.html                # Error page
├── static/
│   └── style.css               # Custom styling
└── vaani.db                    # SQLite database (auto-created)

🔌 API Endpoints
Public Routes
GET / - Marketing homepage
POST /register - Create new user account
POST /login - Authenticate user
GET /logout - End session
GET /public/<username> - View user's public website
Protected Routes (Authentication Required)
GET /dashboard - User control panel
POST /process-audio - Process voice commands
POST /save-data - Update website content
🛠️ Development
Database Schema
Users Table

id          INTEGER PRIMARY KEY
username    TEXT UNIQUE NOT NULL
password    TEXT NOT NULL (hashed)

Websites Table

id              INTEGER PRIMARY KEY
user_id         INTEGER FOREIGN KEY
shop_name       TEXT
description     TEXT
announcement    TEXT
image_url       TEXT
views           INTEGER DEFAULT 0

Adding New Features
The codebase is modular and easy to extend:

Add new voice commands in api_helper.py
Extend database schema in database.py
Create new routes in app.py
Add templates in templates/
🌈 Roadmap
 Multi-language voice support
 Custom themes for public websites
 Advanced analytics dashboard
 Image upload via voice description
 Mobile app (iOS/Android)
 Voice-to-website for e-commerce features
 Team collaboration features
🤝 Contributing
We welcome contributions! This project is built for the Vibeathon with an AI for Good mission.

How to Contribute
Fork the repository
Create your feature branch (git checkout -b feature/AmazingFeature)
Commit your changes (git commit -m 'Add some AmazingFeature')
Push to the branch (git push origin feature/AmazingFeature)
Open a Pull Request
📜 License
This project is licensed under the MIT License - see the LICENSE file for details.

🙏 Acknowledgments
Vibeathon Team for organizing this incredible event
Google Gemini for powerful AI capabilities
Hugging Face for speech recognition infrastructure
Open Source Community for amazing tools and libraries
📧 Contact
Built with ❤️ for Vibeathon - AI for Good

🌟 Star this repo if VAANI helped you build something amazing!
