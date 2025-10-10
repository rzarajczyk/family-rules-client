#!/usr/bin/env python3
"""
Test script for enhanced fullscreen blocking functionality on macOS.
This script helps verify that the BlockScreenWindow can appear over fullscreen applications.
"""

import sys
import os
import time
import logging

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from gui_block import BlockScreenWindow
from osutils import get_os, SupportedOs

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_fullscreen_blocking():
    """Test the enhanced fullscreen blocking functionality"""
    
    if get_os() != SupportedOs.MAC_OS:
        print("This test is designed for macOS only.")
        return
    
    print("Testing enhanced fullscreen blocking functionality...")
    print("Instructions:")
    print("1. Start a fullscreen application (e.g., YouTube in Safari, or any game)")
    print("2. Run this test script")
    print("3. The blocking window should appear over the fullscreen app")
    print("4. The test will automatically end after 5 seconds")
    print()
    
    # Create Qt application
    app = QApplication(sys.argv)
    
    # Create blocking window
    block_window = BlockScreenWindow()
    
    print("Blocking window created. Showing in 3 seconds...")
    time.sleep(3)
    
    # Show the blocking window
    block_window.show()
    print("Blocking window is now visible. It should appear over any fullscreen applications.")
    print("Test will automatically end in 5 seconds...")
    
    # Create a timer to automatically close the test after 5 seconds
    def close_test():
        print("\nTest completed automatically after 5 seconds.")
        block_window.hide()
        app.quit()
    
    timer = QTimer()
    timer.timeout.connect(close_test)
    timer.setSingleShot(True)
    timer.start(10000)  # 5 seconds
    
    try:
        # Keep the application running
        app.exec()
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
        block_window.hide()
    finally:
        print("Test cleanup completed.")

if __name__ == "__main__":
    test_fullscreen_blocking()