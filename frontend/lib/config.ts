// API Configuration
export const API_CONFIG = {
  baseUrl: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000',
  environment: process.env.NEXT_PUBLIC_APP_ENVIRONMENT || 'development',
  timeout: 30000, // 30 seconds
} as const;

// API Endpoints
export const API_ENDPOINTS = {
  upload: '/api/upload',
  jobStatus: (jobId: string) => `/api/job/${jobId}`,
  download: (filename: string) => `/api/download/${filename}`,
  health: '/health',
} as const;