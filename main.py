# ============================================================
# Gmail Triage Agent
# Reads your emails, classifies them with Claude AI,
# and sends you a summary every 6 hours.
# ============================================================

import os
import base64
import json
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import anthropic
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# ============================================================
# CONFIGURATION — Edit these values
# ============================================================

YOUR_EMAIL = "jakkireddykeerthi@gmail.com, g.t.p.sankar@gmail.com"       # Your Gmail address
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")  # From console.anthropic.com
MAX_EMAILS = 20                            # How many emails to fetch each run
SCHEDULE_HOURS = 6                         # Run every 6 hours

# Gmail API scopes
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send"
]
app = Flask(__name__)

@app.route("/")
def health():
    return "✅ Gmail Triage Agent is running!", 200

@app.route("/run")
def manual_run():
    try:
        run_agent()
        return "✅ Triage complete! Check your email.", 200
    except Exception as e:
        return f"❌ Error: {str(e)}", 500

# ============================================================
# STEP 1: Connect to Gmail
# ============================================================

def connect_gmail():
    """Log into Gmail using your credentials.json file."""
    creds = None

    # ✅ Load token from environment variable (for Cloud Run)
    token_env = os.environ.get("GMAIL_TOKEN")
    if token_env and not os.path.exists("token.json"):
        with open("token.json", "w") as f:
            f.write(token_env)

    # Load saved login token if it exists
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # If no valid login, open browser to log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save login token for next time
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    service = build("gmail", "v1", credentials=creds)
    print("✅ Connected to Gmail successfully!")
    return service


# ============================================================
# STEP 2: Fetch Unread Emails
# ============================================================

def fetch_emails(service, max_results=MAX_EMAILS):
    """Fetch unread emails from your inbox."""
    print(f"\n📬 Fetching up to {max_results} unread emails...")

    results = service.users().messages().list(
        userId="me",
        labelIds=["INBOX", "UNREAD"],
        maxResults=max_results
    ).execute()

    messages = results.get("messages", [])

    if not messages:
        print("📭 No unread emails found.")
        return []

    emails = []
    for msg in messages:
        msg_data = service.users().messages().get(
            userId="me",
            id=msg["id"],
            format="full"
        ).execute()

        # Extract email details
        headers = msg_data["payload"]["headers"]
        subject = next((h["value"] for h in headers if h["name"] == "Subject"), "No Subject")
        sender  = next((h["value"] for h in headers if h["name"] == "From"), "Unknown")
        date    = next((h["value"] for h in headers if h["name"] == "Date"), "Unknown")

        # Extract body text
        body = extract_body(msg_data["payload"])

        emails.append({
            "id": msg["id"],
            "subject": subject,
            "sender": sender,
            "date": date,
            "body": body[:500]  # Limit to 500 characters for AI
        })

    print(f"✅ Fetched {len(emails)} emails.")
    return emails


def extract_body(payload):
    """Extract readable text from email body."""
    body = ""
    if "parts" in payload:
        for part in payload["parts"]:
            if part["mimeType"] == "text/plain":
                data = part["body"].get("data", "")
                if data:
                    body = base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
                    break
    else:
        data = payload["body"].get("data", "")
        if data:
            body = base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
    return body.strip()


# ============================================================
# STEP 3: Classify Emails with Claude AI
# ============================================================

def classify_emails(emails):
    """Send emails to Claude AI for classification."""
    if not emails:
        return []

    print(f"\n🤖 Classifying {len(emails)} emails with Claude AI...")

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    classified = []

    for email in emails:
        prompt = f"""
You are an email triage assistant for Keerthi, an IT professional actively job searching for AI engineering roles.
Classify the following email into exactly one category:

IMPORTANT — Flag these immediately:
- Job alerts, job matches, recruiter emails, interview invitations, job application updates
- Emails from real people (not automated systems)
- Legal or immigration documents (DocuSign, I-983, OPT, USCIS, visa-related)
- Payment confirmations, billing issues, bank alerts
- Emails from universities, employers, or government agencies
- Anything requiring action within 48 hours
- Password resets or security alerts

RELEVANT — Good to know but not urgent:
- Professional newsletters about AI, tech, or career development
- LinkedIn notifications about profile views or connections
- Work-related updates or system notifications
- Shipping or order confirmations

LOW_PRIORITY — Safe to ignore:
- Promotional emails from retail stores (Kohl's, SHEIN, Best Buy, etc.)
- Restaurant or food delivery promotions (Domino's, etc.)
- Entertainment recommendations (Netflix, Spotify, etc.)
- Sports betting or gambling emails
- Mass marketing emails
- Car dealership or auto service promotions

Email details:
From: {email['sender']}
Subject: {email['subject']}
Body preview: {email['body'][:300]}

Respond ONLY with a JSON object in this exact format:
{{"category": "IMPORTANT", "reason": "Brief reason why"}}

Categories must be exactly: IMPORTANT, RELEVANT, or LOW_PRIORITY
"""

        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}]
        )

        try:
            result = json.loads(response.content[0].text.strip())
            email["category"] = result.get("category", "RELEVANT")
            email["reason"] = result.get("reason", "")
        except Exception:
            email["category"] = "RELEVANT"
            email["reason"] = "Could not classify"

        classified.append(email)
        print(f"  {'🔴' if email['category'] == 'IMPORTANT' else '🟡' if email['category'] == 'RELEVANT' else '🟢'} {email['subject'][:50]}")

    print("✅ Classification complete!")
    return classified


# ============================================================
# STEP 4: Build Summary Report
# ============================================================

def build_summary(classified_emails):
    """Build a clean, readable email summary."""
    now = datetime.now().strftime("%B %d, %Y at %I:%M %p")

    important  = [e for e in classified_emails if e["category"] == "IMPORTANT"]
    relevant   = [e for e in classified_emails if e["category"] == "RELEVANT"]
    low        = [e for e in classified_emails if e["category"] == "LOW_PRIORITY"]

    lines = [
        f"📬 EMAIL TRIAGE SUMMARY",
        f"Generated: {now}",
        f"Total emails reviewed: {len(classified_emails)}",
        "=" * 50,
        ""
    ]

    # Important emails
    lines.append(f"🔴 IMPORTANT ({len(important)} emails)")
    if important:
        for e in important:
            lines.append(f"  • From: {e['sender'][:40]}")
            lines.append(f"    Subject: {e['subject'][:60]}")
            lines.append(f"    Why: {e['reason']}")
            lines.append("")
    else:
        lines.append("  None\n")

    # Relevant emails
    lines.append(f"🟡 RELEVANT ({len(relevant)} emails)")
    if relevant:
        for e in relevant:
            lines.append(f"  • From: {e['sender'][:40]}")
            lines.append(f"    Subject: {e['subject'][:60]}")
            lines.append("")
    else:
        lines.append("  None\n")

    # Low priority
    lines.append(f"🟢 LOW PRIORITY ({len(low)} emails)")
    if low:
        for e in low:
            lines.append(f"  • {e['subject'][:60]}")
    else:
        lines.append("  None")

    lines.append("")
    lines.append("=" * 50)
    lines.append("Next summary in 6 hours. Powered by Claude AI.")

    return "\n".join(lines)


# ============================================================
# STEP 5: Send Summary to Yourself
# ============================================================

def send_summary(service, summary_text):
    """Email the summary report to yourself."""
    now = datetime.now().strftime("%b %d, %I:%M %p")
    subject = f"📬 Email Summary — {now}"

    message = MIMEMultipart()
    message["to"]      = YOUR_EMAIL
    message["from"]    = YOUR_EMAIL
    message["subject"] = subject
    message.attach(MIMEText(summary_text, "plain"))

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    service.users().messages().send(
        userId="me",
        body={"raw": raw}
    ).execute()

    print(f"\n✅ Summary sent to {YOUR_EMAIL}!")


# ============================================================
# STEP 6: Main Run Function
# ============================================================

def run_agent():
    """Full agent run: fetch → classify → summarize → send."""
    print("\n" + "=" * 50)
    print(f"🚀 Gmail Triage Agent Running — {datetime.now().strftime('%I:%M %p')}")
    print("=" * 50)

    try:
        service         = connect_gmail()
        emails          = fetch_emails(service)

        if not emails:
            print("📭 No unread emails. Skipping summary.")
            return

        classified      = classify_emails(emails)
        summary         = build_summary(classified)

        print("\n" + summary)  # Print to terminal too
        send_summary(service, summary)

    except Exception as e:
        print(f"❌ Error: {e}")


# ============================================================
# STEP 7: Schedule Every 6 Hours
# ============================================================

if __name__ == "__main__":
    print("🤖 Gmail Triage Agent Starting...")
    print(f"📅 Will run every {SCHEDULE_HOURS} hours")

    # Schedule every 6 hours in background
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_agent, "interval", hours=SCHEDULE_HOURS)  # repeats every 6h
    scheduler.add_job(run_agent, "date")                            # runs once, ~now
    scheduler.start()

    print(f"\n⏰ Scheduler active. Next run in {SCHEDULE_HOURS} hours.")

    # Start Flask server (Cloud Run needs this)
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
