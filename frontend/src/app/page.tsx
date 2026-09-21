import Link from "next/link";

export default function Home() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[80vh] text-center px-4">
      <div className="max-w-3xl space-y-8">
        <h1 className="text-5xl md:text-6xl font-extrabold tracking-tight">
          AI Media <span className="text-primary">Authenticity</span> Platform
        </h1>
        <p className="text-xl text-gray-400">
          Advanced deepfake detection and forensic classification using multi-modal deep learning techniques. Ensure the integrity of digital media.
        </p>
        
        <div className="flex justify-center gap-4 py-4">
          <div className="bg-panel px-6 py-3 rounded-lg border border-border flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-primary animate-pulse"></span>
            <span className="font-medium text-sm">Image Analysis</span>
          </div>
          <div className="bg-panel px-6 py-3 rounded-lg border border-border flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-accent animate-pulse"></span>
            <span className="font-medium text-sm">Video Forensics</span>
          </div>
          <div className="bg-panel px-6 py-3 rounded-lg border border-border flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-success animate-pulse"></span>
            <span className="font-medium text-sm">Audio Detection</span>
          </div>
        </div>

        <div className="pt-8">
          <Link 
            href="/analyze" 
            className="inline-flex items-center justify-center px-8 py-4 text-lg font-medium text-white bg-primary hover:bg-primary-hover rounded-xl shadow-lg shadow-primary/20 transition-all hover:scale-105"
          >
            Start Analysis
          </Link>
        </div>
      </div>
    </div>
  );
}
