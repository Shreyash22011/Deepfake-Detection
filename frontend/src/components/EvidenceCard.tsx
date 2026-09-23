export default function EvidenceCard({ title, children }: { title: string, children: React.ReactNode }) {
  return (
    <div className="bg-panel border border-border shadow-sm">
      <div className="px-6 py-4 border-b border-border/50 bg-background/50">
        <h3 className="font-bold text-xs uppercase tracking-widest text-accent">{title}</h3>
      </div>
      <div className="p-6">
        {children}
      </div>
    </div>
  );
}
