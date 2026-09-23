'use client';

import { useState } from 'react';

interface MediaPreviewProps {
  type: string;
  analysisId?: string;
}

export default function MediaPreview({ type, analysisId }: MediaPreviewProps) {
  const [objectUrl] = useState<string | null>(() => {
    if (typeof window === 'undefined' || !analysisId) return null;
    return sessionStorage.getItem(`media_${analysisId}`);
  });

  if (!objectUrl) {
    return (
      <div className="border border-border rounded-lg bg-surface flex items-center justify-center py-12 px-6 text-center">
        <div>
          <p className="text-sm font-medium text-foreground mb-1">Preview not available</p>
          <p className="text-xs text-muted max-w-xs">
            The original file is only available within the browser session where it was uploaded.
          </p>
        </div>
      </div>
    );
  }

  if (type === 'video') {
    return (
      <div className="bg-foreground/5 border border-border rounded-lg overflow-hidden">
        <video
          src={objectUrl}
          controls
          className="w-full h-auto max-h-[420px] block"
          style={{ aspectRatio: '16 / 9', objectFit: 'contain', backgroundColor: '#111' }}
        />
      </div>
    );
  }

  if (type === 'audio') {
    return (
      <div className="border border-border rounded-lg bg-surface p-6">
        <audio src={objectUrl} controls className="w-full" />
      </div>
    );
  }

  return (
    <div className="border border-border rounded-lg overflow-hidden bg-surface-2">
      <img
        src={objectUrl}
        alt="Uploaded media"
        className="w-full h-auto max-h-[420px] object-contain block"
      />
    </div>
  );
}
