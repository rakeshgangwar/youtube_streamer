import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QThread, pyqtSignal
import configparser
from streamer import start_streaming


class StreamerThread(QThread):
    update_signal = pyqtSignal(str)

    def run(self):
        try:
            start_streaming()
        except Exception as e:
            self.update_signal.emit(f"Error: {str(e)}")


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'YouTube Streamer'
        self.left = 10
        self.top = 10
        self.width = 320
        self.height = 200
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        layout = QVBoxLayout()

        self.label = QLabel('YouTube Streamer')
        layout.addWidget(self.label)

        self.button = QPushButton('Start Streaming')
        self.button.clicked.connect(self.start_streaming)
        layout.addWidget(self.button)

        self.setLayout(layout)
        self.show()

    def start_streaming(self):
        self.streamer_thread = StreamerThread()
        self.streamer_thread.update_signal.connect(self.update_label)
        self.streamer_thread.start()
        self.button.setEnabled(False)

    def update_label(self, message):
        self.label.setText(message)
        self.button.setEnabled(True)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())