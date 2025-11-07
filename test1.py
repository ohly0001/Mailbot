import os
from dotenv import load_dotenv
import imaplib
from email import message_from_bytes
from email.header import decode_header

load_dotenv()

mail = imaplib.IMAP4_SSL(os.getenv('IMAP4_SSL'))
mail.login(
    os.getenv('GMAIL_ADDRESS'),
    os.getenv('GMAIL_APP_PASSWORD')
)

mail.select("INBOX")
typ, data = mail.search(None, "ALL")  # or UNSEEN

for num in data[0].split():
    typ, msg_data = mail.fetch(num, "(RFC822)")
    raw_email = msg_data[0][1]
    msg = message_from_bytes(raw_email)

    # --- Decode the subject properly ---
    subject, encoding = decode_header(msg["Subject"])[0]
    if isinstance(subject, bytes):
        subject = subject.decode(encoding or "utf-8", errors="ignore")

    print(f"Subject: {subject}")
    print(f"From: {msg['From']}")

    # --- Extract plain text body ---
    body = None
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))

            if content_type == "text/plain" and "attachment" not in content_disposition:
                body = part.get_payload(decode=True)
                if body:
                    body = body.decode(part.get_content_charset() or "utf-8", errors="ignore")
                    break  # stop at first plaintext part
    else:
        # Not multipart — likely just text/plain
        body = msg.get_payload(decode=True)
        if body:
            body = body.decode(msg.get_content_charset() or "utf-8", errors="ignore")

    print("Body:\n", body or "(no plain text content)")
    print("=" * 60)

mail.close()
mail.logout()