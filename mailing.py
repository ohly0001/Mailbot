import atexit
from datetime import datetime
from email.message import EmailMessage
import smtplib
from dateutil.tz import tzlocal
from email import message_from_bytes
from email.header import decode_header, make_header
from email.utils import parseaddr, parsedate_to_datetime
from imaplib import IMAP4_SSL, IMAP4

class mail_controller:
	def __init__(self, mail_conn_params, whitelist):
		try:
			self.mail_conn_params = mail_conn_params
			self.imap_conn = IMAP4_SSL(mail_conn_params['imap_host'])
			self.imap_conn.login(mail_conn_params['imap_user'], mail_conn_params['imap_password'])
			self.smtp_conn = smtplib.SMTP_SSL(mail_conn_params['smtp_host'], mail_conn_params['smtp_port'])
			self.smtp_conn.login(mail_conn_params['smtp_user'], mail_conn_params['smtp_password'])
			self.imap_conn.select(mail_conn_params['inbox'])

		except IMAP4.error as err:
			print(f"Failed to imap_connect to mail server: {err}")
			exit(2)
		atexit.register(self._cleanup)

		self.whitelist = tuple(row['whitelisted_address'] for row in whitelist)

	def send_reply(self, to_addr, subject, body):
		msg = EmailMessage()
		msg["From"] = self.mail_conn_params['smtp_user']
		msg["To"] = to_addr
		msg["Subject"] = subject
		msg.set_content(body)
    
		self.smtp_conn.send_message(msg)

	def fetch_unread(self) -> list[dict]:
		messages = []

		# Search for unread messages
		status, data = self.imap_conn.search(None, 'UNSEEN')
		if status != 'OK':
			return messages

		for num in data[0].split():
			# Fetch UID and RFC822 message
			status, msg_data = self.imap_conn.fetch(num, '(RFC822 UID)')
			if status != 'OK':
				print(f"Email received has status {status}. Skipping email.")
				continue

			raw_email = msg_data[0][1]
			msg = message_from_bytes(raw_email)

			# Mark message as seen (silently)
			try:
				self.imap_conn.store(num, '+FLAGS.SILENT', '\\Seen')
			except IMAP4.error as err:
				print(f"Issue encountered during store flagging. Skipping flagging: {err}")

			sender_name, sender_email = parseaddr(msg.get("From"))
			sender_email = sender_email.lower()
			if sender_email not in self.whitelist:
				print(f"{sender_email} is not in whitelist. Skipping email.")
				continue

			# UID parsing from fetch response
			uid = None
			for part in msg_data:
				if isinstance(part, tuple):
					resp = part[0].decode()
					if "UID " in resp:
						try:
							uid = int(resp.split("UID ", 1)[1].split()[0])
						except ValueError:
							uid = None
  
			if uid is None:
				print("Email received without UID. Skipping email.")
				continue

			# Get email body (plain text only)
			body = None
			if msg.is_multipart():
				for part in msg.walk():
					content_type = part.get_content_type()
					content_disposition = str(part.get("Content-Disposition"))
					if content_type == "text/plain" and "attachment" not in content_disposition:
						body_bytes = part.get_payload(decode=True)
						body = body_bytes.decode(part.get_content_charset() or 'utf-8', errors='ignore').strip()
						break
			else:
				if msg.get_content_type() == "text/plain":
					body = msg.get_payload(decode=True).decode(msg.get_content_charset() or 'utf-8', errors='ignore').strip()

			# Skip message if no plain text body found
			if body is None:
				print("Email received without plaintext content. Skipping email.")
				continue

			# Decode subject
			subject_raw = msg.get("Subject") or ""
			subject = str(make_header(decode_header(subject_raw)))
   
			# Message-ID and Parent-ID
			message_id = msg.get("Message-ID")
			parent_id = msg.get("In-Reply-To")

			# Sending time
			sending_time = None
			date_header = msg.get("Date")
			if date_header:
				try:
					sending_time = parsedate_to_datetime(date_header)
				except Exception:
					sending_time = datetime.now(tzlocal())  # fallback to current date

			messages.append({
				"email_uid": uid,
				"email_parent_id": parent_id,
				"email_id": message_id,
				"subject_line": subject,
				"sender_name": sender_name,
				"sender_address": sender_email,
				"body_text": body,
				"sent_on": sending_time
			})

		return messages

	def _cleanup(self):
		try:
			self.imap_conn.close()
		except IMAP4.error as err:
			print("Issue encountered during inbox closure: {}".format(err))
		self.imap_conn.logout()
		self.smtp_conn.quit()
		print("Disimap_connected from Gmail Servers")