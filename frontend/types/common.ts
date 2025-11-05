// Common utility types
export type Optional<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;
export type Required<T, K extends keyof T> = T & Required<Pick<T, K>>;

// Component props types
export interface ComponentBaseProps {
  className?: string;
  children?: React.ReactNode;
  'data-testid'?: string;
}

// Form types
export interface FormState {
  isSubmitting: boolean;
  isSubmitted: boolean;
  error?: string;
  success?: boolean;
}

// File types
export interface FileValidationResult {
  isValid: boolean;
  error?: string;
}

export interface FileInfo {
  name: string;
  size: number;
  type: string;
  lastModified: number;
}

// Job types
export interface JobInfo {
  id: string;
  status: JobStatus;
  created_at: string;
  updated_at: string;
  result_file?: string;
}

// UI state types
export interface LoadingState {
  isLoading: boolean;
  isSuccess: boolean;
  isError: boolean;
  error?: string;
}

export interface PollingState {
  isPolling: boolean;
  interval: number;
  maxAttempts: number;
  currentAttempt: number;
}