import anthropic

client = anthropic.Anthropic()

def classify_email(subject, sender, body):
    prompt = f"""You are an email triage assistant. Classify this email and decide if it needs a reply.

Email details:
From: {sender}
Subject: {subject}
Body: {body}

Respond in this exact format:
PRIORITY: [HIGH/MEDIUM/LOW]
CATEGORY: [WORK/PERSONAL/NEWSLETTER/SPAM/OTHER]
NEEDS_REPLY: [YES/NO]
SUMMARY: [One sentence summary]
SUGGESTED_REPLY: [Write a brief professional reply if NEEDS_REPLY is YES, otherwise write NONE]"""

    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return message.content[0].text

def parse_classification(text):
    lines = text.strip().split('\n')
    result = {}
    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            result[key.strip()] = value.strip()
    return result
