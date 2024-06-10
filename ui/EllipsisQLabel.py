from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QPainter, QFontMetrics
from PyQt6.QtCore import Qt, QSize

class MiddleEllipsisLabel(QLabel):
    def __init__(self, text='', parent=None):
        super().__init__(text, parent)
        self.setText(text)

    def paintEvent(self, event):
        painter = QPainter(self)
        font_metrics = QFontMetrics(self.font())

        available_width = self.width()
        elided_text = self.elide_middle(self.text(), font_metrics, available_width)
        
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, elided_text)

    def elide_middle(self, text, font_metrics, width):
        if font_metrics.horizontalAdvance(text) <= width:
            return text

        ellipsis = "..."
        ellipsis_width = font_metrics.horizontalAdvance(ellipsis)
        available_width = width - ellipsis_width

        if available_width <= 0:
            return ellipsis

        left_part = text
        right_part = ""
        for i in range(len(text)):
            left_part = text[:i]
            right_part = text[-(i + 1):]
            if font_metrics.horizontalAdvance(left_part + ellipsis + right_part) >= width:
                left_part = text[:i - 1]
                right_part = text[-(i - 1):]
                break

        return left_part + ellipsis + right_part

class LeftEllipsisLabel(QLabel):
    def __init__(self, text='', parent=None):
        super().__init__(text, parent)
        self.full_text = text
        self.truncated_text = ""
        self.toggle_full_text = False  # Flag to toggle between full and truncated text
        #self.setWordWrap(True)
        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.setToolTip(self.full_text)
        self.update_displayed_text()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, self.displayed_text)

    def update_displayed_text(self):
        if self.toggle_full_text:
            self.displayed_text = self.full_text
            self.setMinimumWidth(0)
            self.setMaximumWidth(90000)
        else:
            self.displayed_text = self.truncated_text
            self.setFixedWidth(400)

    def elide_left(self, text, font_metrics, width):
        ellipsis = "..."
        ellipsis_width = font_metrics.horizontalAdvance(ellipsis)
        available_width = width - ellipsis_width

        if font_metrics.horizontalAdvance(text) <= available_width:
            return text

        left_part = ""
        right_part = text
        for i in range(len(text)):
            left_part = text[:i]
            right_part = text[-(i + 1):]
            if font_metrics.horizontalAdvance(left_part + ellipsis + right_part) >= available_width:
                left_part = text[:i - 1]
                right_part = text[-(i - 1):]
                break

        return left_part + ellipsis + right_part

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_truncated_text()

    def update_truncated_text(self):
        font_metrics = QFontMetrics(self.font())
        width = self.width()
        self.truncated_text = self.elide_left(self.full_text, font_metrics, width)
        self.update_displayed_text()

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if event.button() == Qt.MouseButton.LeftButton:
            self.toggle_full_text = not self.toggle_full_text
            self.update_displayed_text()
            self.update()
            event.accept()

    def minimumSizeHint(self):
        return QSize(0, QFontMetrics(self.font()).height())