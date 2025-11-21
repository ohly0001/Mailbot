import atexit
import mysql.connector

class db_controller:
	INSERT_MAIL="INSERT INTO emails (correspondent_id, subject_line, body_text, sent_on, message_uid) VALUES (%(correspondent_id)s, %(subject_line)s, %(body_text)s, %(sent_on)s, %(message_uid)s);"
	SELECT_WHITELIST = "SELECT * FROM mailbot.correspondent_whitelist;"

	def __init__(self, mysql_conn_params: dict[str, str]):
		try:
			self.mysql_conn_params = mysql_conn_params
			self.mydb=mysql.connector.connect(**mysql_conn_params)
			self.mycursor=self.mydb.cursor(dictionary=True)
   
		except mysql.connector.Error as err:
			print("Failed to connect to DB: {}".format(err))
			exit(1)

		atexit.register(self._cleanup)

	def select_whitelist(self):
		try:
			self.mycursor.execute(self.SELECT_WHITELIST)
			results = self.mycursor.fetchall()
			print("{} whitelist correspondent(s) was selected".format(len(results)))
			return results

		except mysql.connector.Error as err:
			print("Failed to fetch whitelist: {}".format(err))
			exit(1)
   
	def insert_email(self, email: dict[str, str]):
		try:
			self.mydb.start_transaction()
			self.mycursor.execute(self.SELECT_WHITELIST, email)
			self.mydb.commit()
			print("Email inserted")

		except mysql.connector.Error as err:
			self.mydb.rollback()
			print("Failed to put email: {}".format(err))
   
	def insert_emails(self, emails: list[dict[str, str]]):
		try:
			self.mydb.start_transaction()
			self.mycursor.executemany(self.SELECT_WHITELIST, emails)
			self.mydb.commit()
			print("{} email(s) inserted".format(self.mycursor.rowcount))
   
		except  mysql.connector.Error as err:
			self.mydb.rollback()
			print("Failed to insert emails: {}".format(err))

	def _cleanup(self):
		if not self.mycursor:
			self.mycursor.close()
		if not self.mydb:
			self.mydb.close()
		print("Disconnected from MySQL DB")