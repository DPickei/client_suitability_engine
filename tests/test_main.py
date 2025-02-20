import pytest
from src import main
from pathlib import Path

def test_main(json_folderpath):
    """Test that main runs without errors using test data"""
    main.main(json_folderpath)
    assert True  # If we get here, main() completed without raising exceptions

def test_setup():
    """Test that setup returns a valid Path object"""
    result = main.setup()
    assert isinstance(result, Path)
    assert result.exists()  # Verify the path exists