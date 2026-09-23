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
      void media_type; // used implicitly by backend via file mimetype

      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${API_URL}/api/analyze`, {
        method: 'POST',
        // Do NOT set Content-Type header — browser sets multipart/form-data automatically
        body: formData
      });

      if (!response.ok) {
        throw new Error('Analysis failed');
      }

      const data = await response.json();
      const analysisId = data.id;

      // Save local file Object URL for in-session media preview
      try {
        sessionStorage.setItem(`media_${analysisId}`, URL.createObjectURL(file));
      } catch (e) {
        console.warn("Could not save media to session storage", e);
      }

      router.push(`/result/${analysisId}`);

    } catch (err: unknown) {
      console.error(err);
      setStatus('error');
      setErrorMsg(err instanceof Error ? err.message : 'An error occurred during analysis.');
    }
  };

  return (
    <div className="max-w-[1200px] mx-auto px-6 w-full">
      <div className="max-w-2xl py-12">
        <p className="text-xs font-semibold uppercase tracking-widest text-primary mb-4">
          Media Analysis
        </p>
        <h1 className="text-3xl font-bold text-foreground mb-2">Analyze Media</h1>
        <p className="text-accent text-base mb-10">
          Upload a file to detect potential AI manipulation or synthetic content.
        </p>

        {status === 'idle' || status === 'error' ? (
          <div className="space-y-6">
            <UploadBox
              selectedFile={file}
              onFileSelect={setFile}
              onClear={() => setFile(null)}
            />

            {errorMsg && (
              <div className="flex items-start gap-3 px-4 py-3 bg-danger/8 border border-danger/25 text-danger text-sm">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-4 h-4 flex-shrink-0 mt-0.5">
                  <path fillRule="evenodd" d="M18 10a8 8 0 1 1-16 0 8 8 0 0 1 16 0Zm-8-5a.75.75 0 0 1 .75.75v4.5a.75.75 0 0 1-1.5 0v-4.5A.75.75 0 0 1 10 5Zm0 10a1 1 0 1 0 0-2 1 1 0 0 0 0 2Z" clipRule="evenodd" />
                </svg>
                {errorMsg}
              </div>
            )}

            <div className="flex items-center gap-4">
              <button
                onClick={handleAnalyze}
                disabled={!file}
                className="px-6 py-2.5 bg-primary text-surface text-sm font-semibold rounded-sm disabled:opacity-40 disabled:cursor-not-allowed hover:bg-primary-hover transition-colors"
              >
                Run Analysis
              </button>
              {file && (
                <p className="text-sm text-muted">
                  Ready to analyze <span className="font-medium text-accent">{file.name}</span>
                </p>
              )}
            </div>
          </div>
        ) : (
          <AnalysisStatus status={status} />
        )}
      </div>
    </div>
  );
}
