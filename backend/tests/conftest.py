import pytest
import tempfile
import os
from app.core.config import TestingSettings


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment."""
    os.environ["ENVIRONMENT"] = "testing"


@pytest.fixture
def temp_csv_file():
    """Create temporary CSV file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write("""Department Name,Date,Number of Sales
Electronics,2023-08-01,100
Clothing,2023-08-01,200
Electronics,2023-08-02,150""")
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    if os.path.exists(temp_path):
        os.remove(temp_path)