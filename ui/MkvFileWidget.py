from PyQt6.QtWidgets import QLabel, QWidget, QHBoxLayout, QProgressBar
from PyQt6.QtGui import QFont


from ui.EllipsisQLabel import LeftEllipsisLabel

class MkvFileWidget(QWidget):


    STATUS_WAITING = 0
    STATUS_IN_PROGRESS = 1
    STATUS_DONE = 2
    STATUS_WARNING = 3
    STATUS_ERROR = 4

    def __init__(self, filepath, parent=None):
        super().__init__(parent)

        self.layout = QHBoxLayout(self)

        self.file_label = LeftEllipsisLabel(filepath)
        self.layout.addWidget(self.file_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)  # Example progress value
        self.layout.addWidget(self.progress_bar)

        self.status_icon_label = QLabel("⏳")


        font = self.status_icon_label.font()
        font.setPointSize(16)  # Set the font size to 16 (you can adjust this as needed)

        # Set the new font for the label
        self.status_icon_label.setFont(font)

        self.layout.addWidget(self.status_icon_label)

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def update_filepath(self, filepath):
        self.file_label.setText(filepath)

    def set_status_icon(self, status):
        if (status == MkvFileWidget.STATUS_WAITING):
            self.status_icon_label.setText("⏳")
        elif (status == MkvFileWidget.STATUS_IN_PROGRESS):
            self.status_icon_label.setText("⚙️")
        elif (status == MkvFileWidget.STATUS_DONE):
            self.status_icon_label.setText("✅")
        elif (status == MkvFileWidget.STATUS_WARNING):
            self.status_icon_label.setText("⚠️")
        elif (status == MkvFileWidget.STATUS_ERROR):
            self.status_icon_label.setText("❌")
        else:
            print(f"Unsupported status : {status}")
            pass
