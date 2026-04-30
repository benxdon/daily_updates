"parsing email from .mbox file to clean readable data"

import mailbox #to open .mbox file
import email
from bs4 import BeautifulSoup # to parse html files
from email import policy # message parser
from email.parser import BytesParser 

def html_to_text(html):
    soup = BeautifulSoup(html, "html.parser")


def get_body(msg):
    if not msg.is_multipart():
        return msg.get_content()
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
    msgs = mailbox.mbox("data/inbox.mbox",factory=lambda f: BytesParser(policy=policy.default).parse(f)) # byteparser is for parsing the email object

    for i, msg in enumerate(msgs):
        print(f"---email {i}---")
        print(f"From:        {msg['From']}")
        print(f"Subject:     {msg['Subject']}")
        print(f"Date:        {msg['Date']}")
        print(f"Content-Type: {msg.get_content_type()}")

        body = get_body(msg)
        print(f"Body preview: {body[:200]}")

        print()
        if i == 4:
            break
