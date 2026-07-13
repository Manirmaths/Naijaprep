export default function Spinner({ className = 'w-6 h-6' }: { className?: string }) {
  return (
    <div className="flex items-center justify-center py-10">
      <span className={`${className} rounded-full border-[3px] border-brand-200 border-t-brand-500 animate-spin`} />
    </div>
  );
}
