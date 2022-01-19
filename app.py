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

class MyStackedWidget(QtWidgets.QStackedWidget):
    def __init__(self):
        super().__init__()

        self.menu_page = MenuPage()
        self.home_page = HomePage()
        self.addWidget(self.home_page)

        self.home_page.button.clicked.connect(self.change_to_menu_layout)

    def change_to_menu_layout(self):
        if self.sender() == self.home_page.button:
            self.addWidget(self.menu_page)
            self.setCurrentWidget(self.menu_page)


if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = MyStackedWidget()
    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec())
