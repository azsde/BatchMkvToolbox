import sys

import PyQt5.QtWidgets as qtw

from PyQt5.QtWidgets import QMainWindow, QDesktopWidget, QApplication, QPushButton, QWidget, QAction, QTabWidget,QVBoxLayout
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = 'BatchMkvToolbox'
        self.left = 0
        self.top = 0
        self.width = 800
        self.height = 600
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # Move window to the center of the screen
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle = self.frameGeometry()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())
        
        #self.table_widget = MyTableWidget(self)
        #self.setCentralWidget(self.table_widget)

        self.setLayout(qtw.QVBoxLayout())
        
        self.show()
    
#class MyTableWidget(QWidget):
#    
#    def __init__(self, parent):
#        super(QWidget, self).__init__(parent)
#        self.layout = QVBoxLayout(self)
#        
#        # Initialize tab screen
#        self.tabs = QTabWidget()
#        self.tab1 = QWidget()
#        self.tab2 = QWidget()
#        self.tabs.resize(300,200)
#        
#        # Add tabs
#        self.tabs.addTab(self.tab1,"Tab 1")
#        self.tabs.addTab(self.tab2,"Tab 2")
#        
#        # Create first tab
#        self.tab1.layout = QVBoxLayout(self)
#        self.pushButton1 = QPushButton("PyQt5 button")
#        self.tab1.layout.addWidget(self.pushButton1)
#        self.tab1.setLayout(self.tab1.layout)
#        
#        # Add tabs to widget
#        self.layout.addWidget(self.tabs)
#        self.setLayout(self.layout)
#        
#    @pyqtSlot()
#    def on_click(self):
#        print("\n")
#        for currentQTableWidgetItem in self.tableWidget.selectedItems():
#            print(currentQTableWidgetItem.row(), currentQTableWidgetItem.column(), currentQTableWidgetItem.text())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
