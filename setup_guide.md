# 📘 Gmail Triage Agent — Setup Guide
# Follow these steps ONE TIME on your laptop. After that, just run main.py!

==========================================================
STEP 1 — Install Python
==========================================================

1. Go to: https://www.python.org/downloads/
2. Click "Download Python" (get the latest version)
3. Run the installer
   ⚠️ IMPORTANT: Check the box that says "Add Python to PATH"
4. Open Terminal (Mac) or Command Prompt (Windows)
5. Type: python --version
   You should see something like: Python 3.12.0 ✅


==========================================================
STEP 2 — Set Up Gmail API (Google Cloud)
==========================================================

1. Go to: https://console.cloud.google.com/
2. Sign in with your Google account
3. Click "Select a project" at the top → "New Project"
4. Name it: GmailAgent → Click "Create"
5. In the search bar, search: Gmail API → Click it → Click "Enable"
6. Go to: APIs & Services → OAuth consent screen
   - Choose "External" → Click Create
   - App name: Gmail Triage Agent
   - Your email in the support email field
   - Click Save and Continue (skip through the rest)
7. Go to: APIs & Services → Credentials
   - Click "+ Create Credentials" → "OAuth Client ID"
   - Application type: Desktop App
   - Name: GmailAgent
   - Click Create
8. Click the Download button (⬇️) next to your new credential
9. Rename the downloaded file to: credentials.json
10. Move credentials.json into the same folder as main.py


==========================================================
STEP 3 — Get Your Anthropic API Key
==========================================================

1. Go to: https://console.anthropic.com/
2. Sign up for a free account
3. Go to: API Keys (left sidebar)
4. Click "+ Create Key"
5. Name it: GmailAgent
6. Copy the key (it starts with sk-ant-...)
   ⚠️ Save it somewhere safe — you won't see it again!


==========================================================
STEP 4 — Edit main.py With Your Details
==========================================================

Open main.py in any text editor (Notepad, VS Code, etc.)
Find these two lines near the top and update them:

  YOUR_EMAIL = "your_email@gmail.com"      ← your Gmail address
  ANTHROPIC_API_KEY = "your_anthropic_key" ← your key from Step 3

Save the file.


==========================================================
STEP 5 — Install Required Libraries
==========================================================

1. Open Terminal / Command Prompt
2. Navigate to your project folder:
   cd path/to/your/gmail_agent/folder
3. Run:
   pip install -r requirements.txt
4. Wait for everything to install ✅


==========================================================
STEP 6 — Run the Agent for the First Time
==========================================================

1. In Terminal, run:
   python main.py

2. A browser window will open automatically
   → Log in with your Gmail account
   → Click "Allow" to give the app access
   → The window will close automatically

3. The agent will:
   ✅ Fetch your unread emails
   ✅ Classify them with Claude AI
   ✅ Print the summary in the terminal
   ✅ Email the summary to yourself
   ✅ Schedule itself to repeat every 6 hours


==========================================================
STEP 7 — Keep It Running
==========================================================

OPTION A — Run on your laptop (simple):
  Just keep the terminal window open.
  The agent runs every 6 hours automatically.
  Press Ctrl+C to stop.

OPTION B — Run 24/7 for free (recommended):
  Deploy to Railway.app (free tier):
  1. Go to: https://railway.app/
  2. Sign up with GitHub
  3. Upload your project files
  4. It runs 24/7 without your laptop!


==========================================================
YOUR PROJECT FILES
==========================================================

gmail_agent/
├── main.py            ← The agent code
├── requirements.txt   ← Libraries to install
├── credentials.json   ← Download from Google Cloud (Step 2)
├── setup_guide.md     ← This file
└── token.json         ← Created automatically on first run


==========================================================
TROUBLESHOOTING
==========================================================

❌ "credentials.json not found"
   → Make sure credentials.json is in the same folder as main.py

❌ "Invalid API Key"
   → Double-check your Anthropic API key in main.py

❌ Browser doesn't open for Gmail login
   → Run: python main.py and wait a few seconds
   → Or delete token.json and try again

❌ "Module not found" error
   → Run: pip install -r requirements.txt again

Need help? Paste the error message into Claude and ask for help!


==========================================================
WHAT HAPPENS EACH RUN
==========================================================

🚀 Agent starts
  ↓
📬 Fetches your unread emails (up to 20)
  ↓
🤖 Sends each email to Claude AI for classification
  ↓
📊 Builds a summary report:
     🔴 IMPORTANT — needs your attention
     🟡 RELEVANT  — good to know
     🟢 LOW PRIORITY — can ignore
  ↓
📧 Emails the summary to yourself
  ↓
⏰ Waits 6 hours → repeats automatically
