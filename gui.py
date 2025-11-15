"""
YouTube Streamer Desktop GUI

This module provides a PyQt5-based desktop GUI for the YouTube Streamer.

NOTE: This is a legacy component. The main application now uses a web-based
interface (app.py). This GUI is kept for backward compatibility but may not
be fully functional with the current streaming implementation.
"""

import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QThread, pyqtSignal
import configparser
from streamer import start_streaming


class StreamerThread(QThread):
    """
    Worker thread for running streaming operations.

    Runs the FFmpeg streaming process in a separate thread to prevent
    blocking the GUI. Emits signals to update the UI.

    Attributes:
        update_signal (pyqtSignal): Signal emitted with status messages
    """
    update_signal = pyqtSignal(str)

    def run(self):
        """
        Execute the streaming operation.

        NOTE: This calls start_streaming() without parameters, which is
        incompatible with the current implementation that requires
        stream_config parameter.
        """
        try:
            start_streaming()
        except Exception as e:
            self.update_signal.emit(f"Error: {str(e)}")


class App(QWidget):
    """
    Main application window for the YouTube Streamer desktop GUI.

    Provides a simple interface with a start button and status label.
    """

    def __init__(self):
        """
        Initialize the application window.

        Sets up window properties and initializes the UI components.
        """
        super().__init__()
        self.title = 'YouTube Streamer'
        self.left = 10
        self.top = 10
        self.width = 320
        self.height = 200
        self.initUI()

    def initUI(self):
        """
        Initialize the user interface.

        Creates and arranges UI components including the title label
        and start streaming button.
        """
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
        """
        Start the streaming process in a background thread.

        Creates a StreamerThread and connects its signals to update
        the UI. Disables the button while streaming.
        """
        self.streamer_thread = StreamerThread()
        self.streamer_thread.update_signal.connect(self.update_label)
        self.streamer_thread.start()
        self.button.setEnabled(False)

    def update_label(self, message: str):
        """
        Update the status label with a message.

        Args:
            message (str): Status message to display
        """
        self.label.setText(message)
        self.button.setEnabled(True)


if __name__ == '__main__':
    """
    Application entry point.

    Creates the Qt application and main window, then starts the event loop.
    """
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())