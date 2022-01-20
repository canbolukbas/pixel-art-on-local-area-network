from PySide6 import QtCore, QtWidgets, QtGui
import sys, random


class ColorButton(QtWidgets.QPushButton):
	def __init__(self, parent, color):
		super().__init__(parent)

		# To show which button is selected, the buttons are configured to be checkable.
		self.setCheckable(True)

		# The users are allowed to select only one color at once.
		# Therefore, color buttons in the same group are set to be exclusive.
		self.setAutoExclusive(True)

		# The given color gets assigned to the button.
		self.color = color
		self.color_code = self.color.name()
		self.setStyleSheet("background-color: {0}; border: 5px solid {0}".format(self.color_code))

	# Returns the code of the color in hexadecimal format.
	def get_color_code(self):
		return self.color.name()
		

class ColorSelectBar(QtWidgets.QWidget):
	def __init__(self, parent):
		super().__init__(parent)
		
		# Stores the HEX codes of the basic colors.
		self.colors = [
						"#FFFFFF",
						"#C0C0C0",
						"#808080",
						"#000000",
						"#FF0000",
						"#800000",
						"#FFFF00",
						"#808000",
						"#00FF00",
						"#008000",
						"#00FFFF",
						"#008080",
						"#0000FF",
						"#000080",
						"#FF00FF",
						"#800080"
					]
		# Will be used to store the buttons for each basic color.
		self.buttons = list()

		self.configure_layout_and_size()
		self.create_buttons()
		self.add_buttons()

	# Layout and the size of the toolbar get configured.
	def configure_layout_and_size(self):
		# Layout is set to be horizontal box layout.
		self.layout = QtWidgets.QHBoxLayout(self)
		# The toolbar stretches to the width of the widget of which the toolbar is placed inside.
		# The toolbar resizes to the minimum possible height.
		self.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Minimum)
		
	# Buttons for each color get created.
	def create_buttons(self):
		# For the user to be able to only check one color, the buttons are gathered in a button group.
		self.button_group = QtWidgets.QButtonGroup(self)

		# For each basic color, a button gets created.
		for color in self.colors:
			color_button = ColorButton(self, QtGui.QColor(color))
			self.buttons.append(color_button)
			self.button_group.addButton(color_button)

	# Buttons get added to the toolbar visibly.
	def add_buttons(self):
		for button in self.buttons:
			self.layout.addWidget(button)


class Board(QtWidgets.QTableWidget):
	# Creates the board and initializes it.
	def __init__(self, parent):
		row_count = 32
		column_count = 32
		super().__init__(row_count, column_count, parent)
		
		# Board is made ready for the game with the code block below.
		self.fit_into_window()
		self.hide_headers()
		self.fill()
		self.configure_edit_and_selection()

	# Resizes the board to fit into the given window.
	def fit_into_window(self):
		maximum_section_size = 1

		self.horizontalHeader().setMaximumSectionSize(maximum_section_size)
		self.verticalHeader().setMaximumSectionSize(maximum_section_size)

		self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
		self.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

	# The row and column headers of the board get hidden.
	def hide_headers(self):
		self.horizontalHeader().hide()
		self.verticalHeader().hide()

	# To be able to color board, each cell needs to be given a table widget item.
	# Empty cells are contain None.
	def fill(self):
		for i in range(32):
			for j in range(32):
				self.setItem(i, j, QtWidgets.QTableWidgetItem())

	# Disables the feature that allows users edit the cells through clicking.
	# Also, to remove the hover color, configures the cells to be non-selectable.
	def configure_edit_and_selection(self):
		self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
		self.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)

	# The two lines below are responsible for a critical functionality in this application:
	# By default, when the mouse is moved on the board while pressed, each cell along the path of the mouse gets selected one by one in order.
	# Therefore, in the context of this application, it would mean each of those cells would need to be colored.
	# So, a user could color 50 cells at one stroke.
	# This would mean having to send 50 packets (for 50 cells) to the other user in an extremely short time.
	#
	# We aim to update the board of each user almost simultaneously with each change on the board (on local or coming from the network).
	# By blocking users to use that mouse functionality, there will be more time between each packet sent.
	# (Because, users will not be able to color the next cell just by moving their mouse while pressed. To color the next cell, they will have to release the mouse, move to the next cell and click on the next cell.)
	# Therefore, a user will be less likely to re-color a cell that is already colored by the other user but not received from the network yet.
	# (Because it will take a little longer to color a cell after another cell, the user will have more time to see if the next cell is already colored by the other user.)
	def mouseMoveEvent(self, event):
		pass


class MyWidget(QtWidgets.QWidget):
	def __init__(self):
		super().__init__()
		self.setFixedSize(800,600)

		# self.save_button = QtWidgets.QPushButton("Save",self)
		# self.save_button.clicked.connect(self.save_image)

		self.table = Board(self)
		self.color_select_bar = ColorSelectBar(self)
		self.selected_color = None

		self.text = QtWidgets.QLabel("", alignment=QtCore.Qt.AlignCenter)

		self.table.cellClicked.connect(self.magic)
		self.color_select_bar.button_group.buttonClicked.connect(self.magic2)

		self.layout = QtWidgets.QVBoxLayout(self)
		self.layout.addWidget(self.table)
		self.layout.addWidget(self.text)
		self.layout.addWidget(self.color_select_bar)


	@QtCore.Slot()
	def magic(self, row, column):
		if self.selected_color:
			brush = QtGui.QBrush(self.selected_color)

			self.table.item(row,column).setBackground(brush)

	@QtCore.Slot()
	def magic2(self, button):
		self.selected_color = self.color_select_bar.button_group.checkedButton().color

	@QtCore.Slot()
	def save_image(self):
		self.table.grab().save("test.png")


if __name__ == "__main__":
	app = QtWidgets.QApplication([])

	widget = MyWidget()
	widget.show()

	sys.exit(app.exec())