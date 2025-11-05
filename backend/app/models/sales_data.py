from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import uuid


@dataclass
class SalesRecord:
    """Represents a single sales record from CSV."""
    department: str
    date: str
    sales: int
    
    @classmethod
    def from_csv_row(cls, row: List[str]) -> Optional['SalesRecord']:
        """Create SalesRecord from CSV row with validation."""
        if len(row) != 3:
            return None
        
        try:
            department = row[0].strip()
            date = row[1].strip()
            sales = int(row[2].strip())
            
            # Validate sales is positive
            if sales < 0:
                return None
                
            # Basic date validation (ISO format)
            datetime.strptime(date, '%Y-%m-%d')
            
            return cls(department=department, date=date, sales=sales)
        except (ValueError, IndexError):
            return None


@dataclass
class DepartmentSales:
    """Aggregated sales data for a department."""
    department: str
    total_sales: int = 0
    
    def add_sales(self, sales: int) -> None:
        """Add sales to the department total."""
        self.total_sales += sales


@dataclass
class ProcessingResult:
    """Result of CSV processing."""
    job_id: str
    departments: Dict[str, DepartmentSales]
    total_rows: int
    valid_rows: int
    processing_time: float
    
    def to_csv_rows(self) -> List[List[str]]:
        """Convert result to CSV rows."""
        rows = [["Department Name", "Total Number of Sales"]]
        for dept_sales in sorted(self.departments.values(), key=lambda x: x.department):
            rows.append([dept_sales.department, str(dept_sales.total_sales)])
        return rows


@dataclass
class JobStatus:
    """Track processing job status."""
    
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    
    def __init__(self, job_id: str):
        self.job_id = job_id
        self.status = self.PENDING
        self.message = "Job created"
        self.progress = 0
        self.total_rows = 0
        self.processed_rows = 0
        self.result_file: Optional[str] = None
        self.error: Optional[str] = None
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
    
    def start_processing(self) -> None:
        """Mark job as started only if it's pending."""
        if self.status == self.PENDING:
            self.status = self.PROCESSING
            self.start_time = datetime.now().timestamp()
            self.message = "Processing started"
    
    def update_progress(self, processed: int, total: int) -> None:
        """Update processing progress."""
        self.processed_rows = processed
        self.total_rows = total
        if total > 0:
            self.progress = int((processed / total) * 100)
    
    def complete(self, result_file: str) -> None:
        """Mark job as completed."""
        self.status = self.COMPLETED
        self.result_file = result_file
        self.progress = 100
        self.end_time = datetime.now().timestamp()
        self.message = "Processing completed successfully"
    
    def fail(self, error: str) -> None:
        """Mark job as failed."""
        self.status = self.FAILED
        self.error = error
        self.end_time = datetime.now().timestamp()
        self.message = f"Processing failed: {error}"