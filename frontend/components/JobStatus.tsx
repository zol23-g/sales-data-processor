'use client'

import { useState, useEffect } from 'react'
import { Download, Clock, CheckCircle, XCircle, RefreshCw } from 'lucide-react'
import { apiRoutes, ApiError } from '@/lib/api/apiRoutes'
import { JobStatusResponse, LoadingState } from '@/types'
import type { JobStatus } from '@/types'

interface JobStatusProps {
  jobId: string
}

export default function JobStatus({ jobId }: JobStatusProps) {
  const [jobStatus, setJobStatus] = useState<JobStatusResponse | null>(null)
  const [loadingState, setLoadingState] = useState<LoadingState>({
    isLoading: true,
    isSuccess: false,
    isError: false,
  })

  const fetchJobStatus = async () => {
    try {
      const data = await apiRoutes.getJobStatus(jobId)
      setJobStatus(data)
      setLoadingState({
        isLoading: false,
        isSuccess: true,
        isError: false,
      })
    } catch (err) {
      console.error('Failed to fetch job status:', err)
      const errorMessage = err instanceof ApiError 
        ? `Failed to load job status: ${err.statusText}`
        : 'Failed to load job status'
      
      setLoadingState({
        isLoading: false,
        isSuccess: false,
        isError: true,
        error: errorMessage,
      })
    }
  }

  useEffect(() => {
    fetchJobStatus()
    
    // Poll for status updates if job is in progress
    if (jobStatus && apiRoutes.isJobInProgress(jobStatus.status)) {
      const interval = setInterval(fetchJobStatus, 2000)
      return () => clearInterval(interval)
    }
  }, [jobId, jobStatus?.status])

  const getStatusIcon = (status: JobStatus) => {
    switch (status) {
      case 'pending':
        return <Clock className="h-6 w-6 text-yellow-500" />
      case 'processing':
        return <RefreshCw className="h-6 w-6 text-blue-500 animate-spin" />
      case 'completed':
        return <CheckCircle className="h-6 w-6 text-green-500" />
      case 'failed':
        return <XCircle className="h-6 w-6 text-red-500" />
      default:
        return <Clock className="h-6 w-6 text-gray-500" />
    }
  }

  const getStatusColor = (status: JobStatus) => {
    switch (status) {
      case 'pending':
        return 'bg-yellow-50 border-yellow-200'
      case 'processing':
        return 'bg-blue-50 border-blue-200'
      case 'completed':
        return 'bg-green-50 border-green-200'
      case 'failed':
        return 'bg-red-50 border-red-200'
      default:
        return 'bg-gray-50 border-gray-200'
    }
  }

  const getStatusMessage = (status: JobStatus) => {
    switch (status) {
      case 'pending':
        return 'Waiting to start processing...'
      case 'processing':
        return 'Processing your file...'
      case 'completed':
        return 'Processing completed successfully!'
      case 'failed':
        return 'Processing failed. Please try again.'
      default:
        return 'Unknown status'
    }
  }

  if (loadingState.isLoading) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="h-8 bg-gray-200 rounded w-3/4"></div>
        </div>
      </div>
    )
  }

  if (loadingState.isError) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="text-center text-red-600">
          {loadingState.error}
        </div>
      </div>
    )
  }

  if (!jobStatus) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="text-center text-gray-500">
          Failed to load job status
        </div>
      </div>
    )
  }

  return (
    <div className={`bg-white rounded-lg shadow-lg p-6 border-2 ${getStatusColor(jobStatus.status)}`}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xl font-semibold text-gray-900">
          Processing Status
        </h3>
        <div className="flex items-center space-x-2">
          {getStatusIcon(jobStatus.status)}
          <span className="text-sm font-medium capitalize">
            {jobStatus.status}
          </span>
        </div>
      </div>

      <div className="space-y-4">
        <div>
          <p className="text-sm text-gray-600 mb-2">Job ID: {jobStatus.job_id}</p>
          <p className="text-gray-700">{getStatusMessage(jobStatus.status)}</p>
          {jobStatus.environment && (
            <p className="text-xs text-gray-500 mt-1">
              Environment: {jobStatus.environment}
            </p>
          )}
        </div>

        {apiRoutes.isJobInProgress(jobStatus.status) && (
          <div>
            <div className="flex justify-between text-sm text-gray-600 mb-1">
              <span>Progress</span>
              <span>{jobStatus.progress}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${jobStatus.progress}%` }}
              ></div>
            </div>
          </div>
        )}

        {jobStatus.status === 'completed' && jobStatus.download_url && (
          <div className="flex justify-end">
            <a
              href={apiRoutes.getDownloadUrl(jobStatus.download_url.split('/').pop() || '')}
              download
              className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
            >
              <Download className="h-4 w-4" />
              <span>Download Results</span>
            </a>
          </div>
        )}

        {jobStatus.status === 'failed' && (
          <div className="p-3 bg-red-100 rounded-lg">
            <p className="text-red-700 text-sm">
              {jobStatus.message || 'Processing failed. Please try again or contact support.'}
            </p>
          </div>
        )}
      </div>
    </div>
  )
}