import atexit
import mysql.connector

class db_controller:
	INSERT_MAIL="INSERT INTO emails (sender, subject, body) VALUES (%s, %s, %s);"
	SELECT_WHITELIST = "SELECT * FROM mailbot.correspondent_whitelist;"

	def __init__(self, mysql_conn_params):
		try:
			self.mydb=mysql.connector.connect(**mysql_conn_params)
			self.mycursor=self.mydb.cursor(dictionary=True)
		except Exception as e:
			print("Failed to connect to DB: {}".format(e))
			exit(1)

		atexit.register(self._cleanup)

	def fetch_white_list(self):
		try:
			self.mycursor.execute(self.SELECT_WHITELIST)
			return self.mycursor.fetchall()
		except Exception as e:
			print("Failed to fetch whitelist: {}".format(e))
			exit(1)

	def _cleanup(self):
		if not self.mycursor:
			self.mycursor.close()
		if not self.mydb:
			self.mydb.close()