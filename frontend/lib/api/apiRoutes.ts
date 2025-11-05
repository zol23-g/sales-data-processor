import { apiClient, ApiError } from './apiClient';
import { API_CONFIG, API_ENDPOINTS } from '../config';
import {
  UploadResponse,
  JobStatusResponse,
  HealthResponse,
  JobStatus,
} from '../../types';

// API Service
export const apiRoutes = {
  // Upload CSV file
  async uploadFile(file: File): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    return apiClient.postFormData<UploadResponse>(API_ENDPOINTS.upload, formData);
  },

  // Get job status
  async getJobStatus(jobId: string): Promise<JobStatusResponse> {
    return apiClient.get<JobStatusResponse>(API_ENDPOINTS.jobStatus(jobId));
  },

  // Get download URL
  getDownloadUrl(filename: string): string {
    return `${API_CONFIG.baseUrl}${API_ENDPOINTS.download(filename)}`;
  },

  // Health check
  async healthCheck(): Promise<HealthResponse> {
    return apiClient.get<HealthResponse>(API_ENDPOINTS.health);
  },

  // Utility function to check if job is complete
  isJobComplete(status: JobStatus): boolean {
    return status === 'completed' || status === 'failed';
  },

  // Utility function to check if job is in progress
  isJobInProgress(status: JobStatus): boolean {
    return status === 'pending' || status === 'processing';
  },
};

// Export types for use in components
export type { ApiError };