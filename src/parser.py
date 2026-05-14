"parsing email from .mbox file to clean readable data"

import mailbox #to open .mbox file
from email.utils import parsedate_to_datetime
from bs4 import BeautifulSoup # to parse html files
from email import policy # message parser
from email.parser import BytesParser
from datetime import datetime
from dataclasses import dataclass, field
import json


@dataclass
class Email:
    from_address: str
    to: str
    subject: str
    body: str
    date: datetime|None
    message_id:str = ""
    in_reply_to: str = ""
    references: list[str] = field(default_factory=list)


def save_emails(emails, path="data/parsed_emails.json"):
    data = []
    for e in emails:
        d = {
            "from_address": e.from_address,
            "to": e.to,
            "subject": e.subject,
            "body": e.body,
            "date": e.date.isoformat() if e.date else None,
            "message_id": e.message_id,
            "in_reply_to": e.in_reply_to,
            "references": e.references
        }
        for key, val in d.items():
            if isinstance(val, bytes):
                d[key] = val.decode("utf-8", errors="replace")

        data.append(d)

    with open(path,"w") as f:
        json.dump(data,f)
    print(f"Saved {len(data)} emails to {path}")


def load_emails(path="data/parsed_emails.json"):
    with open(path) as f:
        data = json.load(f)
    emails = []
    for d in data:
        emails.append(Email(
            from_address = d["from_address"],
            to = d["to"],
            subject = d["subject"],
            body = d["body"],
            date = datetime.fromisoformat(d["date"]) if d["date"] else None,
            message_id = d["message_id"],
            in_reply_to = d["in_reply_to"],
            references = d["references"]
        ))
    print(f"Loaded {len(emails)} emails from {path}")
    return emails


def html_to_text(html):
    soup = BeautifulSoup(html, "html.parser")

    for element in soup(['script', 'style', 'meta', 'noscript']):
        element.decompose()

    return soup.get_text(separator=' ', strip=True)


def get_body(msg):
    if not msg.is_multipart():
        content = msg.get_content()
        if msg.get_content_type() == "text/html":
            return html_to_text(content)
        return content

    plain = None
    html = None

    for part in msg.walk():
        content_type = part.get_content_type()
        
        if content_type == "text/plain" and plain is None:
            plain = part.get_content()
        elif content_type == "text/html" and html is None:
            html = part.get_content()

    if plain is not None: 
        return plain
    elif html is not None: 
        return html_to_text(html)  

    return "" 


if __name__ == "__main__":
    import os
    
    parsed_path = "data/parsed_emails.json"

    if os.path.exists(parsed_path):
        cleaned_emails = load_emails(parsed_path)

    else:
        msgs = mailbox.mbox("data/inbox.mbox",factory=lambda f: BytesParser(policy=policy.default).parse(f)) # byteparser is for parsing the email object
        cleaned_emails = []

        for i, msg in enumerate(msgs):
            #print(f"---email {i}---")
            #print(f"From:        {msg['From']}")
            #print(f"Subject:     {msg['Subject']}")
            #print(f"Date:        {msg['Date']}")
            #print(f"Content-Type: {msg.get_content_type()}")

            body = get_body(msg)
            #print(f"Body preview: {body[:200]}")

            try:
                date = parsedate_to_datetime(msg['Date'])
            except Exception:
                date = None

            try:
                refs = msg['References']
                e = Email(
                    from_address=msg['From'] or "",
                    to=msg['To'] or "",
                    subject=msg['Subject'],
                    body=body,
                    date=date,
                    message_id=msg['Message-ID'] or "",
                    in_reply_to=msg['In-Reply-To'] or "",
                    references=refs.split() if refs else [],
                )
                cleaned_emails.append(e)

            except Exception as err:
                print(f"Skipping email {i}: {err}")

            #print()
            #if i == 4:
            #break

        save_emails(cleaned_emails)
        print(f"Parsed: {len(cleaned_emails)}")

    print(f"Total: {len(cleaned_emails)} emails")
