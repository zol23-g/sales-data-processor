import pytest
import io
from app.services.csv_processor import CSVProcessor
from app.models.sales_data import SalesRecord


class TestCSVProcessor:
    
    @pytest.fixture
    def processor(self):
        return CSVProcessor()
    
    @pytest.fixture
    def sample_csv_data(self):
        return """Department Name,Date,Number of Sales
Electronics,2023-08-01,100
Clothing,2023-08-01,200
Electronics,2023-08-02,150
Clothing,2023-08-02,50"""
    
    def test_parse_csv_line_valid(self, processor):
        line = "Electronics,2023-08-01,100"
        record = processor._parse_csv_line(line)
        
        assert record is not None
        assert record.department == "Electronics"
        assert record.date == "2023-08-01"
        assert record.sales == 100
    
    def test_parse_csv_line_invalid(self, processor):
        # Test invalid sales number
        line = "Electronics,2023-08-01,-100"
        record = processor._parse_csv_line(line)
        assert record is None
        
        # Test invalid date format
        line = "Electronics,2023/08/01,100"
        record = processor._parse_csv_line(line)
        assert record is None
        
        # Test missing columns
        line = "Electronics,2023-08-01"
        record = processor._parse_csv_line(line)
        assert record is None
    
    def test_process_csv_stream(self, processor, sample_csv_data):
        def chunk_generator():
            # Split data into chunks to simulate streaming
            chunk_size = 20
            data = sample_csv_data.encode('utf-8')
            for i in range(0, len(data), chunk_size):
                yield data[i:i + chunk_size]
        
        result = processor.process_csv_stream(chunk_generator())
        
        assert result.total_rows == 4
        assert result.valid_rows == 4
        assert len(result.departments) == 2
        assert result.departments["Electronics"].total_sales == 250
        assert result.departments["Clothing"].total_sales == 250
    
    def test_update_department_sales(self, processor):
        departments = {}
        record1 = SalesRecord("Electronics", "2023-08-01", 100)
        record2 = SalesRecord("Electronics", "2023-08-02", 150)
        
        processor._update_department_sales(departments, record1)
        processor._update_department_sales(departments, record2)
        
        assert "Electronics" in departments
        assert departments["Electronics"].total_sales == 250