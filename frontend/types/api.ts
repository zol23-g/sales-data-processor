// Base API response interface
export interface BaseApiResponse {
  environment?: string;
  timestamp?: string;
}

// Upload related types
export interface UploadResponse extends BaseApiResponse {
  job_id: string;
  status: string;
  message: string;
}

// Job status related types
export type JobStatus = 'pending' | 'processing' | 'completed' | 'failed';

export interface JobStatusResponse extends BaseApiResponse {
  job_id: string;
  status: JobStatus;
  message: string;
  progress: number;
  download_url?: string;
}

// Health check types
export interface HealthResponse extends BaseApiResponse {
  status: string;
  environment: string;
  timestamp: string;
}

// Error types
export interface ApiErrorResponse {
  error: string;
  message: string;
  status_code: number;
  details?: any;
}

// File upload types
export interface FileUploadProgress {
  loaded: number;
  total: number;
  percentage: number;
}

// Pagination types (future use)
export interface PaginationParams {
  page?: number;
  limit?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface PaginatedResponse<T> {
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    total_pages: number;
    has_next: boolean;
    has_prev: boolean;
  };
}