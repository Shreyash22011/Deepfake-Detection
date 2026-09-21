export default function DashboardPage() {
  return (
    <div className="max-w-5xl mx-auto w-full mt-8 space-y-8">
      <div>
        <h1 className="text-3xl font-bold">System Dashboard</h1>
        <p className="text-gray-400 mt-2">Overview of media analysis metrics.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-panel border border-border rounded-xl p-6">
          <p className="text-sm text-gray-400 uppercase tracking-wider">Total Analyses</p>
          <p className="text-4xl font-bold mt-2">1,248</p>
        </div>
        <div className="bg-panel border border-border rounded-xl p-6">
          <p className="text-sm text-gray-400 uppercase tracking-wider">Fakes Detected</p>
          <p className="text-4xl font-bold text-danger mt-2">412</p>
        </div>
        <div className="bg-panel border border-border rounded-xl p-6">
          <p className="text-sm text-gray-400 uppercase tracking-wider">Avg Processing Time</p>
          <p className="text-4xl font-bold text-primary mt-2">1.8s</p>
        </div>
      </div>

      <div className="bg-panel border border-border rounded-xl p-6 h-64 flex items-center justify-center text-gray-500">
        <p>Chart Placeholder: Analysis Trends over Time (Requires Charting Library)</p>
      </div>
    </div>
  );
}
