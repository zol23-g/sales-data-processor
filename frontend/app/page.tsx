'use client'

import FileUpload from '@/components/FileUpload'
import JobStatus from '@/components/JobStatus'
import { useState } from 'react'


export default function Home() {
  const [currentJobId, setCurrentJobId] = useState<string | null>(null)

  return (
    <main className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold text-gray-900 mb-4">
              Sales Data Processor
            </h1>
            <p className="text-xl text-gray-600">
              Upload large CSV files to process sales data and get aggregated results
            </p>
          </div>

          <div className="grid gap-8">
            <FileUpload onJobCreated={setCurrentJobId} />
            {currentJobId && <JobStatus jobId={currentJobId} />}
          </div>
        </div>
      </div>
    </main>
  )
}