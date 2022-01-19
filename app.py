import sys
from PySide6 import QtCore, QtWidgets, QtGui

class HomePage(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QtWidgets.QVBoxLayout(self)
        self.text = QtWidgets.QLabel("Welcome to Pixel Art on LAN! What is your name?", alignment=QtCore.Qt.AlignCenter)
        self.text_edit = QtWidgets.QTextEdit()
        self.button = QtWidgets.QPushButton("Continue")
        self.layout.addWidget(self.text)
        self.layout.addWidget(self.text_edit)
        self.layout.addWidget(self.button)

class MenuPage(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QtWidgets.QVBoxLayout(self)
        self.see_onlines_button = QtWidgets.QPushButton("See who else is online!")
        self.see_invitations_button = QtWidgets.QPushButton("Invitation Inbox")
        self.layout.addWidget(self.see_onlines_button)
        self.layout.addWidget(self.see_invitations_button)

class OnlineUsersPage(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QtWidgets.QVBoxLayout(self)

        online_user_names = ["alperen", "can"]
        self.online_user_names_text = QtWidgets.QLabel("\n".join(online_user_names))
        self.layout.addWidget(self.online_user_names_text)

        self.text = QtWidgets.QLabel("Send invitation!")
        self.text_edit = QtWidgets.QLineEdit()
        self.button = QtWidgets.QPushButton("Send")
        self.layout.addWidget(self.text)
        self.layout.addWidget(self.text_edit)
        self.layout.addWidget(self.button)

        self.go_back_button = QtWidgets.QPushButton("Go Back")
        self.layout.addWidget(self.go_back_button)

class MyStackedWidget(QtWidgets.QStackedWidget):
    def __init__(self):
        super().__init__()

        self.online_users_page = OnlineUsersPage()
        self.menu_page = MenuPage()
        self.home_page = HomePage()
        self.addWidget(self.home_page)

        self.home_page.button.clicked.connect(self.change_widget)
        self.menu_page.see_onlines_button.clicked.connect(self.change_widget)
        self.online_users_page.go_back_button.clicked.connect(self.change_widget)

    def change_widget(self):
        if self.sender() == self.home_page.button:
            self.addWidget(self.menu_page)
            self.setCurrentWidget(self.menu_page)
        elif self.sender() == self.menu_page.see_onlines_button:
            self.addWidget(self.online_users_page)
            self.setCurrentWidget(self.online_users_page)
        elif self.sender() == self.online_users_page.go_back_button:
            self.setCurrentWidget(self.menu_page)


if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = MyStackedWidget()
    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec())
