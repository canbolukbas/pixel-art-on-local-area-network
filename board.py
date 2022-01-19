from PySide6 import QtCore, QtWidgets, QtGui
import sys

class Board(QtWidgets.QTableWidget):

	def __init__(self, parent):
		row_count = 32
		column_count = 32
		maximum_section_size = 1

		super().__init__(row_count, column_count, parent)

		self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers);

		self.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)

		self.horizontalHeader().setMaximumSectionSize(maximum_section_size)
		self.verticalHeader().setMaximumSectionSize(maximum_section_size)

		self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
		self.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

		self.horizontalHeader().hide()
		self.verticalHeader().hide()

	def mouseMoveEvent(self, event):
		pass


class MyWidget(QtWidgets.QWidget):
	def __init__(self):
		super().__init__()
		self.setFixedSize(800,600)

		self.table = Board(self)

		self.text = QtWidgets.QLabel("", alignment=QtCore.Qt.AlignCenter)

		self.table.cellClicked.connect(self.magic)

		self.layout = QtWidgets.QVBoxLayout(self)
		self.layout.addWidget(self.table)
		self.layout.addWidget(self.text)

	@QtCore.Slot()
	def magic(self, row, column):
		self.text.setText(str((row, column)))

if __name__ == "__main__":
	app = QtWidgets.QApplication([])

	widget = MyWidget()
	widget.show()

	sys.exit(app.exec())