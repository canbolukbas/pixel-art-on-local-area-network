from PySide6 import QtCore, QtWidgets, QtGui
import sys, threading, socket, json
import gameboard
from sys import platform


UDP_BROADCAST_IP = ""  # this depends on different OS.
PORT_NUMBER = 12345
MAXIMUM_PACKET_LENGTH = 256

user_name = None

MAX_USER_NAME_LENGTH = 16

online_users = dict()

class Pixtura(QtWidgets.QStackedWidget):
	def __init__(self):
		super().__init__()

		self.udp_broadcast_listener = threading.Thread(target=self.listen_udp_broadcast, daemon=True)
		self.udp_broadcast_listener.start()

		self.tcp_listener = threading.Thread(target=self.listen_tcp, daemon=True)
		self.tcp_listener.start()

		self.setFixedSize(600,600)
		self.setWindowTitle("Pixtura")

		self.welcome_page = self.WelcomePage()
		self.welcome_page.join_button.clicked.connect(self.join)
		self.addWidget(self.welcome_page)

		self.main_menu = self.MainMenu()
		self.main_menu.view_online_users_page_button.clicked.connect(self.show_online_users)
		self.main_menu.view_invitations_inbox_page_button.clicked.connect(self.show_invitations_inbox)
		self.addWidget(self.main_menu)

		self.online_users_page = self.OnlineUsersPage()
		self.online_users_page.back_to_main_menu_button.clicked.connect(self.show_main_menu)
		self.addWidget(self.online_users_page)

		self.invitations_inbox_page = self.InvitationsInboxPage()
		self.invitations_inbox_page.back_to_main_menu_button.clicked.connect(self.show_main_menu)
		self.addWidget(self.invitations_inbox_page)

		self.in_game = False
		self.game_partner = None

		self.welcome_page.join_button.clicked.connect(self.join)
		self.online_users_page.send_invitation_button.clicked.connect(self.send_invitation)
		self.invitations_inbox_page.accept_invitation_button.clicked.connect(self.send_invitation)


	def process_packet(self, is_udp, data, sender_IP_address):
		global user_name, MAXIMUM_PACKET_LENGTH

		if not is_udp:
			data = data.recv(MAXIMUM_PACKET_LENGTH)

		if data:
			payload = data.decode('utf-8')
			try:
				message = json.loads(payload)
				message_type = message["type"]
				if message_type == 0:
					sender_name = message["name"]
					if sender_name == user_name:
						pass
					elif not online_users.get(sender_IP_address, False):
						online_users[sender_IP_address] = {"IP":sender_IP_address, "name":sender_name, "is_invitee":False, "is_inviter":False}
						self.send_discover_response(sender_IP_address)
				elif message_type == 1:
					sender_name = message["name"]
					online_users[sender_IP_address] = {"IP":sender_IP_address, "name":sender_name, "is_invitee":False, "is_inviter":False}
				elif message_type == 2:
					online_users[sender_IP_address]["is_inviter"] = True
				elif message_type == 3 and online_users[sender_IP_address]["is_invitee"] and not self.in_game:
					self.in_game = True
					self.in_game_with = sender_IP_address
					self.gameboard = gameboard.GameBoard()
					self.addWidget(self.gameboard)
					self.setCurrentWidget(self.gameboard)
				elif message_type == 4 and self.in_game and self.game_partner == sender_IP_address:
					cell_row = message["row"]
					cell_column = message["column"]
					cell_color = message["color_code"]
			except Exception as e:
				print(str(e))


	def listen_udp_broadcast(self):
		global UDP_BROADCAST_IP, PORT_NUMBER
		with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
			s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
			s.bind((UDP_BROADCAST_IP, PORT_NUMBER))
			while True:
				data, addr = s.recvfrom(MAXIMUM_PACKET_LENGTH)
				# addr[0] is the IP address of the sender.
				# Each packet gets processed in a separate thread.
				packet_processor = threading.Thread(target=self.process_packet, args=(True, data, addr[0],), daemon=True)
				packet_processor.start()


	def listen_tcp(self):
		global PORT_NUMBER
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
			# Listener socket binds to the determined port number.
			s.bind(('', PORT_NUMBER))
			# The number of unaccepted connections that the system will allow before refusing new connections is set to be 5.
			s.listen(5)
			# To enable the listener listen multiple connections simultaneously, each connection from clients are continuously handled by new subthreads.
			while(True):
				conn, addr = s.accept()
				# addr[0] is the IP address of the sender.
				packet_processor = threading.Thread(target=self.process_packet, args=(False, conn, addr[0],), daemon=True)
				packet_processor.start()


	def send_discover_response(self, receiver_IP_address):
		global user_name, PORT_NUMBER
		message = json.dumps({"type":1, "name":user_name}).encode('utf-8')
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
			try:
				s.connect((receiver_IP_address, PORT_NUMBER))
				s.sendall(message)
			except Exception as e:
				print(str(e))
				online_users.pop(receiver_IP_address, False)


	def discover(self):
		# Sends discovery messages to other users in the LAN, via the UDP broadcast channel '255.255.255.255'.
		global user_name, UDP_BROADCAST_IP, PORT_NUMBER
		message = json.dumps({"type":0, "name":user_name}).encode('utf-8')
		with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
			s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

			if platform == "darwin":
				s.bind(('', 0))

			for i in range(20):
				if platform == "darwin":
					s.sendto(message, ("<broadcast>", PORT_NUMBER))
				else:
					s.sendto(message, (UDP_BROADCAST_IP, PORT_NUMBER))


	def send_invitation(self):
		sender = self.sender()
		global PORT_NUMBER
		if sender == self.online_users_page.send_invitation_button:
			selected_user = self.online_users_page.select_invitee.currentData()
			message_type = 2
		elif sender == self.invitations_inbox_page.accept_invitation_button:
			selected_user = self.invitations_inbox_page.select_inviter.currentData()
			message_type = 3
		else:
			selected_user = None

		if selected_user is not None:
			receiver_IP_address = selected_user["IP"]
			message = json.dumps({"type": message_type}).encode('utf-8')
			with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
				try:
					s.connect((receiver_IP_address, PORT_NUMBER))
					s.sendall(message)
				except Exception as e:
					print(str(e))
					online_users.pop(receiver_IP_address, False)
				else:
					if message_type == 2:
						online_users[receiver_IP_address]["is_invitee"] = True

	def send_pixel(self):
		pass


	@QtCore.Slot()
	def join(self):
		global user_name
		user_name = self.welcome_page.user_name_input_field.text()
		self.show_main_menu()


	@QtCore.Slot()
	def show_main_menu(self):
		self.setCurrentWidget(self.main_menu)


	@QtCore.Slot()
	def show_online_users(self):
		self.online_users_page.online_users_list.update()
		self.online_users_page.select_invitee.update()
		self.setCurrentWidget(self.online_users_page)


	@QtCore.Slot()
	def show_invitations_inbox(self):
		self.invitations_inbox_page.inviter_users_list.update()
		self.invitations_inbox_page.select_inviter.update()
		self.setCurrentWidget(self.invitations_inbox_page)


	class WelcomePage(QtWidgets.QWidget):
		def __init__(self):
			super().__init__()
			self.setFixedSize(600,600)
			self.layout = QtWidgets.QVBoxLayout(self)
			self.layout.setAlignment(QtCore.Qt.AlignCenter)

			self.welcome_message = QtWidgets.QLabel("Welcome to Pixtura!", self, alignment=QtCore.Qt.AlignCenter)
			self.layout.addWidget(self.welcome_message)

			self.user_name_prompt = QtWidgets.QLabel('''What is your name?\n
													(A user name can be {} alphanumeric characters long at most.)'''.format(MAX_USER_NAME_LENGTH), 
														self, alignment=QtCore.Qt.AlignCenter)
			self.layout.addWidget(self.user_name_prompt)
			
			self.user_name_input_field = QtWidgets.QLineEdit(self)
			self.user_name_input_field.setInputMask("N"*MAX_USER_NAME_LENGTH)
			self.user_name_input_field.textEdited.connect(self.update_join_button)
			self.layout.addWidget(self.user_name_input_field)
			
			self.join_button = QtWidgets.QPushButton("Join!", self)
			self.join_button.setEnabled(False)
			self.layout.addWidget(self.join_button)


		@QtCore.Slot()
		def update_join_button(self, text):
			text_length = len(text)
			if text_length:
				self.join_button.setEnabled(True)
			else:
				self.join_button.setEnabled(False)


	class MainMenu(QtWidgets.QWidget):
		def __init__(self):
			super().__init__()
			self.setFixedSize(600,600)
			self.layout = QtWidgets.QVBoxLayout(self)
			self.layout.setAlignment(QtCore.Qt.AlignCenter)

			self.view_online_users_page_button = QtWidgets.QPushButton("See who is online", self)
			self.view_online_users_page_button.setFixedSize(200,200)
			self.layout.addWidget(self.view_online_users_page_button)

			self.view_invitations_inbox_page_button = QtWidgets.QPushButton("Invitations Inbox", self)
			self.view_invitations_inbox_page_button.setFixedSize(200,200)
			self.layout.addWidget(self.view_invitations_inbox_page_button)


	class OnlineUsersPage(QtWidgets.QWidget):
		def __init__(self):
			super().__init__()
			self.setFixedSize(600,600)
			self.layout = QtWidgets.QGridLayout(self)
			self.layout.setAlignment(QtCore.Qt.AlignCenter)

			self.online_users_list_header = QtWidgets.QLabel("List of currently online users:", self)
			self.layout.addWidget(self.online_users_list_header, 0, 0)

			self.back_to_main_menu_button = QtWidgets.QPushButton("Go back to main menu", self)
			self.layout.addWidget(self.back_to_main_menu_button, 0, 1, alignment=QtCore.Qt.AlignTop)

			self.online_users_list = self.OnlineUsersList(self)
			self.layout.addWidget(self.online_users_list, 1, 0)

			self.invite_user_prompt = QtWidgets.QLabel("To invite someone to play together:", self)
			self.layout.addWidget(self.invite_user_prompt, 2, 0)

			self.select_invitee = self.SelectInviteeComboBox(self)
			self.layout.addWidget(self.select_invitee, 3, 0)

			self.send_invitation_button = QtWidgets.QPushButton("Send Invitation", self)
			if self.select_invitee.currentIndex() == -1:
				self.send_invitation_button.setEnabled(False)
			self.select_invitee.currentIndexChanged.connect(self.check_selected_invitee)
			self.layout.addWidget(self.send_invitation_button, 3, 1)


		@QtCore.Slot()
		def check_selected_invitee(self, index):
			if index == -1:
				self.send_invitation_button.setEnabled(False)
			else:
				self.send_invitation_button.setEnabled(True)


		class OnlineUsersList(QtWidgets.QListWidget):
			def __init__(self, parent):
				super().__init__(parent)
				self.update()

			def update(self):
				self.clear()
				for user in online_users.keys():
					self.addItem(online_users[user]["name"])


		class SelectInviteeComboBox(QtWidgets.QComboBox):
			def __init__(self, parent):
				super().__init__(parent)
				self.update()

			def update(self):
				self.clear()
				for user in online_users.keys():
					self.addItem(online_users[user]["name"], userData=online_users[user])


	class InvitationsInboxPage(QtWidgets.QWidget):
		def __init__(self):
			super().__init__()
			self.setFixedSize(600,600)
			self.layout = QtWidgets.QGridLayout(self)
			self.layout.setAlignment(QtCore.Qt.AlignCenter)

			self.inviter_users_list_header = QtWidgets.QLabel("List of the users who have sent you an invitation:", self)
			self.layout.addWidget(self.inviter_users_list_header, 0, 0)

			self.back_to_main_menu_button = QtWidgets.QPushButton("Go back to main menu", self)
			self.layout.addWidget(self.back_to_main_menu_button, 0, 1, alignment=QtCore.Qt.AlignTop)

			self.inviter_users_list = self.InviterUsersList(self)
			self.layout.addWidget(self.inviter_users_list, 1, 0)

			self.accept_invitation_prompt = QtWidgets.QLabel("To accept the invitation of an inviter user:", self)
			self.layout.addWidget(self.accept_invitation_prompt, 2, 0)

			self.select_inviter = self.SelectInviterComboBox(self)
			self.layout.addWidget(self.select_inviter, 3, 0)

			self.accept_invitation_button = QtWidgets.QPushButton("Accept Invitation", self)
			if self.select_inviter.currentIndex() == -1:
				self.accept_invitation_button.setEnabled(False)
			self.select_inviter.currentIndexChanged.connect(self.check_selected_inviter)
			self.layout.addWidget(self.accept_invitation_button, 3, 1)


		@QtCore.Slot()
		def check_selected_inviter(self, index):
			if index == -1:
				self.accept_invitation_button.setEnabled(False)
			else:
				self.accept_invitation_button.setEnabled(True)


		class InviterUsersList(QtWidgets.QListWidget):
			def __init__(self, parent):
				super().__init__(parent)
				self.update()

			def update(self):
				self.clear()
				for user in online_users.keys():
					if online_users[user]["is_inviter"]:
						self.addItem(online_users[user]["name"])


		class SelectInviterComboBox(QtWidgets.QComboBox):
			def __init__(self, parent):
				super().__init__(parent)
				self.update()

			def update(self):
				self.clear()
				for user in online_users.keys():
					if online_users[user]["is_inviter"]:
						self.addItem(online_users[user]["name"], userData=online_users[user])


if __name__ == "__main__":
	app = QtWidgets.QApplication([])

	widget = Pixtura()
	widget.show()

	UDP_BROADCAST_IP = "" if platform == "darwin" else "255.255.255.255"

	sys.exit(app.exec())