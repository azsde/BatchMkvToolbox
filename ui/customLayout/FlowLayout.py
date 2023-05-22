#!/usr/bin/env python


#############################################################################
##
## Copyright (C) 2013 Riverbank Computing Limited.
## Copyright (C) 2010 Nokia Corporation and/or its subsidiary(-ies).
## All rights reserved.
##
## This file is part of the examples of PyQt.
##
## $QT_BEGIN_LICENSE:BSD$
## You may use this file under the terms of the BSD license as follows:
##
## "Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are
## met:
##   * Redistributions of source code must retain the above copyright
##     notice, this list of conditions and the following disclaimer.
##   * Redistributions in binary form must reproduce the above copyright
##     notice, this list of conditions and the following disclaimer in
##     the documentation and/or other materials provided with the
##     distribution.
##   * Neither the name of Nokia Corporation and its Subsidiary(-ies) nor
##     the names of its contributors may be used to endorse or promote
##     products derived from this software without specific prior written
##     permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
## "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
## LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
## A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
## OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
## SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
## LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
## DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
## THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
## OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
## $QT_END_LICENSE$
##
#############################################################################

from PyQt6.QtCore import QPoint, QRect, QSize, Qt, pyqtSignal
from PyQt6.QtWidgets import (QApplication, QLayout, QPushButton, QSizePolicy,
        QWidget)


class Window(QWidget):
    def __init__(self):
        super(Window, self).__init__()

        flowLayout = FlowLayout()
        flowLayout.addWidget(QPushButton("Short"))
        flowLayout.addWidget(QPushButton("Longer"))
        flowLayout.addWidget(QPushButton("Different text"))
        flowLayout.addWidget(QPushButton("More text"))
        flowLayout.addWidget(QPushButton("Even longer button text"))
        self.setLayout(flowLayout)

        self.setWindowTitle("Flow Layout")


class FlowLayout(QLayout):

    widthChanged = pyqtSignal(int)

    def __init__(self, parent=None, margin=0, spacing=-1, orientation=Qt.Orientation.Horizontal):
        super(FlowLayout, self).__init__(parent)

        if parent is not None:
            self.setContentsMargins(margin, margin, margin, margin)

        self.setSpacing(spacing)
        self.itemList = []
        self.orientation = orientation

    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item):
        self.itemList.append(item)

    def count(self):
        return len(self.itemList)

    def itemAt(self, index):
        if index >= 0 and index < len(self.itemList):
            return self.itemList[index]

        return None

    def takeAt(self, index):
        if index >= 0 and index < len(self.itemList):
            return self.itemList.pop(index)

        return None

    def expandingDirections(self):
        return Qt.Orientation(Qt.Orientation(0))

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        if (self.orientation == Qt.Orientation.Horizontal):
            return self.doLayoutHorizontal(QRect(0, 0, width, 0), True)
        elif (self.orientation == Qt.Orientation.Vertical):
            return self.doLayoutVertical(QRect(0, 0, width, 0), True)

    def setGeometry(self, rect):
        super(FlowLayout, self).setGeometry(rect)
        if (self.orientation == Qt.Orientation.Horizontal):
            self.doLayoutHorizontal(rect, False)
        elif (self.orientation == Qt.Orientation.Vertical):
            self.doLayoutVertical(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()

        for item in self.itemList:
            size = size.expandedTo(item.minimumSize())

        margin, _, _, _ = self.getContentsMargins()

        size += QSize(2 * margin, 2 * margin)
        return size

    def doLayoutHorizontal(self, rect, testOnly):
        # Get initial coordinates of the drawing region (should be 0, 0)
        x = rect.x()
        y = rect.y()
        lineHeight = 0
        i = 0
        for item in self.itemList:
            wid = item.widget()
            # Space X and Y is item spacing horizontally and vertically
            spaceX = self.spacing() + wid.style().layoutSpacing(QSizePolicy.ControlType.PushButton, QSizePolicy.ControlType.PushButton, Qt.Orientation.Horizontal)
            spaceY = self.spacing() + wid.style().layoutSpacing(QSizePolicy.ControlType.PushButton, QSizePolicy.ControlType.PushButton, Qt.Orientation.Vertical)
            # Determine the coordinate we want to place the item at
            # It should be placed at : initial coordinate of the rect + width of the item + spacing
            nextX = x + item.sizeHint().width() + spaceX
            # If the calculated nextX is greater than the outer bound...
            if nextX - spaceX > rect.right() and lineHeight > 0:
                x = rect.x() # Reset X coordinate to origin of drawing region
                y = y + lineHeight + spaceY # Move Y coordinate to the next line
                nextX = x + item.sizeHint().width() + spaceX # Recalculate nextX based on the new X coordinate
                lineHeight = 0

            if not testOnly:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))

            x = nextX # Store the next starting X coordinate for next item
            lineHeight = max(lineHeight, item.sizeHint().height())
            i = i + 1

        return y + lineHeight - rect.y()

    def doLayoutVertical(self, rect, testOnly):
        # Get initial coordinates of the drawing region (should be 0, 0)
        x = rect.x()
        y = rect.y()
        # Initalize column width and line height
        columnWidth = 0
        lineHeight = 0

        # Space between items
        spaceX = 0
        spaceY = 0

        # Variables that will represent the position of the widgets in a 2D Array
        i = 0
        j = 0
        for item in self.itemList:
            wid = item.widget()
            # Space X and Y is item spacing horizontally and vertically
            spaceX = self.spacing() + wid.style().layoutSpacing(QSizePolicy.ControlType.PushButton, QSizePolicy.ControlType.PushButton, Qt.Orientation.Horizontal)
            spaceY = self.spacing() + wid.style().layoutSpacing(QSizePolicy.ControlType.PushButton, QSizePolicy.ControlType.PushButton, Qt.Orientation.Vertical)
            # Determine the coordinate we want to place the item at
            # It should be placed at : initial coordinate of the rect + width of the item + spacing
            nextY = y + item.sizeHint().height() + spaceY
            # If the calculated nextY is greater than the outer bound, move to the next column
            if nextY - spaceY > rect.bottom() and columnWidth > 0:
                y = rect.y() # Reset y coordinate to origin of drawing region
                x = x + columnWidth + spaceX # Move X coordinate to the next column
                nextY = y + item.sizeHint().height() + spaceY # Recalculate nextX based on the new X coordinate
                # Reset the column width
                columnWidth = 0

                # Set indexes of the item for the 2D array
                j += 1
                i = 0

            # Assign 2D array indexes
            item.x_index = i
            item.y_index = j

            # Only call setGeometry (which place the actual widget using coordinates) if testOnly is false
            # For some reason, Qt framework calls the doLayout methods with testOnly set to true (WTF ??)
            if not testOnly:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))

            y = nextY # Store the next starting Y coordinate for next item
            columnWidth = max(columnWidth, item.sizeHint().width()) # Update the width of the column
            lineHeight = max(lineHeight, item.sizeHint().height()) # Update the height of the line

            i += 1 # Increment i

        # Only call setGeometry (which place the actual widget using coordinates) if testOnly is false
        # For some reason, Qt framework calls the doLayout methods with testOnly set to true (WTF ??)
        if not testOnly:
            self.calculateMaxWidth(i)
            #print("Total width : " + str(totalWidth))
            self.widthChanged.emit(self.totalMaxWidth + spaceX * self.itemsOnWidestRow)
            #self.widthChanged.emit(self.totalMaxWidth)
        return lineHeight

    # Method to calculate the maximum width among each "row" of the flow layout
    # This will be useful to let the UI know the total width of the flow layout
    def calculateMaxWidth(self, numberOfRows):
        # Init variables
        self.totalMaxWidth = 0
        self.itemsOnWidestRow = 0

        # For each "row", calculate the total width by adding the width of each item
        # and then update the totalMaxWidth if the calculated width is greater than the current value
        # Also update the number of items on the widest row
        for i in range(numberOfRows):
            rowWidth = 0
            itemsOnWidestRow = 0
            for item in self.itemList:
                # Only compare items from the same row
                if (item.x_index == i):
                    rowWidth += item.sizeHint().width()
                    itemsOnWidestRow += 1
                if (rowWidth > self.totalMaxWidth):
                    self.totalMaxWidth = rowWidth
                    self.itemsOnWidestRow = itemsOnWidestRow

if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    mainWin = Window()
    mainWin.show()
    sys.exit(app.exec())
