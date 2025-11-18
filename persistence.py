import atexit
import mysql.connector

class db_controller:
	INSERT_MAIL="INSERT INTO emails (correspondent_id, subject_line, body_text, sent_on, message_uid) VALUES (%(correspondent_id)s, %(subject_line)s, %(body_text)s, %(sent_on)s, %(message_uid)s);"
	SELECT_WHITELIST = "SELECT * FROM mailbot.correspondent_whitelist;"

	def __init__(self, mysql_conn_params):
		try:
			self.mydb=mysql.connector.connect(**mysql_conn_params)
			self.mycursor=self.mydb.cursor(dictionary=True)
		except Exception as e:
			print("Failed to connect to DB: {}".format(e))
			exit(1)

		atexit.register(self._cleanup)

	def select_whitelist(self):
		try:
			self.mycursor.execute(self.SELECT_WHITELIST)
			results = self.mycursor.fetchall()
			print("{} whitelist correspondent(s) was selected".format(len(results)))
			return results

		except Exception as e:
			print("Failed to fetch whitelist: {}".format(e))
			exit(1)
   
	def insert_emails(self, emails):
		try:
			self.mydb.start_transaction()
			self.mycursor.executemany(self.SELECT_WHITELIST, emails)
   
		except Exception as e:
			self.mydb.rollback()
			print("Failed to put emails: {}".format(e))
			exit(1)
   
		self.mydb.commit()
		print("{} email(s) was inserted".format(self.mycursor.rowcount))

	def _cleanup(self):
		if not self.mycursor:
			self.mycursor.close()
		if not self.mydb:
			self.mydb.close()
		print("Disconnected from MySQL DB")