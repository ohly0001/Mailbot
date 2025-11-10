import atexit
from imaplib import IMAP4_SSL


class mail_controller:
	def __init__(self, mail_conn_params):
		try:
			self.mail = IMAP4_SSL(mail_conn_params['host'])
			self.mail.login(mail_conn_params['user'], mail_conn_params['password'])
		except Exception as e:
			print("Failed to connect to mail server: {}".format(e))
			exit(2)
		
		atexit.register(self._cleanup)
		
	def _cleanup(self.):
		self.mail.logout()