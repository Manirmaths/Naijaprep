export default function ProgressBar({ value, tone = 'brand' }: { value: number; tone?: 'brand' | 'success' | 'warning' | 'danger' }) {
  const pct = Math.max(0, Math.min(100, value));
  const toneClass = {
    brand: 'bg-brand-500',
    success: 'bg-success-500',
    warning: 'bg-warning-500',
    danger: 'bg-danger-500',
  }[tone];
  return (
    <div className="w-full h-2 rounded-full bg-ink-100 overflow-hidden">
      <div className={`h-full rounded-full ${toneClass} transition-all duration-300 ease-out`} style={{ width: `${pct}%` }} />
    </div>
  );
}
