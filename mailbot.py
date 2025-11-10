from imaplib import IMAP4_SSL
from os import getenv
from dotenv import load_dotenv
from mailing import mail_controller
from persistence import db_controller
from transformers import AutoModelForCausalLM, AutoTokenizer

# Step 0 Initialization
load_dotenv()

# Step 0c Load AI model
MODEL_NAME = getenv('MODEL')
print("Loading {}...".format(MODEL_NAME),end='\r')
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
print("Loaded {}!".format(MODEL_NAME))

# Step 0a Connect to DB
print("Connecting to MySQL DB...",end='\r')

MYSQL_CONN_PARAMS = {
	'host': getenv('MYSQL_HOST'),
	'user': getenv('MYSQL_USER'),
	'password': getenv('MYSQL_PASSWORD'),
	'database': getenv('MYSQL_DB')
}
db = db_controller(MYSQL_CONN_PARAMS)

print("Connected to MySQL DB!")

# Step 0b Connect to Gmail
print("Connecting to Gmail...",end='\r')

MAIL_CONN_PARAMS = {
	'host': getenv('MAIL_HOST'),
	'user': getenv('MAIL_USER'),
	'password': getenv('MAIL_PASSWORD')
}
mail = mail_controller(MAIL_CONN_PARAMS)

print("Connected to Gmail!")

# Step 1 Read Inbox (with whitelist checking)



# Step 2 Process messages
# Step 2a persist message



# Step 2b respond to message



# Step 2c send reply



# Step 2d persist reply



# Step 2e repeat from step 2a until no messages remain



# Step 3 pause for X seconds for new messages to arrive, repeat from step 1 or shutdown




mail.logout()