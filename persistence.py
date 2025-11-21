import atexit
import mysql.connector

class db_controller:
	INSERT_MAIL="INSERT INTO emails (email_id, email_parent_id, correspondent_id, subject_line, body_text, sent_on, email_uid) VALUES (%(email_id)s, %(email_parent_id)s, %(correspondent_id)s, %(subject_line)s, %(body_text)s, %(sent_on)s, %(email_uid)s);"
	SELECT_MAIL_BY_PARENT="SELECT (email_id, email_parent_id, correspondent_id, subject_line, body_text, sent_on, email_uid) FROM emails WHERE email_parent_id = %s"
	SELECT_WHITELIST = "SELECT (correspondent_id, preferred_name, email_address, added_on) FROM correspondent_whitelist;"

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
   
		except mysql.connector.Error as err:
			self.mydb.rollback()
			print("Failed to insert emails: {}".format(err))

	def select_email_thread(self, parent_id: int):
		try:
			results = []
			while parent_id:
				result = self.mycursor(self.SELECT_MAIL_BY_PARENT, parent_id)
				results.append(result)
				parent_id = result['email_parent_id']
			print("{} email(s) selected in thread".format(len(results)))
			return results

		except mysql.connector.Error as err:
			print("Failed to retrieve thread: {}".format(err))
			return []

	def _cleanup(self):
		if not self.mycursor:
			self.mycursor.close()
		if not self.mydb:
			self.mydb.close()
		print("Disconnected from MySQL DB")