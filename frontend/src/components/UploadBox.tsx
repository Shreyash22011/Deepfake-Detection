'use client';

import { useState, useRef } from 'react';

interface UploadBoxProps {
  onFileSelect: (file: File) => void;
  onClear: () => void;
  selectedFile: File | null;
}

export default function UploadBox({ onFileSelect, onClear, selectedFile }: UploadBoxProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const validateFile = (file: File) => {
    const maxSize = 50 * 1024 * 1024; // 50MB

    const type = file.type || '';
    const name = file.name.toLowerCase();
    
    const isImage = type.startsWith('image/') || name.match(/\.(jpg|jpeg|png|webp|gif)$/);
    const isVideo = type.startsWith('video/') || name.match(/\.(mp4|webm|ogg|mov|avi)$/);
    const isAudio = type.startsWith('audio/') || name.match(/\.(mp3|wav|ogg|m4a)$/);

    if (!isImage && !isVideo && !isAudio) {
      setError(`Invalid file type. Please upload an image, video, or audio file.`);
      return false;
    }
    if (file.size > maxSize) {
      setError('File is too large. Max size is 50MB');
      return false;
    }
    setError(null);
    return true;
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0];
      if (validateFile(file)) {
        onFileSelect(file);
      }
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const file = e.target.files[0];
      if (validateFile(file)) {
        onFileSelect(file);
      }
    }
  };

  const handleClear = (e?: React.MouseEvent) => {
    if (e) {
      e.preventDefault();
      e.stopPropagation();
    }
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
    setError(null);
    onClear();
  };

  if (selectedFile) {
    return (
      <div className="bg-panel border border-border p-6 rounded-xl flex items-center justify-between relative z-10">
        <div>
          <p className="font-medium">{selectedFile.name}</p>
          <p className="text-sm text-gray-400">{(selectedFile.size / 1024 / 1024).toFixed(2)} MB</p>
        </div>
        <button 
          type="button"
          onClick={handleClear}
          className="text-danger hover:text-danger/80 text-sm font-medium px-4 py-2"
        >
          Remove
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-2 relative">
      <div 
        className={`relative block border-2 border-dashed rounded-xl p-12 text-center transition-colors ${isDragging ? 'border-primary bg-primary/10' : 'border-border bg-panel hover:bg-panel/80'}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <input 
          id="file-upload"
          type="file" 
          ref={fileInputRef} 
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10" 
          onChange={handleFileChange}
          accept="image/*,video/*,audio/*"
        />
        <div className="space-y-4 pointer-events-none">
          <div className="w-16 h-16 mx-auto bg-background rounded-full flex items-center justify-center border border-border">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-8 h-8 text-primary">
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 16.5V9.75m0 0l3 3m-3-3l-3 3M6.75 19.5a4.5 4.5 0 01-1.41-8.775 5.25 5.25 0 0110.233-2.33 3 3 0 013.758 3.848A3.752 3.752 0 0118 19.5H6.75z" />
            </svg>
          </div>
          <div>
            <p className="text-lg font-medium">Drag & drop your file here</p>
            <p className="text-sm text-gray-400 mt-1">or click to browse</p>
          </div>
          <p className="text-xs text-gray-500">Supports: JPG, PNG, MP4, MP3, WAV (Max 50MB)</p>
        </div>
      </div>
      {error && <p className="text-danger text-sm mt-2">{error}</p>}
    </div>
  );
}
