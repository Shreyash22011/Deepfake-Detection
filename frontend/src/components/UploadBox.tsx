'use client';

import { useState, useRef } from 'react';

interface UploadBoxProps {
  onFileSelect: (file: File) => void;
  onClear: () => void;
  selectedFile: File | null;
}

const ACCEPTED_EXTENSIONS = ['jpg', 'jpeg', 'png', 'webp', 'gif', 'mp4', 'webm', 'ogg', 'mov', 'avi', 'mp3', 'wav', 'm4a'];
const MAX_SIZE_MB = 50;

function FileIcon() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5} className="w-8 h-8 text-muted">
      <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5m-13.5-9L12 3m0 0 4.5 4.5M12 3v13.5" />
    </svg>
  );
}

function formatBytes(bytes: number): string {
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`;
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}

export default function UploadBox({ onFileSelect, onClear, selectedFile }: UploadBoxProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const validate = (file: File): boolean => {
    const ext = file.name.split('.').pop()?.toLowerCase() || '';
    const type = file.type || '';
    const isImage = type.startsWith('image/') || ['jpg', 'jpeg', 'png', 'webp', 'gif'].includes(ext);
    const isVideo = type.startsWith('video/') || ['mp4', 'webm', 'ogg', 'mov', 'avi'].includes(ext);
    const isAudio = type.startsWith('audio/') || ['mp3', 'wav', 'm4a'].includes(ext);

    if (!isImage && !isVideo && !isAudio) {
      setError(`Unsupported file type. Accepted: ${ACCEPTED_EXTENSIONS.join(', ')}`);
      return false;
    }
    if (file.size > MAX_SIZE_MB * 1024 * 1024) {
      setError(`File too large. Maximum size is ${MAX_SIZE_MB} MB.`);
      return false;
    }
    setError(null);
    return true;
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files?.[0];
    if (file && validate(file)) onFileSelect(file);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && validate(file)) onFileSelect(file);
  };

  const handleClear = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (fileInputRef.current) fileInputRef.current.value = '';
    setError(null);
    onClear();
  };

  if (selectedFile) {
    return (
      <div className="border border-border bg-surface rounded-lg p-5 flex items-center gap-4 shadow-sm">
        <div className="w-10 h-10 rounded-sm bg-surface-2 flex items-center justify-center flex-shrink-0">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-5 h-5 text-primary">
            <path d="M3 3.5A1.5 1.5 0 0 1 4.5 2h6.879a1.5 1.5 0 0 1 1.06.44l4.122 4.12A1.5 1.5 0 0 1 17 7.622V16.5a1.5 1.5 0 0 1-1.5 1.5h-11A1.5 1.5 0 0 1 3 16.5v-13Z" />
          </svg>
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-foreground truncate">{selectedFile.name}</p>
          <p className="text-xs text-muted mt-0.5">{formatBytes(selectedFile.size)}</p>
        </div>
        <button
          type="button"
          onClick={handleClear}
          className="text-xs text-muted hover:text-danger transition-colors font-medium"
        >
          Remove
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      <div
        className={`relative border-2 border-dashed rounded-lg transition-colors ${
          isDragging
            ? 'border-primary bg-primary/5'
            : 'border-border hover:border-accent bg-surface'
        }`}
        onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
        onDragLeave={(e) => { e.preventDefault(); setIsDragging(false); }}
        onDrop={handleDrop}
      >
        <input
          id="file-upload"
          type="file"
          ref={fileInputRef}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
          onChange={handleChange}
          accept="image/*,video/*,audio/*"
        />
        <div className="flex flex-col items-center justify-center py-16 px-6 text-center pointer-events-none select-none">
          <div className="w-12 h-12 rounded-xl bg-primary/8 flex items-center justify-center"><FileIcon /></div>
          <p className="mt-5 text-base font-semibold text-foreground">
            Drop your file here, or{' '}
            <span className="text-primary underline underline-offset-4">browse</span>
          </p>
          <p className="mt-2 text-xs text-muted">
            Images, video, and audio · up to {MAX_SIZE_MB} MB
          </p>
        </div>
      </div>
      {error && (
        <p className="text-xs text-danger font-medium">{error}</p>
      )}
    </div>
  );
}
