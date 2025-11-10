import atexit
import mysql.connector

class db_controller:
	INSERT_MAIL="INSERT INTO emails (sender, subject, body) VALUES (%s, %s, %s)"
	SELECT_ONE=""

	def __init__(self, mysql_conn_params):
		try:
			self.mydb=mysql.connector.connect(**mysql_conn_params)
			self.mycursor=self.mydb.cursor(dictionary=True)
		except Exception as e:
			print("Failed to connect to DB: {}".format(e))
			exit(1)

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