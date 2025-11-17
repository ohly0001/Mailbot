import atexit
import datetime
from email import message_from_bytes
from email.header import decode_header
from email.utils import parseaddr, parsedate_to_datetime
from imaplib import IMAP4_SSL
from dateutil import parser as dateparser

class mail_controller:
    def __init__(self, mail_conn_params, whitelist):
        try:
            self.mail = IMAP4_SSL(mail_conn_params['host'])
            self.mail.login(mail_conn_params['user'], mail_conn_params['password'])
        except Exception as e:
            print("Failed to connect to mail server: {}".format(e))
            exit(2)

        atexit.register(self._cleanup)

        self.address_id_mapping = {
            row['email_address'].lower(): row['correspondent_id']
            for row in whitelist
        }

    def fetch_unread(self):
        self.mail.select("INBOX")
        typ, data = self.mail.search(None, "UNSEEN")

        results = []

        for num in data[0].split():

            # mark as read with SILENT flag change (more efficient)
            self.mail.store(num, '+FLAGS.SILENT', '\\Seen')

            typ, msg_data = self.mail.fetch(num, "(RFC822)")
            raw_email = msg_data[0][1]
            msg = message_from_bytes(raw_email)

            # ----------------------
            # 1. Parse & normalize Date
            # ----------------------
            date_header = msg.get("Date")
            if date_header:
                try:
                    date = parsedate_to_datetime(date_header)
                except Exception:
                    try:
                        date = dateparser.parse(date_header)
                    except Exception:
                        date = None
            else:
                date = None

            # ----------------------
            # 2. Decode Subject safely
            # ----------------------
            raw_subject = msg.get("Subject")
            if raw_subject is None:
                subject = "No Subject"
            else:
                parts = decode_header(raw_subject)
                subject, encoding = parts[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding or "utf-8", errors="ignore")

            # ----------------------
            # 3. Normalize sender email
            # ----------------------
            email_address = parseaddr(msg.get("From", ""))[1].lower()
            correspondent_id = self.address_id_mapping.get(email_address, 0)

            # ----------------------
            # 4. Extract plain text body safely
            # ----------------------
            body = None

            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disp = str(part.get("Content-Disposition") or "")
                    filename = part.get_filename()

                    if (
                        content_type == "text/plain"
                        and "attachment" not in content_disp.lower()
                        and filename is None
                    ):
                        payload = part.get_payload(decode=True)
                        if payload:
                            body = payload.decode(
                                part.get_content_charset() or "utf-8",
                                errors="ignore"
                            )
                            break
            else:
                payload = msg.get_payload(decode=True)
                if payload:
                    body = payload.decode(
                        msg.get_content_charset() or "utf-8",
                        errors="ignore"
                    )

            if body:
                body = body.strip()
            else:
                body = "No Message"

            results.append({
                'correspondent_id': correspondent_id,
                'subject_line': subject,
                'body_text': body,
                'sent_on': date
            })

        # ----------------------
        # 5. Sort safely regardless of timezone presence
        # ----------------------
        epoch = datetime.datetime.min.replace(tzinfo=datetime.timezone.utc)
        results.sort(key=lambda r: r['sent_on'] or epoch)

        return results

    def _cleanup(self):
        try:
            self.mail.close()
        except:
            pass  # mailbox may already be closed
        self.mail.logout()
