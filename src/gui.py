from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import QWidget, QApplication, QSystemTrayIcon, QMenu, QVBoxLayout, QLabel


class TopRightWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Top Right Window")
        self.setWindowIcon(QIcon("../resources/foaf.png"))  # Replace with your icon path
        self.setFixedSize(200, 100)  # Set the size of the window

        # Center the content inside the window
        layout = QVBoxLayout()
        label = QLabel("This is a small window")
        layout.addWidget(label)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(layout)

        self.move_to_top_right()

    def move_to_top_right(self):
        # Get the screen geometry
        screen_geometry = QApplication.primaryScreen().geometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        # Get the window geometry
        window_width = self.frameGeometry().width()
        window_height = self.frameGeometry().height()

        # Calculate the top-right position
        x = screen_width - window_width
        y = 0

        # Move the window to the top-right corner
        self.move(x, y)


class Gui:
    def __init__(self):
        self.app: QApplication = QApplication([])
        self.quit: QAction = None
        self.tray: QSystemTrayIcon = None
        self.menu: QMenu = None
        self.top_right_window: TopRightWindow = None

    def setup(self):
        self.app.setQuitOnLastWindowClosed(False)

        # Create the tray
        self.tray = QSystemTrayIcon()
        self.tray.setIcon(QIcon("../resources/foaf.png"))
        self.tray.setVisible(True)

        # Create the menu
        self.menu = QMenu()
        action = QAction("A menu item")
        self.menu.addAction(action)

        # Add a Quit option to the menu.
        self.quit = QAction("Quit")
        self.quit.triggered.connect(self.app.quit)
        self.menu.addAction(self.quit)

        # Add the menu to the tray
        self.tray.setContextMenu(self.menu)

        self.top_right_window = TopRightWindow()

    def show_notification(self, title, message):
        self.tray.showMessage(title, message, QSystemTrayIcon.MessageIcon.Information, 5000)

    def show_top_right_window(self):
        self.top_right_window.show()

    def run(self):
        return self.app.exec()
