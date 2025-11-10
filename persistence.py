import atexit
import os
from dotenv import load_dotenv
import mysql.connector

load_dotenv()

class db_controller:
	INSERT_MAIL="INSERT INTO emails (sender, subject, body) VALUES (%s, %s, %s)"
	SELECT_ONE=""

	def __init__(self):
		self.mydb=mysql.connector.connect(
			host="localhost",
			user=os.getenv('MYSQL_USER'),
			password=os.getenv('MYSQL_PASS'),
			database=os.getenv('MYSQL_DB')
		)
		self.mycursor=self.mydb.cursor(dictionary=True)

		atexit.register(self._cleanup)

	def create(self):
		pass

	def read_one(self):
		pass

	def read_all(self):
		pass

	def update(self):
		pass

	def delete(self):
		pass

def _cleanup(self):
		if not self.mycursor:
			self.mycursor.close()
		if not self.mydb:
			self.mydb.close()

if __name__=='__main__':
	db=db_controller()