import logging
import os
import sys
import traceback

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt

from Installer import Installer
from Reporter import Reporter
from Settings import Settings
from UptimeDb import AbsoluteUsage
from gui import Gui
from StateController import (StateController)
from osutils import app_data, path_to_str
from basedir import Basedir
from osutils import make_sure_only_one_instance_is_running
from guiutils import set_grayscale
from uptime import PsUptime

TICK_INTERVAL_SECONDS = 5
REPORT_INTERVALS_TICK = 4
DEBUG_HTTP_REQUESTS = False

Basedir.init(os.path.dirname(__file__))

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(path_to_str(app_data() / "output.log")),
        logging.StreamHandler(sys.stdout)
    ]
)

if DEBUG_HTTP_REQUESTS:
    import http.client as http_client

    http_client.HTTPConnection.debuglevel = 1
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True

state_controller = StateController()
reporter = Reporter()


def global_exception_handler(exc_type, exc_value, exc_traceback):
    """
    Global exception handler that shows a message box and quits the application.
    This handles any unhandled exceptions that occur in the main thread.
    """
    if issubclass(exc_type, KeyboardInterrupt):
        # Allow KeyboardInterrupt to be handled normally
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    # Log the exception
    logging.critical("Unhandled exception occurred", exc_info=(exc_type, exc_value, exc_traceback))
    
    # Create a message box to show the error
    try:
        # Try to create a QApplication if one doesn't exist
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # Create error message
        error_msg = f"An unexpected error occurred:\n\n{exc_type.__name__}: {exc_value}"
        
        # Add traceback details for debugging
        traceback_str = ''.join(traceback.format_tb(exc_traceback))
        error_msg += f"\n\nTraceback:\n{traceback_str}"
        
        # Show message box
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Application Error")
        msg_box.setText("The application encountered an unexpected error and will now close.")
        msg_box.setDetailedText(error_msg)
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()
        
    except Exception as e:
        # If we can't show a GUI message box, at least log it
        logging.critical(f"Failed to show error dialog: {e}")
        print(f"CRITICAL ERROR: {exc_type.__name__}: {exc_value}")
        print("Traceback:")
        traceback.print_tb(exc_traceback)
    
    # Force exit the application
    sys.exit(1)


def uptime_tick():
    return PsUptime(TICK_INTERVAL_SECONDS).get()


def report_tick(gui: Gui, usage: AbsoluteUsage, first_run: bool):
    state = reporter.submit_report_get_state(usage)
    state_controller.run(state, first_run)


if __name__ == "__main__":
    sys.excepthook = global_exception_handler

    
    logging.info("App started!")
    make_sure_only_one_instance_is_running()
    set_grayscale(False)
    gui = Gui(sys.argv)
    state_controller.initialize(gui)

    if not Settings.setup_completed():
        gui.setup_initial_setup_ui()
    else:
        Installer.install_autorun()
        gui.setup_main_ui(
            uptime_tick_interval_ms=TICK_INTERVAL_SECONDS * 1000,
            uptime_tick_function=uptime_tick,
            report_tick_interval_ms=TICK_INTERVAL_SECONDS * REPORT_INTERVALS_TICK * 1000,
            report_tick_function=report_tick
        )
    sys.exit(gui.run())
