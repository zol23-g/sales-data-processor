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
    
    @pytest.fixture
    def sample_csv_with_empty_lines(self):
        return """Department Name,Date,Number of Sales

Electronics,2023-08-01,100

Clothing,2023-08-01,200

Electronics,2023-08-02,150

Clothing,2023-08-02,50
"""
    
    @pytest.fixture
    def sample_csv_with_invalid_data(self):
        return """Department Name,Date,Number of Sales
Electronics,2023-08-01,100
Invalid Department,2023-13-01,-50
Electronics,invalid_date,abc
Clothing,2023-08-01,200
,2023-08-01,100
Electronics,2023-08-02,
"""
    
    def test_parse_csv_line_valid(self, processor):
        line = "Electronics,2023-08-01,100"
        record = processor._parse_csv_line(line)
        
        assert record is not None
        assert record.department == "Electronics"
        assert record.date == "2023-08-01"
        assert record.sales == 100
    
    def test_parse_csv_line_header(self, processor):
        # Test header line should be ignored
        line = "Department Name,Date,Number of Sales"
        record = processor._parse_csv_line(line)
        assert record is None
    
    def test_parse_csv_line_empty(self, processor):
        # Test empty line should be ignored
        line = ""
        record = processor._parse_csv_line(line)
        assert record is None
    
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
        
        # Test extra columns
        line = "Electronics,2023-08-01,100,extra"
        record = processor._parse_csv_line(line)
        assert record is None
        
        # Test non-numeric sales
        line = "Electronics,2023-08-01,abc"
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
        
        # The processor counts all rows (including header) in total_rows
        # but only valid data rows in valid_rows
        assert result.total_rows == 5  # Header + 4 data rows
        assert result.valid_rows == 4  # Only the 4 valid data rows
        assert len(result.departments) == 2
        assert result.departments["Electronics"].total_sales == 250
        assert result.departments["Clothing"].total_sales == 250
    
    def test_process_csv_stream_with_empty_lines(self, processor, sample_csv_with_empty_lines):
        def chunk_generator():
            data = sample_csv_with_empty_lines.encode('utf-8')
            yield data
        
        result = processor.process_csv_stream(chunk_generator())
        
        # Should ignore empty lines and only count valid rows
        assert result.valid_rows == 4
        assert len(result.departments) == 2
        assert result.departments["Electronics"].total_sales == 250
        assert result.departments["Clothing"].total_sales == 250
    
    def test_process_csv_stream_with_invalid_data(self, processor, sample_csv_with_invalid_data):
        def chunk_generator():
            data = sample_csv_with_invalid_data.encode('utf-8')
            yield data
        
        result = processor.process_csv_stream(chunk_generator())
        
        # Should only process valid rows and ignore invalid ones
        assert result.valid_rows == 2  # Only 2 valid rows out of the data
        assert len(result.departments) == 2
        assert result.departments["Electronics"].total_sales == 100
        assert result.departments["Clothing"].total_sales == 200
    
    def test_process_csv_stream_empty_file(self, processor):
        def chunk_generator():
            yield b""
        
        result = processor.process_csv_stream(chunk_generator())
        
        assert result.total_rows == 0
        assert result.valid_rows == 0
        assert len(result.departments) == 0
    
    def test_update_department_sales(self, processor):
        departments = {}
        record1 = SalesRecord("Electronics", "2023-08-01", 100)
        record2 = SalesRecord("Electronics", "2023-08-02", 150)
        record3 = SalesRecord("Clothing", "2023-08-01", 200)
        
        processor._update_department_sales(departments, record1)
        processor._update_department_sales(departments, record2)
        processor._update_department_sales(departments, record3)
        
        assert "Electronics" in departments
        assert "Clothing" in departments
        assert departments["Electronics"].total_sales == 250
        assert departments["Clothing"].total_sales == 200
    
    def test_update_department_sales_new_department(self, processor):
        departments = {}
        record = SalesRecord("New Department", "2023-08-01", 300)
        
        processor._update_department_sales(departments, record)
        
        assert "New Department" in departments
        assert departments["New Department"].total_sales == 300