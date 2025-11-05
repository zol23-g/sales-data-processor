'use client'

import { useState, useCallback } from 'react'
import { Upload, FileText, AlertCircle } from 'lucide-react'
import { apiRoutes, ApiError } from '@/lib/api/apiRoutes'
import { FileValidationResult, FileInfo, FormState } from '@/types'

interface FileUploadProps {
  onJobCreated: (jobId: string) => void
}

export default function FileUpload({ onJobCreated }: FileUploadProps) {
  const [isDragging, setIsDragging] = useState(false)
  const [formState, setFormState] = useState<FormState>({
    isSubmitting: false,
    isSubmitted: false,
  })
  const [selectedFile, setSelectedFile] = useState<FileInfo | null>(null)

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }, [])

  const validateFile = (file: File): FileValidationResult => {
    if (!file.name.endsWith('.csv')) {
      return { isValid: false, error: 'Please upload a CSV file' }
    }
    if (file.size > 100 * 1024 * 1024) { // 100MB
      return { isValid: false, error: 'File size must be less than 100MB' }
    }
    return { isValid: true }
  }

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    setFormState(prev => ({ ...prev, error: undefined }))

    const files = Array.from(e.dataTransfer.files)
    if (files.length > 0) {
      const file = files[0]
      const validation = validateFile(file)
      if (!validation.isValid) {
        setFormState(prev => ({ ...prev, error: validation.error }))
      } else {
        setSelectedFile({
          name: file.name,
          size: file.size,
          type: file.type,
          lastModified: file.lastModified,
        })
      }
    }
  }, [])

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setFormState(prev => ({ ...prev, error: undefined }))
    const files = e.target.files
    if (files && files.length > 0) {
      const file = files[0]
      const validation = validateFile(file)
      if (!validation.isValid) {
        setFormState(prev => ({ ...prev, error: validation.error }))
      } else {
        setSelectedFile({
          name: file.name,
          size: file.size,
          type: file.type,
          lastModified: file.lastModified,
        })
      }
    }
  }, [])

  const handleUpload = async () => {
    if (!selectedFile) return

    setFormState({ isSubmitting: true, isSubmitted: false })

    try {
      const fileInput = document.getElementById('file-upload') as HTMLInputElement
      const file = fileInput?.files?.[0]
      
      if (!file) {
        throw new Error('No file selected')
      }

      const result = await apiRoutes.uploadFile(file)
      onJobCreated(result.job_id)
      setFormState({ isSubmitting: false, isSubmitted: true, success: true })
      
    } catch (err) {
      const errorMessage = err instanceof ApiError 
        ? `Upload failed: ${err.statusText} (${err.status})`
        : err instanceof Error ? err.message : 'Upload failed'
      
      setFormState({
        isSubmitting: false,
        isSubmitted: true,
        error: errorMessage,
        success: false,
      })
    }
  }

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-semibold text-gray-900 mb-4">
        Upload CSV File
      </h2>

      <div
        className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
          isDragging
            ? 'border-blue-500 bg-blue-50'
            : 'border-gray-300 hover:border-gray-400'
        }`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <input
          type="file"
          id="file-upload"
          className="hidden"
          accept=".csv"
          onChange={handleFileSelect}
          disabled={formState.isSubmitting}
        />

        <div className="flex flex-col items-center justify-center space-y-4">
          <Upload className="h-12 w-12 text-gray-400" />
          
          <div className="text-lg text-gray-600">
            <label
              htmlFor="file-upload"
              className="cursor-pointer text-blue-600 hover:text-blue-500 font-medium"
            >
              Click to upload
            </label>
            {' '}or drag and drop
          </div>
          
          <p className="text-sm text-gray-500">
            CSV files only, max 100MB
          </p>
        </div>
      </div>

      {selectedFile && (
        <div className="mt-4 p-4 bg-green-50 rounded-lg flex items-center space-x-3">
          <FileText className="h-5 w-5 text-green-500" />
          <div className="flex-1">
            <p className="text-sm font-medium text-green-800">
              {selectedFile.name}
            </p>
            <p className="text-sm text-green-600">
              {formatFileSize(selectedFile.size)}
            </p>
          </div>
        </div>
      )}

      {formState.error && (
        <div className="mt-4 p-4 bg-red-50 rounded-lg flex items-center space-x-3">
          <AlertCircle className="h-5 w-5 text-red-500" />
          <p className="text-sm text-red-700">{formState.error}</p>
        </div>
      )}

      {formState.success && (
        <div className="mt-4 p-4 bg-green-50 rounded-lg">
          <p className="text-sm text-green-700">
            File uploaded successfully! Processing has started.
          </p>
        </div>
      )}

      <div className="mt-6 flex justify-end">
        <button
          onClick={handleUpload}
          disabled={!selectedFile || formState.isSubmitting}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
        >
          {formState.isSubmitting ? 'Uploading...' : 'Process File'}
        </button>
      </div>
    </div>
  )
}