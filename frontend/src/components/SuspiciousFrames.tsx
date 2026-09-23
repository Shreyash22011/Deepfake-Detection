'use client';

import { useEffect, useState, useRef } from 'react';

interface SuspiciousFramesProps {
  frames: number[];
  analysisId?: string;
  fps?: number;
}

export default function SuspiciousFrames({ frames, analysisId, fps = 24 }: SuspiciousFramesProps) {
  const [objectUrl] = useState<string | null>(() => {
    if (typeof window === 'undefined' || !analysisId) return null;
    return sessionStorage.getItem(`media_${analysisId}`);
  });
  const [thumbnails, setThumbnails] = useState<Record<number, string>>({});
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    if (!objectUrl || !frames || frames.length === 0) return;
    let isMounted = true;
    const video = videoRef.current;
    const canvas = canvasRef.current;
    if (!video || !canvas) return;

    const extractFrames = async () => {
      for (const frame of frames) {
        if (!isMounted) break;
        if (thumbnails[frame]) continue;
        const time = frame / fps;

        await new Promise<void>((resolve) => {
          const onSeeked = () => {
            const ctx = canvas.getContext('2d');
            if (ctx && video.videoWidth > 0 && video.videoHeight > 0) {
              canvas.width = video.videoWidth;
              canvas.height = video.videoHeight;
              ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
              try {
                const dataUrl = canvas.toDataURL('image/jpeg', 0.85);
                setThumbnails(prev => ({ ...prev, [frame]: dataUrl }));
              } catch { /* cross-origin */ }
            }
            video.removeEventListener('seeked', onSeeked);
            resolve();
          };
          video.addEventListener('seeked', onSeeked);
          video.currentTime = time;
        });
      }
    };

    const onLoadedData = () => extractFrames();
    video.addEventListener('loadeddata', onLoadedData);
    return () => {
      isMounted = false;
      video.removeEventListener('loadeddata', onLoadedData);
    };
  }, [objectUrl, frames, fps]);

  if (!frames || frames.length === 0) {
    return (
      <div className="border border-border rounded-sm bg-surface px-5 py-6">
        <p className="text-sm font-medium text-foreground mb-1">No suspicious frames</p>
        <p className="text-xs text-muted">No anomalous frames were identified during analysis.</p>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {/* Hidden video + canvas for thumbnail extraction */}
      {objectUrl && (
        <>
          <video ref={videoRef} src={objectUrl} className="sr-only" crossOrigin="anonymous" preload="auto" />
          <canvas ref={canvasRef} className="sr-only" />
        </>
      )}

      {/* Scrollable evidence strip */}
      <div className="flex gap-3 overflow-x-auto pb-3" style={{ scrollbarWidth: 'thin' }}>
        {frames.map((frame) => {
          const time = (frame / fps).toFixed(2);
          const thumb = thumbnails[frame];

          return (
            <div key={frame} className="flex-shrink-0 w-40">
              {/* Thumbnail */}
              <div className="relative w-40 bg-surface-2 border border-border rounded-sm overflow-hidden" style={{ aspectRatio: '16/9' }}>
                {thumb ? (
                  <img src={thumb} alt={`Frame ${frame}`} className="w-full h-full object-cover" />
                ) : (
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="w-4 h-4 rounded-full border-2 border-border border-t-transparent animate-spin" />
                  </div>
                )}
                {/* Danger indicator */}
                <div className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-danger" />
              </div>
              {/* Caption */}
              <div className="mt-2 px-0.5">
                <p className="text-xs font-mono text-foreground">Frame {frame}</p>
                <p className="text-[10px] text-muted font-mono">{time}s</p>
              </div>
            </div>
          );
        })}
      </div>
      <p className="text-[10px] text-muted">{frames.length} flagged frame{frames.length !== 1 ? 's' : ''}</p>
    </div>
  );
}
