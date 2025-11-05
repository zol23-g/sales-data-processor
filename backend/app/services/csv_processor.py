import csv
from datetime import datetime
import io
import uuid
from typing import Dict, Generator, List, Optional, Tuple, AsyncGenerator
import time
import asyncio

from app.models.sales_data import SalesRecord, DepartmentSales, ProcessingResult, JobStatus
from app.core.logger import get_logger


class CSVProcessor:
    """Streaming CSV processor for large files."""
    
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
    
    async def process_csv_stream_async(
        self, 
        file_stream: AsyncGenerator[bytes, None],
        chunk_size: int = 8192
    ) -> ProcessingResult:
        """
        Process CSV data stream asynchronously with memory efficiency.
        
        Time Complexity: O(n) where n is number of rows
        Space Complexity: O(k) where k is number of unique departments
        """
        job_id = str(uuid.uuid4())
        start_time = time.time()
        
        # Use dictionary for O(1) department lookups
        departments: Dict[str, DepartmentSales] = {}
        total_rows = 0
        valid_rows = 0
        
        # Create a text buffer for incomplete lines
        text_buffer = ""
        
        try:
            async for chunk in file_stream:
                if not chunk:
                    continue
                    
                # Decode chunk and add to buffer
                text_buffer += chunk.decode('utf-8')
                
                # Process complete lines from buffer
                lines = text_buffer.split('\n')
                text_buffer = lines[-1]  # Keep incomplete line in buffer
                
                # Process complete lines
                for line in lines[:-1]:
                    total_rows += 1
                    record = self._parse_csv_line(line.strip())
                    
                    if record:
                        valid_rows += 1
                        self._update_department_sales(departments, record)
            
            # Process remaining buffer
            if text_buffer.strip():
                total_rows += 1
                record = self._parse_csv_line(text_buffer.strip())
                if record:
                    valid_rows += 1
                    self._update_department_sales(departments, record)
        
        except Exception as e:
            self.logger.error("Error processing CSV stream", error=str(e), job_id=job_id)
            raise
        
        processing_time = time.time() - start_time
        
        self.logger.info(
            "CSV processing completed",
            job_id=job_id,
            total_rows=total_rows,
            valid_rows=valid_rows,
            unique_departments=len(departments),
            processing_time=processing_time
        )
        
        return ProcessingResult(
            job_id=job_id,
            departments=departments,
            total_rows=total_rows,
            valid_rows=valid_rows,
            processing_time=processing_time
        )
    
    def process_csv_stream(
        self, 
        file_stream: Generator[bytes, None, None],
        chunk_size: int = 8192
    ) -> ProcessingResult:
        """
        Process CSV data stream synchronously with memory efficiency.
        """
        job_id = str(uuid.uuid4())
        start_time = time.time()
        
        departments: Dict[str, DepartmentSales] = {}
        total_rows = 0
        valid_rows = 0
        text_buffer = ""
        
        try:
            for chunk in file_stream:
                if not chunk:
                    continue
                    
                text_buffer += chunk.decode('utf-8')
                lines = text_buffer.split('\n')
                text_buffer = lines[-1]
                
                for line in lines[:-1]:
                    total_rows += 1
                    record = self._parse_csv_line(line.strip())
                    
                    if record:
                        valid_rows += 1
                        self._update_department_sales(departments, record)
            
            if text_buffer.strip():
                total_rows += 1
                record = self._parse_csv_line(text_buffer.strip())
                if record:
                    valid_rows += 1
                    self._update_department_sales(departments, record)
        
        except Exception as e:
            self.logger.error("Error processing CSV stream", error=str(e), job_id=job_id)
            raise
        
        processing_time = time.time() - start_time
        
        self.logger.info(
            "CSV processing completed",
            job_id=job_id,
            total_rows=total_rows,
            valid_rows=valid_rows,
            unique_departments=len(departments),
            processing_time=processing_time
        )
        
        return ProcessingResult(
            job_id=job_id,
            departments=departments,
            total_rows=total_rows,
            valid_rows=valid_rows,
            processing_time=processing_time
        )
    
    def _parse_csv_line(self, line: str) -> Optional[SalesRecord]:
        """Parse a single CSV line into SalesRecord with strict validation."""
        try:
            # Skip empty lines and header
            if not line or line.startswith('Department Name'):
                return None
            
            # Use CSV reader to handle quoted fields and commas within fields
            reader = csv.reader(io.StringIO(line))
            parts = next(reader)
            
            # Must have exactly 3 columns
            if len(parts) != 3:
                return None
            
            department = parts[0].strip()
            date_str = parts[1].strip()
            sales_str = parts[2].strip()
            
            # Validate department name
            if not department:
                return None
            
            # Validate date format (YYYY-MM-DD)
            try:
                datetime.strptime(date_str, '%Y-%m-%d')
            except ValueError:
                return None
            
            # Validate sales number
            try:
                sales = int(sales_str)
                if sales < 0:  # Sales cannot be negative
                    return None
            except ValueError:
                return None
            
            return SalesRecord(
                department=department,
                date=date_str,
                sales=sales
            )
            
        except Exception as e:
            self.logger.debug("Failed to parse CSV line", line=line, error=str(e))
            return None
    
    def _update_department_sales(
        self, 
        departments: Dict[str, DepartmentSales], 
        record: SalesRecord
    ) -> None:
        """Update department sales aggregation."""
        if record.department not in departments:
            departments[record.department] = DepartmentSales(department=record.department)
        
        departments[record.department].add_sales(record.sales)
    
    def write_results_to_csv(self, result: ProcessingResult, output_path: str) -> None:
        """Write processing results to CSV file."""
        try:
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerows(result.to_csv_rows())
            
            self.logger.info("Results written to CSV", output_path=output_path, job_id=result.job_id)
        except Exception as e:
            self.logger.error("Failed to write results CSV", error=str(e), job_id=result.job_id)
            raise