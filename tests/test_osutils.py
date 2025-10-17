"""
Tests for osutils.py module.
"""

import pytest
import os

# Import from src (path setup handled in conftest.py)
from Basedir import Basedir
from osutils import app_version, get_os, OperatingSystem

# Initialize Basedir for tests
Basedir.init(os.path.join(os.path.dirname(__file__), "..", "src"))


def test_app_version():
    """Test that app_version returns a reasonable version string."""
    version = app_version()
    
    # Should return a string
    assert isinstance(version, str)
    
    # Should not be empty
    assert len(version.strip()) > 0
    
    # Should contain version-like content (starts with 'v' and has numbers)
    assert version.strip().startswith('v')
    
    # Should have some numeric content
    assert any(char.isdigit() for char in version)
    
    # Should be a reasonable length (not too short, not too long)
    assert 3 <= len(version.strip()) <= 20


def test_get_os():
    """Test that get_os returns a valid OperatingSystem enum."""
    os_type = get_os()
    
    # Should return an OperatingSystem enum
    assert isinstance(os_type, OperatingSystem)
    
    # Should be one of the expected values
    assert os_type in [OperatingSystem.MAC_OS, OperatingSystem.WINDOWS, OperatingSystem.OTHER]


def test_app_version_content():
    """Test specific content of app_version."""
    version = app_version().strip()
    
    # Based on the version.txt file, should be "v0.98"
    assert version == "v0.98"


if __name__ == "__main__":
    pytest.main([__file__])
