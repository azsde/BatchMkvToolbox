from PyQt6.QtWidgets import QLabel, QWidget, QHBoxLayout, QProgressBar

from ui.EllipsisQLabel import LeftEllipsisLabel

class MkvFileWidget(QWidget):
    def __init__(self, filepath, parent=None):
        super().__init__(parent)

        self.layout = QHBoxLayout(self)

        self.file_label = LeftEllipsisLabel(filepath)
        self.layout.addWidget(self.file_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)  # Example progress value
        self.layout.addWidget(self.progress_bar)

        self.check_label = QLabel("✓")
        self.layout.addWidget(self.check_label)

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def update_filepath(self, filepath):
        self.file_label.setText(filepath)

    def set_check_visible(self, visible):
        self.check_label.setVisible(visible)