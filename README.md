# Gmail Triage Agent

An AI-powered agent that automatically reads your unread Gmail, classifies each message by priority using the Anthropic Claude API, and emails you a clean summary report every 6 hours. Runs 24/7 on Google Cloud Run.

## What it does

1. **Fetches** unread emails from your Gmail inbox via the Gmail API.
2. **Classifies** each email into one of three priority tiers using Claude:
   - 🔴 **Important** – needs immediate attention (urgent deadlines, payments, personal contacts)
   - 🟡 **Relevant** – good to know but not urgent (work updates, newsletters you care about)
   - 🟢 **Low priority** – can be ignored (promotions, mass emails, spam)
3. **Summarizes** the results into a readable report.
4. **Sends** the summary to your inbox on a recurring schedule.

## Tech stack

- **Python** – core application
- **Gmail API** – reading and sending email
- **Anthropic Claude API** – email classification
- **APScheduler** – runs the triage every 6 hours
- **Flask** – lightweight HTTP server (required by Cloud Run)
- **Docker** – containerization
- **Google Cloud Run** – serverless 24/7 hosting
- **Google Secret Manager** – secure storage of API keys and OAuth tokens

## How it works

The agent runs as a containerized service on Cloud Run with a single always-on instance, so the scheduler never sleeps. A Flask endpoint (`/`) serves as a health check so Cloud Run knows the service is alive. APScheduler triggers the triage job on startup and then every 6 hours after that. Credentials are never stored in the image — the Anthropic API key and Gmail OAuth token are injected at runtime from Secret Manager.

## Setup

> **Note:** This project requires your own Google Cloud project, a Gmail OAuth credentials file, and an Anthropic API key.

1. **Clone the repo**
   ```bash
   git clone https://github.com/keerthija1/gmail-triage-agent.git
   cd gmail-triage-agent
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Add your Gmail credentials**
   Place your `credentials.json` (from Google Cloud Console → OAuth client) in the project folder. On first local run, a browser window opens to authorize access and generates `token.json`.

4. **Set your Anthropic API key**
   ```bash
   export ANTHROPIC_API_KEY="your-key-here"
   ```

5. **Run locally**
   ```bash
   python main.py
   ```

## Deploying to Google Cloud Run

Store secrets in Secret Manager, then deploy from source:

```bash
gcloud run deploy gmail-triage-agent \
  --source . \
  --region us-central1 \
  --set-secrets="ANTHROPIC_API_KEY=ANTHROPIC_API_KEY:latest,GMAIL_TOKEN=GMAIL_TOKEN:latest" \
  --min-instances=1 \
  --allow-unauthenticated \
  --memory=512Mi \
  --timeout=600
```

## Configuration

Key settings live at the top of `main.py`:

| Setting | Description |
|---------|-------------|
| `YOUR_EMAIL` | Address(es) the summary is sent to |
| `MAX_EMAILS` | How many unread emails to fetch per run |
| `SCHEDULE_HOURS` | How often the triage runs (default: 6 hours) |

## Security

- Secret files (`credentials.json`, `token.json`) are excluded from version control via `.gitignore` and must never be committed.
- In production, all credentials are pulled from Google Secret Manager at runtime.

## Notes

This is a personal learning project built to explore AI agents, the Gmail and Anthropic APIs, containerization, and cloud deployment.
