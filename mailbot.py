from os import getenv
from dotenv import load_dotenv
from persistence import db_controller

# Step 0 Connect to DB and load AI model
load_dotenv()

MYSQL_CONN_PARAMS = {
    'host': getenv('MYSQL_HOST'),
	'user': getenv('MYSQL_USER'),
    'password': getenv('MYSQL_PASS'),
    'database': getenv('MYSQL_DB')
}

db_controller = db_controller(MYSQL_CONN_PARAMS)

# Step 1 Read Inbox (with whitelist checking)



# Step 2 Process messages
# Step 2a persist message



# Step 2b respond to message



# Step 2c send reply



# Step 2d persist reply



# Step 2e repeat from step 2a until no messages remain



# Step 3 pause for X seconds for new messages to arrive, repeat from step 1 or shutdown