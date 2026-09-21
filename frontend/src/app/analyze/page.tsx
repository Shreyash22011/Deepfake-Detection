'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import UploadBox from '@/components/UploadBox';
import AnalysisStatus from '@/components/AnalysisStatus';

export default function AnalyzePage() {
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<'idle' | 'uploading' | 'processing' | 'error'>('idle');
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const router = useRouter();

  const handleAnalyze = async () => {
    if (!file) return;
    
    setStatus('processing');
    setErrorMsg(null);

    try {
      // Determine media type
      let media_type = 'image';
      const type = file.type || '';
      const name = file.name.toLowerCase();
      
      if (type.startsWith('video/') || name.match(/\.(mp4|webm|ogg|mov|avi)$/)) media_type = 'video';
      else if (type.startsWith('audio/') || name.match(/\.(mp3|wav|ogg|m4a)$/)) media_type = 'audio';

      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${API_URL}/api/analyze`, {
        method: 'POST',
        // Do NOT set Content-Type header when sending FormData
        // The browser will automatically set it to multipart/form-data with the correct boundary
        body: formData
      });

      if (!response.ok) {
        throw new Error('Analysis failed');
      }

      // The backend now returns an AnalysisRecord containing the real ID
      const data = await response.json();
      const analysisId = data.id;
      
      router.push(`/result/${analysisId}`);
      
    } catch (err: unknown) {
      console.error(err);
      setStatus('error');
      setErrorMsg(err instanceof Error ? err.message : 'An error occurred during analysis.');
    }
  };

  return (
    <div className="max-w-2xl mx-auto w-full space-y-8 mt-12">
      <div>
        <h1 className="text-3xl font-bold">Analyze Media</h1>
        <p className="text-gray-400 mt-2">Upload an image, video, or audio file to detect AI manipulation.</p>
      </div>

      {status === 'idle' || status === 'error' ? (
        <div className="space-y-6">
          <UploadBox 
            selectedFile={file}
            onFileSelect={setFile}
            onClear={() => setFile(null)}
          />
          
          {errorMsg && (
            <div className="bg-danger/10 border border-danger/20 text-danger px-4 py-3 rounded-lg">
              {errorMsg}
            </div>
          )}

          <button
            onClick={handleAnalyze}
            disabled={!file}
            className="w-full py-4 bg-primary text-white font-medium rounded-xl disabled:opacity-50 disabled:cursor-not-allowed hover:bg-primary-hover transition-colors"
          >
            Run Analysis
          </button>
        </div>
      ) : (
        <AnalysisStatus status={status} />
      )}
    </div>
  );
}
