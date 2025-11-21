from imaplib import IMAP4_SSL
from os import getenv
import time
from dotenv import load_dotenv
from mailing import mail_controller
from persistence import db_controller
from transformer import ai_controller
from transformers import AutoModelForCausalLM, AutoTokenizer

# Step 0 Initialization
load_dotenv()

SCAN_INTERVAL = int(getenv('SCAN_INTERVAL'))

# Step 0c Load AI model
print("Loading Model...")

MODEL_NAME = getenv('MODEL')
transformer = ai_controller(MODEL_NAME)

print("Loaded Model ({})!".format(MODEL_NAME))

# Step 0a Connect to DB
print("Connecting to MySQL DB...")

MYSQL_CONN_PARAMS = {
	'host': getenv('MYSQL_HOST'),
	'user': getenv('MYSQL_USER'),
	'password': getenv('MYSQL_PASSWORD'),
	'database': getenv('MYSQL_DB')
}
db = db_controller(MYSQL_CONN_PARAMS)

print("Connected to MySQL DB!")

whitelist = db.select_whitelist()

# Step 0b Connect to Gmail
print("Connecting to Gmail Servers...")

MAIL_CONN_PARAMS = {
	'host': getenv('MAIL_HOST'),
	'address': getenv('MAIL_ADDRESS'),
	'password': getenv('MAIL_PASSWORD'),
	'inbox': getenv('MAIL_INBOX')
}
mail = mail_controller(MAIL_CONN_PARAMS, whitelist)

print("Connected to Gmail Servers!")

try:
	while True:
		# Step 1 Read Inbox (with whitelist checking)
		print("Fetching from Gmail Inbox")
		inbox = mail.fetch_unread()

		# Step 2 Process messages
		# Step 2a persist message
		if inbox:
			db_controller.insert_emails(inbox)

			for in_msg in inbox:
				# Step 2b respond to message
				msg_stack = db_controller.select_email_thread(in_msg['email_parent_id'])
				rsp_text = transformer(msg_stack)

				# Step 2d send reply
				rsp_msg = mail.send_reply(rsp_text, parent_id=in_msg['email_id'])
	
				# Step 2c persist reply
				db_controller.insert_email(rsp_msg)

		# Step 2e repeat from step 2a until no messages remain

		# Step 3 pause for X seconds for new messages to arrive, repeat from step 1 or shutdown
		print("Sleeping for {}s".format(SCAN_INTERVAL))
		time.sleep(SCAN_INTERVAL)

except KeyboardInterrupt:
    print("Terminating Mailbot")