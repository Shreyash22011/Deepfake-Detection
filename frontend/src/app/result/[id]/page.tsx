import ResultCard from '@/components/ResultCard';
import EvidenceCard from '@/components/EvidenceCard';
import HeatmapViewer from '@/components/HeatmapViewer';
import SuspiciousFrames from '@/components/SuspiciousFrames';
import MetadataCard from '@/components/MetadataCard';
import MediaPreview from '@/components/MediaPreview';
import Link from 'next/link';

export default async function ResultPage({ params }: { params: Promise<{ id: string }> }) {
  // In a real implementation, we would fetch data from the backend here.
  // For the frontend shell, we mock the data.
  const resolvedParams = await params;
  const analysisId = resolvedParams.id;

  // Fetch data from backend
  let apiData = null;
  let errorMsg = null;
  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  try {
    const res = await fetch(`${API_URL}/api/analyses/${analysisId}`, { cache: 'no-store' });
    if (!res.ok) {
      errorMsg = "Failed to fetch analysis result.";
    } else {
      apiData = await res.json();
    }
  } catch (e) {
    errorMsg = "Network error. Is the backend running?";
  }

  // If there's an error, or the result is still processing, show a fallback UI
  if (errorMsg) {
    return <div className="text-red-500 mt-10 text-center">{errorMsg}</div>;
  }

  if (!apiData) {
    return <div className="mt-10 text-center">Loading...</div>;
  }

  if (apiData.status === "processing" || apiData.status === "pending") {
    return (
      <div className="max-w-6xl mx-auto w-full mt-20 text-center space-y-4">
        <h1 className="text-3xl font-bold">Analysis in Progress...</h1>
        <p className="text-gray-400">ID: {analysisId}</p>
        <p className="text-primary animate-pulse">The AI is currently analyzing your media. Please refresh this page in a moment.</p>
      </div>
    );
  }

  if (apiData.status === "error") {
    return (
      <div className="max-w-6xl mx-auto w-full mt-20 text-center space-y-4">
        <h1 className="text-3xl font-bold text-red-500">Analysis Failed</h1>
        <p className="text-gray-400">ID: {analysisId}</p>
        <div className="bg-red-500/10 text-red-400 p-4 rounded-lg inline-block border border-red-500/20">
          {apiData.error_message || "An unknown error occurred during processing."}
        </div>
        <div className="mt-6">
           <Link href="/analyze" className="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary-hover">Try Again</Link>
        </div>
      </div>
    );
  }

  // Success state mappings
  const result = apiData.result || {};
  const mockData = {
    id: analysisId,
    prediction: result.prediction || "uncertain",
    confidence: result.confidence || 0.0,
    model_name: result.model_name || "Unknown",
    media_type: apiData.media_type || "video",
    processing_time_ms: result.processing_time_ms || 0,
    evidence: {
      suspicious_regions: result.evidence?.suspicious_regions || [],
      suspicious_frames: result.evidence?.suspicious_frames || [],
      note: result.evidence?.note || result.evidence?.error || "Analysis completed successfully."
    },
    metadata: {
      filename: apiData.filename || "Unknown"
    }
  };

  return (
    <div className="max-w-6xl mx-auto w-full space-y-8 mt-8 pb-12">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Analysis Result</h1>
          <p className="text-gray-400 mt-1 font-mono text-sm">ID: {mockData.id}</p>
        </div>
        <div className="flex gap-4">
          <button className="px-4 py-2 bg-panel border border-border rounded-lg text-sm font-medium hover:bg-panel/80 transition-colors flex items-center gap-2">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-4 h-4">
              <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
            </svg>
            Generate PDF
          </button>
          <Link href="/analyze" className="px-4 py-2 bg-primary text-white rounded-lg text-sm font-medium hover:bg-primary-hover transition-colors">
            New Analysis
          </Link>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-1 space-y-6">
          <ResultCard 
            prediction={mockData.prediction} 
            confidence={mockData.confidence} 
            modelName={mockData.model_name} 
          />
          <EvidenceCard title="Processing Details">
            <MetadataCard metadata={{
              Time_Taken: `${mockData.processing_time_ms} ms`,
              Media_Type: mockData.media_type,
            }} />
          </EvidenceCard>
          <EvidenceCard title="Extracted Metadata">
            <MetadataCard metadata={mockData.metadata} />
          </EvidenceCard>
        </div>

        <div className="lg:col-span-2 space-y-6">
          <EvidenceCard title="Media Preview">
            <MediaPreview type={mockData.media_type} url="#" />
          </EvidenceCard>
          
          <EvidenceCard title="Forensic Heatmap">
            <HeatmapViewer regions={mockData.evidence.suspicious_regions} />
          </EvidenceCard>

          {mockData.media_type === 'video' && (
            <EvidenceCard title="Flagged Frames">
              <SuspiciousFrames frames={mockData.evidence.suspicious_frames} />
            </EvidenceCard>
          )}

          <EvidenceCard title="Analyst Note">
            <p className="text-gray-300">{mockData.evidence.note}</p>
          </EvidenceCard>
        </div>
      </div>
    </div>
  );
}
