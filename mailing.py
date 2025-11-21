import atexit
from email import message_from_bytes
from email.header import decode_header, make_header
from email.utils import parseaddr, parsedate_to_datetime
from imaplib import IMAP4_SSL

class mail_controller:
	def __init__(self, mail_conn_params, whitelist):
		try:
			self.mail_conn_params = mail_conn_params
			self.conn = IMAP4_SSL(mail_conn_params['host'])
			self.conn.login(mail_conn_params['user'], mail_conn_params['password'])
			self.conn.select(mail_conn_params['inbox'])
		except Exception as e:
			print("Failed to connect to mail server: {}".format(e))
			exit(2)

		atexit.register(self._cleanup)

		self.address_id_mapping = {
			row['email_address'].lower(): row['correspondent_id']
			for row in whitelist
		}

	def fetch_unread(self) -> list[dict]:
		messages = []

		# Search for unread messages
		status, data = self.conn.search(None, 'UNSEEN')
		if status != 'OK':
			return messages

		for num in data[0].split():
			# Fetch UID and RFC822 message
			status, msg_data = self.conn.fetch(num, '(RFC822 UID)')
			if status != 'OK':
				continue

			raw_email = msg_data[0][1]
			msg = message_from_bytes(raw_email)

			sender_name, sender_email = parseaddr(msg.get("From"))
			sender_email = sender_email.lower()
			if sender_email not in self.address_id_mapping.keys():
				print("Email received that is not in whitelist: {}".format(sender_email))
				continue
			correspondent_id = self.address_id_mapping[sender_email.lower()]

			# Get email body (plain text only)
			body = None
			if msg.is_multipart():
				for part in msg.walk():
					content_type = part.get_content_type()
					content_disposition = str(part.get("Content-Disposition"))
					if content_type == "text/plain" and "attachment" not in content_disposition:
						body_bytes = part.get_payload(decode=True)
						body = body_bytes.decode(part.get_content_charset() or 'utf-8', errors='ignore')
						break
			else:
				if msg.get_content_type() == "text/plain":
					body = msg.get_payload(decode=True).decode(msg.get_content_charset() or 'utf-8', errors='ignore')

			# Skip message if no plain text body found
			if body is None:
				continue

			# Decode subject
			subject = str(make_header(decode_header(msg.get("Subject"))))

			# Sender
			sender = msg.get("From")

			# Message-ID and Parent-ID
			message_id = msg.get("Message-ID")
			parent_id = msg.get("In-Reply-To")

			# UID parsing from fetch response
			uid = None
			for part in msg_data:
				if isinstance(part, tuple):
					resp = part[0].decode()
					if "UID" in resp:
						uid = resp.split("UID")[1].split()[0]

			# Sending time
			sending_time = None
			date_header = msg.get("Date")
			if date_header:
				try:
					sending_time = parsedate_to_datetime(date_header)
				except Exception:
					sending_time = date_header  # fallback to raw string if parsing fails

			# Mark message as seen (silently)
			try:
				self.conn.store(num, '+FLAGS.SILENT', '\\Seen')
			except IMAP4_SSL.error as err:
				print("Issue encountered during store flagging: {}".format(err))

			messages.append({
				"email_uid": uid,
				"email_id": message_id,
				"email_parent_id": parent_id,
				"subject_line": subject,
				"correspondent_id": correspondent_id,
				"body_text": body,
				"sent_on": sending_time
			})

		return messages

	def _cleanup(self):
		try:
			self.conn.close()
		except IMAP4_SSL.error as err:
			print("Issue encountered during inbox closure: {}".format(err))
		self.conn.logout()
		print("Disconnected from Gmail Servers")