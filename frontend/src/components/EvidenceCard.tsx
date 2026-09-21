export default function EvidenceCard({ title, children }: { title: string, children: React.ReactNode }) {
  return (
    <div className="bg-panel border border-border rounded-xl overflow-hidden">
      <div className="bg-background/50 px-4 py-3 border-b border-border">
        <h3 className="font-semibold text-sm">{title}</h3>
      </div>
      <div className="p-4">
        {children}
      </div>
    </div>
  );
}
