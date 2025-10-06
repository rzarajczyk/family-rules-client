import logging
import sys
import traceback

from PySide6.QtWidgets import QApplication, QMessageBox

from translations import tr


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
        error_msg = f"{tr('An unexpected error occurred:')}\n\n{exc_type.__name__}: {exc_value}"

        # Add traceback details for debugging
        traceback_str = ''.join(traceback.format_tb(exc_traceback))
        error_msg += f"\n\n{tr('Traceback:')}\n{traceback_str}"

        # Show message box
        msg_box = QMessageBox()
        msg_box.setWindowTitle(tr("Application Error"))
        msg_box.setText(tr("The application encountered an unexpected error and will now close."))
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

